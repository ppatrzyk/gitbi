"""
Main app file
"""
import json
import os
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

import query
import repo
import scheduler

VERSION = "0.3"
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
    Endpoint for empty query
    """
    try:
        db = request.path_params.get("db")
        if db not in repo.list_sources("HEAD").keys():
            raise RuntimeError(f"db {db} not present in repo")
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        request.state.query_data = {
            "query": request.query_params.get('query') or "",
            "vega": request.query_params.get('vega') or "",
            "state": None,
            "file": "",
            **request.path_params, # db
        }
        return await _query_route(request)

async def saved_query_route(request):
    """
    Endpoint for saved query
    """
    try:
        query, vega = repo.get_query(**request.path_params)
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        request.state.query_data = {
            "query": query,
            "vega": vega,
            **request.path_params, # db, file, state
        }
        return await _query_route(request)

async def _query_route(request):
    """
    Common logic for query endpoint
    """
    data = {
        "request": request,
        "version": VERSION,
        **request.state.query_data,
    }
    return TEMPLATES.TemplateResponse(name='query.html', context=data)

async def execute_route(request):
    """
    Endpoint for getting query result
    Used by htmx
    """
    try:
        form = await request.form()
        data = json.loads(form["data"])
        table, vega_viz = query.execute(
            db=request.path_params.get("db"),
            query=data.get("query"),
            vega=data.get("vega")
        )
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        return _htmx_error(str(e), status_code)
    else:
        data = {
            "request": request,
            "table": table,
            "vega": vega_viz,
        }
        return TEMPLATES.TemplateResponse(name='result.html', context=data)

async def save_route(request):
    """
    Save query to repository
    """
    try:
        form = await request.form()
        data = json.loads(form["data"])
        data['file'] = data['file'].strip()
        repo.save(**request.path_params, **data)
        redirect_url = request.url_for(
            "saved_query_route",
            db=request.path_params['db'],
            file=data['file'],
            state="HEAD"
        )
        headers = {"HX-Redirect": redirect_url}
        response = HTMLResponse(content="<p>OK</p>", headers=headers, status_code=200)
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        return _htmx_error(str(e), status_code)
    else:
        return response

def _htmx_error(message, code):
    """
    Creates successful reponse for htmx (with error msg)
    even if endpoint actually failed
    """
    error_msg = f"<h3>Error {code}</h3><p>{message}</p>"
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
    Route('/save/{db:str}', endpoint=save_route, methods=("POST", ), name="save_route"),
]

exception_handlers = {
    HTTPException: server_error,
}

if scheduler.scheduler_middleware is None:
    middleware = []
else:
    middleware = [scheduler.scheduler_middleware, ]

app = Starlette(
    debug=True,
    exception_handlers=exception_handlers,
    middleware=middleware,
    routes=routes
)
