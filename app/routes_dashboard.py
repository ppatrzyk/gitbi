"""
Routes for displaying and saving dashboards
"""

import config
import utils
from starlette.exceptions import HTTPException


async def dashboard_route(request):
    """
    Show dashboard
    """
    try:
        dashboard_conf = config.get_dashboard(**request.path_params)
        dashboard_conf = tuple(
            el
            + [
                utils.random_id(),
            ]
            for el in dashboard_conf
        )
        data = {
            **utils.common_context_args(request),
            **request.path_params,
            "dashboard_conf": dashboard_conf,
        }
        response = utils.TEMPLATES.TemplateResponse(
            request=request, name="dashboard.html.jinja", context=data
        )
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        raise HTTPException(status_code=status_code, detail=str(e))
    else:
        return response
