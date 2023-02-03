"""
common functions for all routes
"""
import os
from starlette.templating import Jinja2Templates
from starlette.responses import HTMLResponse

VERSION = "0.5"
APP_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(APP_DIR, "frontend/static")
TEMPLATE_DIR = os.path.join(APP_DIR, "frontend")
TEMPLATES = Jinja2Templates(directory=TEMPLATE_DIR, autoescape=False)

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
