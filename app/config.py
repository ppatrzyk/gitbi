"""
Functions to interact with config
"""

import json
import logging
import os
from collections import OrderedDict
from pathlib import Path

import utils
from markdown import markdown

DIR = os.environ["GITBI_CONFIG_DIR"]
VALID_DB_TYPES = (
    "sqlite",
    "postgres",
    "clickhouse",
    "duckdb",
)
VALID_QUERY_EXTENSIONS = (
    ".sql",
    ".prql",
)
VALID_DASHBOARD_EXTENSIONS = (".json",)
DASHBOARDS_DIR = "_dashboards"
DASHBOARDS_FULL_PATH = os.path.join(DIR, DASHBOARDS_DIR)
if not os.path.exists(DASHBOARDS_FULL_PATH):
    os.makedirs(DASHBOARDS_FULL_PATH)
QUERIES_EXCLUDE = (DASHBOARDS_DIR,)


def get_db_params(db):
    """
    Reads database configuration from environment variables
    """
    db_type_key = f"GITBI_{db.upper()}_TYPE"
    conn_str_key = f"GITBI_{db.upper()}_CONN"
    db_type = _read_env_var(db_type_key)
    conn_str = _read_env_var(conn_str_key)
    if db_type not in VALID_DB_TYPES:
        raise ValueError(f"DB type {db_type} not supported")
    return db_type, conn_str


def get_email_params():
    """
    Reads environment variables for email
    """
    smtp_user = _read_env_var("GITBI_SMTP_USER")
    smtp_pass = _read_env_var("GITBI_SMTP_PASS")
    smtp_url = _read_env_var("GITBI_SMTP_URL")
    smtp_email = _read_env_var("GITBI_SMTP_EMAIL")
    return smtp_user, smtp_pass, smtp_url, smtp_email


def get_auth():
    """
    Get authentication configuration
    """
    users_raw = _read_env_var("GITBI_AUTH")
    users = tuple(entry.strip() for entry in users_raw.split(","))
    assert users, "Empty user list"
    return users


def get_query(db, file):
    """
    Gets query content
    """
    assert Path(file).suffix in VALID_QUERY_EXTENSIONS, "Bad query extension"
    lang = utils.get_lang(file)
    query_path = os.path.join(db, file)
    query_str = _get_file_content(query_path)
    return query_str, lang


def get_query_viz(db, file):
    """
    Gets saved viz for given query
    """
    try:
        viz_path = os.path.join(db, f"{file}.json")
        viz_str = _get_file_content(viz_path)
    except:
        viz_str = "null"  # this is read by JS
    return viz_str


def get_dashboard(file):
    """
    Get dashboard content
    """
    assert Path(file).suffix in VALID_DASHBOARD_EXTENSIONS, "Bad dashboard extension"
    path = os.path.join(DASHBOARDS_DIR, file)
    raw_dashboard = _get_file_content(path)
    return json.loads(raw_dashboard)


def get_readme():
    """
    Gets readme content from the repo
    """
    try:
        readme = _get_file_content("README.md")
        readme = markdown(readme)
    except Exception as e:
        # It is OK for README to be missing, fallback present in template
        logging.warning(f"Readme not specified: {e!s}")
        readme = None
    return readme


def list_sources():
    """
    Lists all available sources (db + queries)
    """
    try:
        db_dirs = {
            db_dir
            for db_dir in os.scandir(DIR)
            if db_dir.is_dir() and db_dir.name not in QUERIES_EXCLUDE
        }
        sources = {db_dir.name: _list_file_names(db_dir) for db_dir in db_dirs}
        sources = OrderedDict(
            (db, _filter_extension(queries, VALID_QUERY_EXTENSIONS))
            for db, queries in sorted(sources.items())
        )
    except Exception as e:
        raise RuntimeError(f"Sources cannot be listed: {e!s}")
    else:
        return sources


def list_dashboards():
    """
    List dasboards in repo
    """
    try:
        dashboards = _list_file_names(DASHBOARDS_FULL_PATH)
        dashboards = _filter_extension(dashboards, VALID_DASHBOARD_EXTENSIONS)
    except Exception as e:
        raise RuntimeError(f"Dashboards cannot be listed: {e!s}")
    else:
        return dashboards


def _list_file_names(dir):
    """
    List file names in given directory
    """
    return tuple(el.name for el in os.scandir(dir) if el.is_file())


def _filter_extension(files, valid_ext):
    """
    Filter file list based on extension
    """
    return tuple(sorted(f for f in files if Path(f).suffix in valid_ext))


def _get_file_content(path):
    """
    Read file content from filesystem
    """
    try:
        with open(os.path.join(DIR, path), "r") as f:
            content = f.read()
    except Exception as e:
        raise RuntimeError(f"File {path} cannot be accessed: {e!s}")
    else:
        return content


def _read_env_var(key):
    """
    Read variable, also attempt to take from file
    """
    try:
        value = os.environ[key]
    except:
        try:
            file_key = f"{key}_FILE"
            value_file = os.environ[file_key]
            value = _get_file_content(value_file)
        except Exception as e:
            raise NameError(f"Neither {key} nor valid {file_key} was set: {e!s}")
    return value
