"""
Routes for listing info
"""
from starlette.exceptions import HTTPException
import query
import config
import utils

async def home_route(request):
    """
    Endpoint for home page
    """
    try:
        data = {
            **utils.common_context_args(request),
            "readme": config.get_readme(),
        }
        response = utils.TEMPLATES.TemplateResponse(request=request, name='index.html', context=data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        return response

async def resources_route(request):
    """
    Endpoint for resources menu
    """
    try:
        data = {
            **utils.common_context_args(request),
            "databases": config.list_sources(),
            "dashboards": config.list_dashboards(),
        }
        response = utils.TEMPLATES.TemplateResponse(request=request, name='partial_resources.html', context=data)
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
        response = utils.TEMPLATES.TemplateResponse(request=request, name='db_details.html', context=data)
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        raise HTTPException(status_code=status_code, detail=str(e))
    else:
        return response
