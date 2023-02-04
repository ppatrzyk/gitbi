"""
Main app file
"""
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
import auth
import routes_execute, routes_listing, routes_query, routes_utils

# Error types
# 404 RuntimeError file not accessible
# 500 NameError variables not set
# 500 ValueError bad query

async def server_error(request, exc):
    data = {
        "request": request,
        "version": routes_utils.VERSION,
        "code": exc.status_code,
        "message": exc.detail
    }
    return routes_utils.TEMPLATES.TemplateResponse(name='error.html', context=data, status_code=exc.status_code)

routes = [
    # routes execute
    Route('/email/alert/{db:str}/{file:str}/{state:str}', endpoint=routes_execute.email_alert_route, name="email_alert_route"),
    Route('/email/report/{db:str}/{file:str}/{state:str}', endpoint=routes_execute.email_report_route, name="email_report_route"),
    Route('/execute/{db:str}', endpoint=routes_execute.execute_route, methods=("POST", ), name="execute_route"),
    Route('/report/{db:str}/{file:str}/{state:str}', endpoint=routes_execute.report_route, name="report_route"),
    # routes_listing
    Route("/", endpoint=routes_listing.home_default_route, name="home_default_route"),
    Route("/db/{db:str}/{state:str}", endpoint=routes_listing.db_route, name="db_route"),
    Route("/home/{state:str}", endpoint=routes_listing.home_route, name="home_route"),
    # routes query
    Route('/query/{db:str}', endpoint=routes_query.query_route, name="query_route"),
    Route('/query/{db:str}/{file:str}/{state:str}', endpoint=routes_query.saved_query_route, name="saved_query_route"),
    Route('/delete/{db:str}/{file:str}', endpoint=routes_query.delete_route, name="delete_route"),
    Route('/save/{db:str}', endpoint=routes_query.save_route, methods=("POST", ), name="save_route"),
    # static
    Mount('/static', app=StaticFiles(directory=routes_utils.STATIC_DIR), name="static"),
]

exception_handlers = {
    HTTPException: server_error,
}

middleware = []
middleware.extend(auth.AUTH)

app = Starlette(
    debug=True,
    routes=routes,
    exception_handlers=exception_handlers,
    middleware=middleware
)
