"""
common functions for all routes
"""
import html
import json
import os
from starlette.templating import Jinja2Templates
from starlette.responses import HTMLResponse

VERSION = "0.5"
APP_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(APP_DIR, "frontend/static")
TEMPLATE_DIR = os.path.join(APP_DIR, "frontend")
TEMPLATES = Jinja2Templates(directory=TEMPLATE_DIR, autoescape=False)
VEGA_DEFAULTS = {
    "config": {
        "font": "system-ui",
        "axis": {"labelFontSize": 16, "titleFontSize": 20},
        "legend": {"labelFontSize": 16},
        "header": {"labelFontSize": 16},
        "text": {"fontSize": 16},
        "title": {"fontSize": 24},
    },
}

def format_table(id, headers, rows, interactive):
    """
    Format data into a html table
    """
    headers = _escape_tuple(headers)
    rows = tuple(_escape_tuple(row) for row in rows)
    data = {"request": None, "id": id}
    if interactive:
        data = {**data, "data_json": json.dumps({"headings": headers, "data": rows})}
        response = TEMPLATES.TemplateResponse(name='partial_html_table_interactive.html', context=data)
    else:
        data = {**data, "headers": headers, "rows": rows}
        response = TEMPLATES.TemplateResponse(name='partial_html_table.html', context=data)
    return response.body.decode()

def format_vega(col_names, rows, vega):
    """
    Joins passed vega lite specification with received data
    """
    try:
        assert vega, "No vega specification"
        vega = json.loads(vega)
        data = tuple({col: row[i] for i, col in enumerate(col_names, start=0)} for row in rows)
        vega = {**VEGA_DEFAULTS, "data": {"values": data}, **vega}
    except Exception as e:
        vega = {"error": str(e)}
    return json.dumps(vega)

def _escape_tuple(t):
    """
    Helper for escaping tuple of elements
    """
    return tuple(html.escape(el) if isinstance(el, str) else el for el in t)

def partial_html_error(message, code):
    """
    Creates successful (200) reponse for htmx (with error msg)
    even if endpoint actually failed
    """
    error_msg = f"<h3>Error {code}</h3><p>{message}</p>"
    return HTMLResponse(content=error_msg, status_code=200)

def common_context_args(request):
    """
    Return context args common for all endpoints
    """
    data = {
        "request": request,
        "version": VERSION,
        "user": _get_user(request),
        "state": None, # to be overwritten if exists
    }
    return data

def _get_user(request):
    """
    Get user name, if exists
    """
    try:
        user = request.user.display_name
    except:
        user = None
    return user
