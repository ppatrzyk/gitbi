"""
Routes for executing queries
"""
from starlette.exceptions import HTTPException
from starlette.responses import PlainTextResponse
from datetime import datetime
import json
import mailer
import query
import repo
import routes_utils

async def execute_route(request):
    """
    Endpoint for getting query result
    Executes query POSTed from app, used by htmx
    """
    try:
        form = await request.form()
        data = json.loads(form["data"])
        table, vega_viz, duration_ms, no_rows = query.execute(
            db=request.path_params.get("db"),
            query=data.get("query"),
            vega=data.get("vega")
        )
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        return routes_utils.partial_html_error(str(e), status_code)
    else:
        data = {
            "request": request,
            "table": table,
            "vega": vega_viz,
            "time": _get_time(),
            "no_rows": no_rows,
            "duration": duration_ms,
        }
        headers = {"Gitbi-Row-Count": str(no_rows)}
        return routes_utils.TEMPLATES.TemplateResponse(name='result.html', headers=headers, context=data)

async def report_route(request):
    """
    Endpoint for running reports
    This just returns html with report
    """
    report, _no_rows =  await _execute_from_saved_query(request)
    return report

async def email_alert_route(request):
    """
    Endpoint for alerts, sends email only if there are results for a query
    """
    to = request.query_params.get('to')
    report, no_rows =  await _execute_from_saved_query(request)
    if no_rows:
        response = await _mailer_response(report, no_rows, to)
    else:
        response = PlainTextResponse(content=None, status_code=204)
    return response

async def email_report_route(request):
    """
    Endpoint for reports, sends report via email
    """
    to = request.query_params.get('to')
    report, no_rows =  await _execute_from_saved_query(request)
    return await _mailer_response(report, no_rows, to)

async def _mailer_response(report, no_rows, to):
    """
    Wrapper for sending email
    """
    try:
        _res = mailer.send(report, to)
    except Exception as e:
        error = f"Error: {str(e)}"
        response = PlainTextResponse(content=error, status_code=500)
    else:
        headers = {"Gitbi-Row-Count": str(no_rows)}
        response = PlainTextResponse(content="OK", status_code=200)
    return response

async def _execute_from_saved_query(request):
    """
    Execute saved query, common logic for reports and alerts
    Called by:
    - report
    - email alert/report
    """
    try:
        query_url = request.url_for("saved_query_route", **request.path_params)
        query_str, vega_str = repo.get_query(**request.path_params)
        table, _vega_viz, duration_ms, no_rows = query.execute(
            db=request.path_params.get("db"),
            query=query_str,
            vega=vega_str
        )
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        raise HTTPException(status_code=status_code, detail=str(e))
    else:
        data = {
            "request": request,
            "query_url": query_url,
            "table": table,
            "duration": duration_ms,
            "query": query_str,
            "time": _get_time(),
            "no_rows": no_rows,
            **request.path_params,
        }
        headers = {"Gitbi-Row-Count": str(no_rows)}
        report = routes_utils.TEMPLATES.TemplateResponse(name='report.html', headers=headers, context=data)
    return report, no_rows

def _get_time():
    """
    Returns current time formatted
    """
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")