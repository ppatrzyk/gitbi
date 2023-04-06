"""
common functions for all routes
"""
import datetime
import decimal
import html
import json
import os
from pathlib import Path
from starlette.templating import Jinja2Templates
import uuid

VERSION = "0.7"
APP_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(APP_DIR, "frontend/static")
TEMPLATE_DIR = os.path.join(APP_DIR, "frontend")
TEMPLATES = Jinja2Templates(directory=TEMPLATE_DIR, autoescape=False)

def parse_query_data(request, form):
    """
    Parses and validates query data generated from query_format()
    app/frontend/js/code_editor.js
    query, user, viz: string
    """
    data = json.loads(form["data"])
    data["file"] = data["file"].strip()
    for key in ("query", "viz", "echart_id", "file", ):
        assert key in data.keys(), f"No {key} in POST data"
        assert data[key] != "", f"Empty {key} string"
    data["user"] = common_context_args(request).get("user")
    return data

def parse_dashboard_data(request, form):
    """
    Parses and validates query data generated from dashboard_format()
    app/frontend/js/dashboard_creation.js
    """
    data = json.loads(form["data"])
    data["file"] = data["file"].strip()
    assert data["file"] != "", "Empty file name"
    assert data["queries"], "zero queries chosen"
    data["queries"] = json.dumps(tuple(el.split('/') for el in data["queries"]))
    data["user"] = common_context_args(request).get("user")
    return data

def get_lang(file):
    """
    Establish query language based on file extension
    """
    suffix = Path(file).suffix
    return suffix[1:]

def format_table(table_id, echart_id, headers, rows, interactive):
    """
    Format data into a html table
    """
    if rows:
        dtypes = tuple(_data_convert(el)[1] for el in rows[0])
    else:
        dtypes = tuple(None for _ in headers)
    headers = tuple(_data_convert(el)[0] for el in headers)
    rows = tuple(tuple(_data_convert(el)[0] for el in row) for row in rows)
    data = {"request": None, "table_id": table_id, "echart_id": echart_id}
    if interactive:
        data_json = json.dumps({"headings": headers, "data": rows, "dtypes": dtypes}, default=str)
        data = {**data, "data_json": data_json}
        response = TEMPLATES.TemplateResponse(name='partial_html_table_interactive.html', context=data)
    else:
        data = {**data, "headers": headers, "data": rows}
        response = TEMPLATES.TemplateResponse(name='partial_html_table.html', context=data)
    return response.body.decode()

def random_id():
    """
    Random id for html element
    """
    return f"id-{str(uuid.uuid4())}"

def _data_convert(el):
    """
    Convert complex types such that it can be passed to json.dumps
    Data type names determined for echarts
    https://echarts.apache.org/en/option.html#xAxis.type
    """
    match el:
        case decimal.Decimal() | float():
            el = float(el)
            dtype = "value"
        case int():
            dtype = "value"
        case datetime.datetime():
            el = datetime.datetime.isoformat(el)
            dtype = "time"
        case _:
            el = str(el)
            dtype = "category"
    if isinstance(el, str):
        el = html.escape(el)
    return el, dtype

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
