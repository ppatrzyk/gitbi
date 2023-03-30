"""
Routes for displaying and saving dashboards
"""
from starlette.exceptions import HTTPException
from starlette.responses import PlainTextResponse
import repo
import utils

async def dashboard_route(request):
    """
    Show dashboard
    """
    try:
        dashboard_conf = repo.get_dashboard(**request.path_params)
        dashboard_conf = tuple(el + [utils.random_id(), ] for el in dashboard_conf)
        data = {
            **utils.common_context_args(request),
            **request.path_params,
            "dashboard_conf": dashboard_conf,
        }
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        raise HTTPException(status_code=status_code, detail=str(e))
    else:
        return utils.TEMPLATES.TemplateResponse(name='dashboard.html', context=data)

async def delete_route(request):
    """
    Delete query from repository
    """
    try:
        user = utils.common_context_args(request).get("user")
        repo.delete_dashboard(user=user, **request.path_params)
        redirect_url = request.app.url_path_for("home_route", state="HEAD")
        headers = {"HX-Redirect": redirect_url}
        response = PlainTextResponse(content="OK", headers=headers, status_code=200)
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        data = {"request": request, "code": status_code, "message": str(e)}
        return utils.TEMPLATES.TemplateResponse(name='partial_error.html', context=data)
    else:
        return response

async def save_route(request):
    """
    Save query to repository
    """
    try:
        form = await request.form()
        data = utils.parse_dashboard_data(request, form)
        print(data)
        repo.save_dashboard(**request.path_params, **data)
        redirect_url = request.app.url_path_for(
            "dashboard_route",
            file=data['file'],
            state="HEAD"
        )
        headers = {"HX-Redirect": redirect_url}
        response = PlainTextResponse(content="OK", headers=headers, status_code=200)
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        data = {"request": request, "code": status_code, "message": str(e)}
        return utils.TEMPLATES.TemplateResponse(name='partial_error.html', context=data)
    else:
        return response
