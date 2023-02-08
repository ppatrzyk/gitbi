"""
Routes for displaying and saving queries
"""
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse, PlainTextResponse, RedirectResponse
import json
import repo
import routes_utils

async def delete_route(request):
    """
    Delete query from repository
    """
    try:
        user = routes_utils.common_context_args(request).get("user")
        repo.delete(user=user, **request.path_params)
        redirect_url = request.app.url_path_for("home_route", state="HEAD")
        headers = {"HX-Redirect": redirect_url}
        response = PlainTextResponse(content="OK", headers=headers, status_code=200)
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        return routes_utils.partial_html_error(str(e), status_code)
    else:
        return response

async def save_route(request):
    """
    Save query to repository
    """
    try:
        form = await request.form()
        data = json.loads(form["data"])
        data["file"] = data["file"].strip()
        assert data["query"], "No query in POST data"
        if "vega" not in data.keys():
            data["vega"] = None
        data["user"] = routes_utils.common_context_args(request).get("user")
        repo.save(**request.path_params, **data)
        redirect_url = request.app.url_path_for(
            "saved_query_route",
            db=request.path_params['db'],
            file=data['file'],
            state="HEAD"
        )
        headers = {"HX-Redirect": redirect_url}
        response = PlainTextResponse(content="OK", headers=headers, status_code=200)
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        return routes_utils.partial_html_error(str(e), status_code)
    else:
        return response

async def query_route(request):
    """
    Endpoint for empty query
    """
    try:
        db = request.path_params.get("db")
        if db not in repo.list_sources("HEAD").keys():
            raise RuntimeError(f"db {db} not present in repo")
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        request.state.query_data = {
            "query": request.query_params.get('query') or "",
            "vega": request.query_params.get('vega') or "",
            "file": "",
            "report_url": None,
            **request.path_params, # db
        }
        return await _query(request)

async def saved_query_route(request):
    """
    Endpoint for saved query
    """
    try:
        query_str, vega_str = repo.get_query(**request.path_params)
        report_url = request.url_for("report_route", **request.path_params)
        email_alert_url = request.url_for("email_alert_route", **request.path_params)
        email_report_url = request.url_for("email_report_route", **request.path_params)
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        request.state.query_data = {
            "query": query_str,
            "vega": vega_str,
            "report_url": report_url,
            "email_alert_url": email_alert_url,
            "email_report_url": email_report_url,
            **request.path_params, # db, file, state
        }
        return await _query(request)

async def _query(request):
    """
    Common logic for query endpoint
    Called by:
    - query
    - saved query
    """
    data = {
        **routes_utils.common_context_args(request),
        **request.state.query_data,
    }
    return routes_utils.TEMPLATES.TemplateResponse(name='query.html', context=data)
