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

templates = Jinja2Templates(directory='templates', autoescape=False)

async def home(request):
    """
    Endpoint for home page
    """
    home_data = get_home_data(state='file')
    data = {"request": request, **home_data, }
    return templates.TemplateResponse('index.html', data)

async def query(request):
    """
    Endpoint for displaying query results
    """
    params = request.path_params
    try:
        query = get_query_data(
            state='file',
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
        data = {"request": request, **query, }
        return templates.TemplateResponse('query.html', data)

routes = [
    Route("/", endpoint=home),
    Route('/query/{db:str}/{file:str}', endpoint=query),
    Mount('/static', app=StaticFiles(directory='static'), name="static"),
]

app = Starlette(debug=True, routes=routes)
