"""
Main app file
"""
import os
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

import query
import repo

VERSION = "0.2"
APP_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(APP_DIR, "static")
TEMPLATE_DIR = os.path.join(APP_DIR, "templates")
TEMPLATES = Jinja2Templates(directory=TEMPLATE_DIR, autoescape=False)

# Error types
# 404 RuntimeError file not accessible
# 500 NameError variables not set
# 500 ValueError bad query

async def home_route(request):
    """
    Endpoint for home page
    """
    try:
        state = request.path_params.get("state")
        data = {
            "request": request,
            "version": VERSION,
            "state": state,
            "readme": repo.get_readme(state),
            "databases": repo.list_sources(state),
            "commits": repo.list_commits(),
        }
        return TEMPLATES.TemplateResponse(name='index.html', context=data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

async def home_default_route(request):
    """
    Default endpoint: redirect to HEAD state
    """
    return RedirectResponse(url="/home/HEAD/")

async def db_route(request):
    """
    Endpoint for listing all db info: queries and tables
    """
    try:
        db = request.path_params.get("db")
        databases = repo.list_sources(request.path_params.get("state"))
        if db not in databases:
            raise RuntimeError(f"db {db} not present in repo")
        queries = databases[db]
        tables = query.list_tables(db)
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        raise HTTPException(status_code=status_code, detail=str(e))
    else:
        data = {
            "request": request,
            "version": VERSION,
            "queries": queries,
            "tables": tables,
            **request.path_params,
        }
        return TEMPLATES.TemplateResponse(name='db.html', context=data)

async def query_route(request):
    """
    Endpoint for editable empty query
    """
    try:
        query_str = request.query_params.get('query')
        db = request.path_params.get("db")
        if db not in repo.list_sources("HEAD").keys():
            raise RuntimeError(f"db {db} not present in repo")
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        data = {
            "request": request,
            "version": VERSION,
            "state": None,
            "query": query_str or "",
            "editable": True,
            "db": db, 
        }
        return TEMPLATES.TemplateResponse(name='query.html', context=data)

async def saved_query_route(request):
    """
    Endpoint for displaying query
    """
    try:
        query = repo.get_query(**request.path_params)
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        data = {
            "request": request,
            "version": VERSION,
            "query": query,
            "editable": False,
            **request.path_params,
        }
        return TEMPLATES.TemplateResponse(name='query.html', context=data)

async def execute_route(request):
    """
    Endpoint for getting query result
    Used by htmx
    """
    htmx_req = bool(request.headers.get("HX-Request"))
    try:
        form = await request.form()
        table = query.execute(db=request.path_params.get("db"), query=form["query"])
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        if htmx_req:
            return _htmx_error(str(e), status_code)
        else:
            raise HTTPException(status_code=status_code, detail=str(e))
    else:
        return HTMLResponse(content=table, status_code=200)

def _htmx_error(message, code):
    """
    Creates successful reponse for htmx (with error msg)
    even if endpoint actually failed
    """
    error_msg = f"""
    <article>
        <header><h3>{code} Error</h3></header>
        {message}
    </article>
    """
    return HTMLResponse(content=error_msg, status_code=200)

async def server_error(request, exc):
    data = {
        "request": request,
        "version": VERSION,
        "code": exc.status_code,
        "message": exc.detail
    }
    return TEMPLATES.TemplateResponse(name='error.html', context=data, status_code=exc.status_code)

routes = [
    Mount('/static', app=StaticFiles(directory=STATIC_DIR), name="static"),
    Route("/", endpoint=home_default_route, name="home_default_route"),
    Route("/home/{state:str}", endpoint=home_route, name="home_route"),
    Route("/db/{db:str}/{state:str}", endpoint=db_route, name="db_route"),
    Route('/query/{db:str}', endpoint=query_route, name="query_route"),
    Route('/query/{db:str}/{file:str}/{state:str}', endpoint=saved_query_route, name="saved_query_route"),
    Route('/execute/{db:str}', endpoint=execute_route, methods=("POST", ), name="execute_route"),
]

exception_handlers = {
    HTTPException: server_error,
}

app = Starlette(
    debug=True,
    routes=routes,
    exception_handlers=exception_handlers
)
