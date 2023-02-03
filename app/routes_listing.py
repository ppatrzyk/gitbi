"""
Routes for listing info
"""
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse
import query
import repo
import routes_utils

async def home_route(request):
    """
    Endpoint for home page
    """
    try:
        state = request.path_params.get("state")
        data = {
            **routes_utils.common_context_args(request),
            "state": state,
            "readme": repo.get_readme(state),
            "databases": repo.list_sources(state),
            "commits": repo.list_commits(),
        }
        return routes_utils.TEMPLATES.TemplateResponse(name='index.html', context=data)
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
            **routes_utils.common_context_args(request),
            "queries": queries,
            "tables": tables,
            **request.path_params,
        }
        return routes_utils.TEMPLATES.TemplateResponse(name='db.html', context=data)
