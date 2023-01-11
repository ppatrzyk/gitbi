from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from home import get_home
from query import get_query

templates = Jinja2Templates(directory='templates')

async def home(request):
    print(__file__)
    home_data = get_home(state='file')
    data = {"request": request, **home_data, }
    return templates.TemplateResponse('index.html', data)

async def query(request):
    params = request.path_params
    query = get_query(
        state='file',
        db=params.get('db'),
        file=params.get('file')
    )
    data = {"request": request, **query, }
    return templates.TemplateResponse('query.html', data)

routes = [
    Route("/", endpoint=home),
    Route('/query/{db:str}/{file:str}', endpoint=query),
    Mount('/static', app=StaticFiles(directory='static'), name="static"),
]

app = Starlette(debug=True, routes=routes)
