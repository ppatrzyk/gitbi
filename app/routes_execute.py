"""
Routes for executing queries
"""
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, PlainTextResponse
from datetime import datetime
import mailer
import prettytable
import query
import repo
import utils

async def execute_route(request):
    """
    Endpoint for getting query result
    Executes query POSTed from app, used by htmx
    """
    try:
        form = await request.form()
        data = utils.parse_query_data(request, form)
        col_names, rows, duration_ms = query.execute(
            db=request.path_params.get("db"),
            query=data.get("query"),
            lang=utils.get_lang(data.get("file"))
        )
        table_id = f"results-table-{utils.random_id()}"
        table = utils.format_table(table_id, data["echart_id"], col_names, rows, True)
        no_rows = len(rows)
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        data = {"request": request, "code": status_code, "message": str(e)}
        return utils.TEMPLATES.TemplateResponse(name='partial_error.html', context=data)
    else:
        data = {
            **utils.common_context_args(request),
            "table": table,
            "time": _get_time(),
            "no_rows": no_rows,
            "duration": duration_ms,
        }
        headers = {"Gitbi-Row-Count": str(no_rows)}
        return utils.TEMPLATES.TemplateResponse(name='partial_result.html', headers=headers, context=data)

async def report_route(request):
    """
    Endpoint for running reports
    This just returns html with report
    """
    format = (request.query_params.get("format") or "html")
    report, _no_rows =  await _execute_from_saved_query(request, format)
    return report

async def email_route(request):
    """
    Endpoint for reports/alerts sent via email
    """
    try:
        file_name = request.path_params.get("file")
        to = request.query_params.get("to")
        format = (request.query_params.get("format") or "html")
        type = (request.query_params.get("type") or "report")
        assert type in ("report", "alert", ), "Bad type"
        report, no_rows =  await _execute_from_saved_query(request, format)
        if (no_rows == 0) and (type == "alert"):
            response = PlainTextResponse(content=None, status_code=204)
        else:
            response = await _mailer_response(report, to, file_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return response

async def _mailer_response(report, to, file_name):
    """
    Wrapper for sending email
    """
    try:
        _res = mailer.send(report, to, file_name)
    except Exception as e:
        error = f"Error: {str(e)}"
        response = PlainTextResponse(content=error, status_code=500)
    else:
        response = PlainTextResponse(content="OK", status_code=200)
    return response

async def dashboard_entry_route(request):
    """
    Single entry in dashboard - execute from saved query
    """
    query_str, viz, lang = repo.get_query(**request.path_params)
    col_names, rows, _duration_ms = query.execute(
        db=request.path_params.get("db"),
        query=query_str,
        lang=lang
    )
    table_id = utils.random_id()
    echart_id = utils.random_id()
    table = utils.format_table(table_id, echart_id, col_names, rows, True)
    data = {
        **utils.common_context_args(request),
        **request.path_params,
        "table": table,
        "viz": viz,
        "echart_id": echart_id,
        "time": _get_time(),
    }
    return utils.TEMPLATES.TemplateResponse(name='partial_dashboard_entry.html', context=data)

async def _execute_from_saved_query(request, format):
    """
    Execute saved query, common logic for reports and alerts
    format: html, text, json
    Called by:
    - report
    - email alert/report
    """
    try:
        query_url = request.url_for("saved_query_route", **request.path_params)
        query_str, _viz, lang = repo.get_query(**request.path_params)
        col_names, rows, duration_ms = query.execute(
            db=request.path_params.get("db"),
            query=query_str,
            lang=lang
        )
        time = _get_time()
        no_rows = len(rows)
        headers = {"Gitbi-Row-Count": str(no_rows)}
        match format:
            case "html":
                table = utils.format_table(f"results-table-{utils.random_id()}", utils.random_id(), col_names, rows, False)
                data = {
                    **utils.common_context_args(request),
                    "query_url": query_url,
                    "table": table,
                    "duration": duration_ms,
                    "query": query_str,
                    "time": time,
                    "no_rows": no_rows,
                    **request.path_params,
                }
                response = utils.TEMPLATES.TemplateResponse(name='report.html', headers=headers, context=data)
            case "text":
                table = prettytable.PrettyTable()
                table.field_names = col_names
                table.add_rows(rows)
                data = {
                    **utils.common_context_args(request),
                    "duration": duration_ms,
                    "no_rows": no_rows,
                    "time": time,
                    "table": table.get_string(),
                    **request.path_params,
                }
                response = utils.TEMPLATES.TemplateResponse(name='report.txt', headers=headers, context=data, media_type="text/plain")
            case "json":
                data = {"headers": col_names, "rows": rows, "duration_ms": duration_ms}
                response = JSONResponse(content=data, headers=headers)
            case other:
                raise ValueError(f"Bad format: {other}")
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        raise HTTPException(status_code=status_code, detail=str(e))
    else:
        return response, no_rows

def _get_time():
    """
    Returns current time formatted
    """
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
