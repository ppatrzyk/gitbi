from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from home import get_home

async def home(request):
    home_data = get_home()
    return JSONResponse(home_data)

routes = [
    Route("/", endpoint=home)
]

app = Starlette(debug=True, routes=routes)
