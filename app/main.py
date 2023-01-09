from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from home import get_home
from query import get_query

async def home(request):
    home_data = get_home()
    return JSONResponse(home_data)

async def query(request):
    query = get_query(**request.path_params)
    return JSONResponse({"query": query})

routes = [
    Route("/", endpoint=home),
    Route('/query/{db:str}/{file:str}', endpoint=query),
]

app = Starlette(debug=True, routes=routes)
