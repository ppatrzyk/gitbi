"""
common functions for all routes
"""
import csv
import datetime
import decimal
import io
import itertools
import json
import os
import prettytable
from pathlib import Path
from starlette.templating import Jinja2Templates
import uuid

VERSION = "0.10"
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
    for key in ("query", "viz", "echart_id", "file", "format", ):
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

def format_asciitable(headers, rows):
    """
    Format data into a text table
    """
    table = prettytable.PrettyTable()
    table.field_names = headers
    table.add_rows(rows)
    return table.get_string()

def format_csvtable(headers, rows):
    """
    Format data into a CSV table
    """
    out = io.StringIO()
    writer = csv.writer(out)
    for entry in itertools.chain((headers, ), rows):
        writer.writerow(entry)
    return out.getvalue()

def format_htmltable(table_id, col_names, rows, interactive):
    """
    Format data into a html table
    """
    data = {"request": None, "table_id": table_id, }
    if interactive:
        data = {**data, "data_json": get_data_json(col_names, rows)}
        response = TEMPLATES.TemplateResponse(name='partial_html_table_interactive.html', context=data)
    else:
        data = {**data, "col_names": col_names, "data": rows}
        response = TEMPLATES.TemplateResponse(name='partial_html_table.html', context=data)
    return response.body.decode()

def random_id():
    """
    Random id for html element
    """
    return f"id-{str(uuid.uuid4())}"

def get_data_json(headers, rows):
    """
    Convert data to json
    """
    if rows:
        dtypes = tuple(_data_convert(el)[1] for el in rows[0])
    else:
        dtypes = tuple(None for _ in headers)
    headers = tuple(_data_convert(el)[0] for el in headers)
    rows = tuple(tuple(_data_convert(el)[0] for el in row) for row in rows)
    return json.dumps({"headings": headers, "data": rows, "dtypes": dtypes}, default=str)

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
    return el, dtype

def common_context_args(request):
    """
    Return context args common for all endpoints
    """
    data = {
        "request": request,
        "version": VERSION,
        "user": _get_user(request),
        "state": (request.path_params.get("state") or "HEAD"),
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
