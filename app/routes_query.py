"""
Routes for displaying and saving queries
"""

import config
import utils
from starlette.exceptions import HTTPException


async def query_route(request):
    """
    Endpoint for empty query
    """
    try:
        db = request.path_params.get("db")
        if db not in config.list_sources():
            raise RuntimeError(f"db {db} not present in repo")
        request.state.query_data = {
            "query": request.query_params.get("query") or "",
            "viz": "null",
            "file": "__empty__",
            **request.path_params,  # db
        }
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        return await _query(request)


async def saved_query_route(request):
    """
    Endpoint for saved query
    """
    try:
        query_str, _lang = config.get_query(**request.path_params)
        viz_str = config.get_query_viz(**request.path_params)
        request.state.query_data = {
            "query": query_str,
            "viz": viz_str,
            **request.path_params,  # db, file
        }
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        return await _query(request)


async def _query(request):
    """
    Common logic for query endpoint
    Called by:
    - query
    - saved query
    """
    data = {
        **utils.common_context_args(request),
        **request.state.query_data,
        "echart_id": f"echart-{utils.random_id()}",
    }
    return utils.TEMPLATES.TemplateResponse(
        request=request, name="query.html", context=data
    )
