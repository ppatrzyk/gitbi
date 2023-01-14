"""
Main app file
"""
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from home import get_home_data
from query import get_query_data

VERSION = "0.1"
templates = Jinja2Templates(directory='templates', autoescape=False)

async def home(request):
    """
    Endpoint for home page
    """
    home_data = get_home_data(state='HEAD')
    data = {"request": request, "version": VERSION, **home_data, }
    return templates.TemplateResponse('index.html', data)

async def query(request):
    """
    Endpoint for displaying query results
    """
    params = request.path_params
    try:
        query = get_query_data(
            state='HEAD',
            db=params.get('db'),
            file=params.get('file')
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NameError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        data = {"request": request, "version": VERSION, **query, }
        return templates.TemplateResponse('query.html', data)

async def server_error(request, exc):
    data = {
        "request": request,
        "code": exc.status_code,
        "message": exc.detail
    }
    return templates.TemplateResponse('error.html', data)

routes = [
    Route("/", endpoint=home, name="home"),
    Route('/query/{db:str}/{file:str}', endpoint=query, name="query"),
    Mount('/static', app=StaticFiles(directory='static'), name="static"),
]

exception_handlers = {
    HTTPException: server_error,
}

app = Starlette(debug=True, routes=routes, exception_handlers=exception_handlers)
