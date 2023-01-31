"""
Main app file
"""
from datetime import datetime
import json
import os
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

import mailer
import query
import repo

VERSION = "0.4"
APP_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(APP_DIR, "frontend/static")
TEMPLATE_DIR = os.path.join(APP_DIR, "frontend")
TEMPLATES = Jinja2Templates(directory=TEMPLATE_DIR, autoescape=False)

# Error types
# 404 RuntimeError file not accessible
# 500 NameError variables not set
# 500 ValueError bad query

async def home_route(request):
    """
    Endpoint for home page
    """
    try:
        state = request.path_params.get("state")
        data = {
            "request": request,
            "version": VERSION,
            "state": state,
            "readme": repo.get_readme(state),
            "databases": repo.list_sources(state),
            "commits": repo.list_commits(),
        }
        return TEMPLATES.TemplateResponse(name='index.html', context=data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

async def home_default_route(request):
    """
    Default endpoint: redirect to HEAD state
    """
    return RedirectResponse(url="/home/HEAD/")

async def db_route(request):
    """
    Endpoint for listing all db info: queries and tables
    """
    try:
        db = request.path_params.get("db")
        databases = repo.list_sources(request.path_params.get("state"))
        if db not in databases:
            raise RuntimeError(f"db {db} not present in repo")
        queries = databases[db]
        tables = query.list_tables(db)
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        raise HTTPException(status_code=status_code, detail=str(e))
    else:
        data = {
            "request": request,
            "version": VERSION,
            "queries": queries,
            "tables": tables,
            **request.path_params,
        }
        return TEMPLATES.TemplateResponse(name='db.html', context=data)

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
            "state": None,
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
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        request.state.query_data = {
            "query": query_str,
            "vega": vega_str,
            "report_url": report_url,
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
        "request": request,
        "version": VERSION,
        **request.state.query_data,
    }
    return TEMPLATES.TemplateResponse(name='query.html', context=data)

async def execute_route(request):
    """
    Endpoint for getting query result
    Used by htmx
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
        return _partial_html_error(str(e), status_code)
    else:
        data = {
            "request": request,
            "table": table,
            "vega": vega_viz,
            "time": _get_time(),
            "no_rows": no_rows,
            "duration": duration_ms,
        }
        return TEMPLATES.TemplateResponse(name='result.html', context=data)

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
        response = await _mailer_response(report, to)
    else:
        response = PlainTextResponse(content=None, status_code=204)
    return response

async def email_report_route(request):
    """
    Endpoint for reports, sends report via email
    """
    to = request.query_params.get('to')
    report, _no_rows =  await _execute_from_saved_query(request)
    return await _mailer_response(report, to)

async def _mailer_response(report, to):
    """
    Wrapper for sending email
    """
    try:
        _res = mailer.send(report, to)
    except Exception as e:
        error = f"Error: {str(e)}"
        response = PlainTextResponse(content=error, status_code=500)
    else:
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
        return _partial_html_error(str(e), status_code)
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
        report = TEMPLATES.TemplateResponse(name='report.html', context=data)
        return report, no_rows

async def save_route(request):
    """
    Save query to repository
    """
    try:
        form = await request.form()
        data = json.loads(form["data"])
        data['file'] = data['file'].strip()
        repo.save(**request.path_params, **data)
        redirect_url = request.app.url_path_for(
            "saved_query_route",
            db=request.path_params['db'],
            file=data['file'],
            state="HEAD"
        )
        headers = {"HX-Redirect": redirect_url}
        response = HTMLResponse(content="<p>OK</p>", headers=headers, status_code=200)
    except Exception as e:
        status_code = 404 if isinstance(e, RuntimeError) else 500
        return _partial_html_error(str(e), status_code)
    else:
        return response

def _partial_html_error(message, code):
    """
    Creates successful reponse for htmx (with error msg)
    even if endpoint actually failed
    """
    error_msg = f"<h3>Error {code}</h3><p>{message}</p>"
    return HTMLResponse(content=error_msg, status_code=200)

async def server_error(request, exc):
    data = {
        "request": request,
        "version": VERSION,
        "code": exc.status_code,
        "message": exc.detail
    }
    return TEMPLATES.TemplateResponse(name='error.html', context=data, status_code=exc.status_code)

def _get_time():
    """
    Returns current time formatted
    """
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

routes = [
    Route("/", endpoint=home_default_route, name="home_default_route"),
    Route("/db/{db:str}/{state:str}", endpoint=db_route, name="db_route"),
    Route('/email/alert/{db:str}/{file:str}/{state:str}', endpoint=email_alert_route, name="email_alert_route"),
    Route('/email/report/{db:str}/{file:str}/{state:str}', endpoint=email_report_route, name="email_report_route"),
    Route('/execute/{db:str}', endpoint=execute_route, methods=("POST", ), name="execute_route"),
    Route("/home/{state:str}", endpoint=home_route, name="home_route"),
    Route('/query/{db:str}', endpoint=query_route, name="query_route"),
    Route('/query/{db:str}/{file:str}/{state:str}', endpoint=saved_query_route, name="saved_query_route"),
    Route('/report/{db:str}/{file:str}/{state:str}', endpoint=report_route, name="report_route"),
    Route('/save/{db:str}', endpoint=save_route, methods=("POST", ), name="save_route"),
    Mount('/static', app=StaticFiles(directory=STATIC_DIR), name="static"),
]

exception_handlers = {
    HTTPException: server_error,
}

app = Starlette(
    debug=True,
    routes=routes,
    exception_handlers=exception_handlers
)
