"""
Routes for executing queries
"""
from starlette.exceptions import HTTPException
from starlette.responses import PlainTextResponse
from datetime import datetime
import mailer
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
        query_data = utils.parse_query_data(request, form)
        col_names, rows, duration_ms = query.execute(
            db=request.path_params.get("db"),
            query=query_data.get("query"),
            lang=utils.get_lang(query_data.get("file"))
        )
        format = query_data.get("format")
        no_rows = len(rows)
        data_json = utils.get_data_json(col_names, rows)
        data = {
            **utils.common_context_args(request),
            "time": _get_time(),
            "no_rows": no_rows,
            "duration": duration_ms,
            "data_json": data_json,
            "echart_id": query_data["echart_id"],
        }
        match format:
            case "interactive-table" | "simple-table":
                interactive = (format == "interactive-table")
                table_id = f"results-table-{utils.random_id()}"
                table = utils.format_htmltable(table_id, col_names, rows, interactive)
            case "text" | "csv" | "json":
                match format:
                    case "text":
                        table = utils.format_asciitable(col_names, rows)
                    case "csv":
                        table = utils.format_csvtable(col_names, rows)
                    case "json":
                        table = data_json
                table = f'<pre class="text-result"><code>{table}</pre></code>'
            case other:
                raise ValueError(f"Bad format: {other}")
        data = {**data, "table": table}
        headers = {"Gitbi-Row-Count": str(no_rows)}
        response = utils.TEMPLATES.TemplateResponse(name='partial_result.html', headers=headers, context=data)
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        raise HTTPException(status_code=status_code, detail=str(e))
    else:
        return response

async def report_route(request):
    """
    Endpoint for running reports
    i.e. executes saved query and passes ready result in given format
    """
    try:
        format = request.path_params.get("format")
        query_args = {k: request.path_params[k] for k in ("db", "file", "state")}
        query_str = repo.get_query(**query_args)
        col_names, rows, duration_ms = query.execute_saved(**query_args)
        no_rows = len(rows)
        headers = {"Gitbi-Row-Count": str(no_rows), "Gitbi-Duration-Ms": str(duration_ms)}
        table_id = f"results-table-{utils.random_id()}"
        common_data = {
            **utils.common_context_args(request),
            **request.path_params,
            "time": _get_time(),
            "duration": duration_ms,
            "no_rows": no_rows,
        }
        match format:
            case "html":
                table = utils.format_htmltable(table_id, col_names, rows, False)
                data = {
                    **common_data,
                    "table": table,
                    # TODO pass this everywhere
                    "query": query_str,
                }
                response = utils.TEMPLATES.TemplateResponse(name='report.html', headers=headers, context=data)
            case "dashboard":
                table = utils.format_htmltable(table_id, col_names, rows, True)
                data_json = utils.get_data_json(col_names, rows)
                viz_str = repo.get_query_viz(**query_args)
                data = {
                    **common_data,
                    "table": table,
                    "viz": viz_str,
                    "echart_id": utils.random_id(),
                    "tab_id": utils.random_id(),
                    "data_json": data_json,
                }
                response = utils.TEMPLATES.TemplateResponse(name='partial_dashboard_entry.html', context=data)
            case "text":
                table = utils.format_asciitable(col_names, rows)
                data = {
                    **common_data,
                    "table": table,
                }
                response = utils.TEMPLATES.TemplateResponse(name='report.txt', headers=headers, context=data, media_type="text/plain")
            case "json":
                response = PlainTextResponse(content=utils.get_data_json(col_names, rows), headers=headers, media_type="application/json")
            case "csv":
                table = utils.format_csvtable(col_names, rows)
                response = PlainTextResponse(content=table, headers=headers, media_type="text/csv")
            case other:
                raise ValueError(f"Bad format: {other}")
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        raise HTTPException(status_code=status_code, detail=str(e))
    else:
        return response

def _get_time():
    """
    Returns current time formatted
    """
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
