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
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        return routes_utils.TEMPLATES.TemplateResponse(name='index.html', context=data)

async def home_default_route(request):
    """
    Default endpoint: redirect to HEAD state
    """
    return RedirectResponse(url="/home/HEAD/")

async def tables_route(request):
    """
    Endpoint for getting table info
    User by htmx
    """
    try:
        db = request.path_params.get("db")
        tables = query.list_tables(db)
        data_types = query.list_table_data_types(db, tables)
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        return routes_utils.partial_html_error(str(e), status_code)
    else:
        data = {
            **routes_utils.common_context_args(request),
            "tables": tables,
            "data_types": data_types,
            **request.path_params,
        }
        return routes_utils.TEMPLATES.TemplateResponse(name='partial_tables.html', context=data)

async def commits_route(request):
    """
    Endpoint for getting commits list
    """
    try:
        data = {
            **routes_utils.common_context_args(request),
            "commits": repo.list_commits(),
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        return routes_utils.TEMPLATES.TemplateResponse(name='partial_commits.html', context=data)
