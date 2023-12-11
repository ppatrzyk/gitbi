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
        # since readme can be empty, need to check for state validity
        commits_headers, commits = repo.list_commits()
        commit_hashes = ("HEAD", ) + tuple(entry[0] for entry in commits)
        assert state in commit_hashes, f"Unknown state: {state}"
        commits_table = utils.format_htmltable("commits-table", commits_headers, commits, False)
        data = {
            **utils.common_context_args(request),
            "readme": repo.get_readme(state),
            "commits_table": commits_table,
        }
        response = utils.TEMPLATES.TemplateResponse(name='index.html', context=data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        return response

async def home_default_route(request):
    """
    Default endpoint: redirect to HEAD state
    """
    return RedirectResponse(url="/home/HEAD/")

async def resources_route(request):
    """
    Endpoint for resources menu
    """
    try:
        state = request.path_params.get("state")
        data = {
            **utils.common_context_args(request),
            "databases": repo.list_sources(state),
            "dashboards": repo.list_dashboards(state),
        }
        response = utils.TEMPLATES.TemplateResponse(name='partial_resources.html', context=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return response

async def db_details_route(request):
    """
    Endpoint for getting database docs
    """
    try:
        db = request.path_params.get("db")
        tables = query.list_tables(db)
        data_docs = query.list_table_data_types(db, tables)
        data = {
            **utils.common_context_args(request),
            "data_docs": data_docs,
            "tables": tables,
            **request.path_params,
        }
        response = utils.TEMPLATES.TemplateResponse(name='db_details.html', context=data)
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        raise HTTPException(status_code=status_code, detail=str(e))
    else:
        return response
