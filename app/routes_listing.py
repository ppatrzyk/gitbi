"""
Routes for listing info
"""
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse
import query
import repo
import utils

async def home_route(request):
    """
    Endpoint for home page
    """
    try:
        state = request.path_params.get("state")
        data = {
            **utils.common_context_args(request),
            "state": state,
            "readme": repo.get_readme(state),
            "databases": repo.list_sources(state),
            "dashboards": repo.list_dashboards(state),
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        return utils.TEMPLATES.TemplateResponse(name='index.html', context=data)

async def home_default_route(request):
    """
    Default endpoint: redirect to HEAD state
    """
    return RedirectResponse(url="/home/HEAD/")

async def db_details_route(request):
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
        data = {"request": request, "code": status_code, "message": str(e)}
        return utils.TEMPLATES.TemplateResponse(name='partial_error.html', context=data)
    else:
        data = {
            **utils.common_context_args(request),
            "tables": tables,
            "data_types": data_types,
            "tables_toc": (len(tables) > 1),
            **request.path_params,
        }
        return utils.TEMPLATES.TemplateResponse(name='partial_db_details.html', context=data)

async def commits_route(request):
    """
    Endpoint for getting commits list
    """
    try:
        headers, commits = repo.list_commits()
        table = utils.format_table("commits-table", utils.random_id(), headers, commits, False)
        data = {
            **utils.common_context_args(request),
            "commits_table": table,
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        return utils.TEMPLATES.TemplateResponse(name='partial_commits.html', context=data)
