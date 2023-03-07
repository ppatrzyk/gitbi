"""
common functions for all routes
"""
import html
import json
import os
from starlette.templating import Jinja2Templates
from starlette.responses import HTMLResponse

VERSION = "0.6"
APP_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(APP_DIR, "frontend/static")
TEMPLATE_DIR = os.path.join(APP_DIR, "frontend")
TEMPLATES = Jinja2Templates(directory=TEMPLATE_DIR, autoescape=False)

def parse_query_data(request, form):
    """
    Parses and validates query data generated from query_format()
    app/frontend/js/make_code_editor.js
    query: string
    user: string
    """
    data = json.loads(form["data"])
    data["file"] = data["file"].strip()
    # TODO some viz config here
    for key in ("query", ):
        assert key in data.keys(), f"No {key} in POST data"
        assert data[key] != "", f"Empty {key} string"
    data["user"] = common_context_args(request).get("user")
    return data

def format_table(id, headers, rows, interactive):
    """
    Format data into a html table
    """
    headers = _escape_tuple(headers)
    rows = tuple(_escape_tuple(row) for row in rows)
    data = {"request": None, "id": id}
    if interactive:
        data_json = json.dumps({"headings": headers, "data": rows}, default=str)
        data = {**data, "data_json": data_json}
        response = TEMPLATES.TemplateResponse(name='partial_html_table_interactive.html', context=data)
    else:
        data = {**data, "headers": headers, "rows": rows}
        response = TEMPLATES.TemplateResponse(name='partial_html_table.html', context=data)
    return response.body.decode()

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
