"""
Functions to interact with config repository
"""
from collections import OrderedDict
from datetime import datetime
import json
import logging
from markdown import markdown
import os
from pathlib import Path
from pygit2 import Repository, Signature
import utils

DIR = os.environ["GITBI_REPO_DIR"]
REPO = Repository(DIR)
VALID_DB_TYPES = ("sqlite", "postgres", "clickhouse", "duckdb", )
VALID_QUERY_EXTENSIONS = (".sql", ".prql", )
VALID_DASHBOARD_EXTENSIONS = (".json", )
DASHBOARDS_DIR = "_dashboards"
DASHBOARDS_FULL_PATH = os.path.join(DIR, DASHBOARDS_DIR)
if not os.path.exists(DASHBOARDS_FULL_PATH):
    os.makedirs(DASHBOARDS_FULL_PATH)
QUERIES_EXCLUDE = (".git", DASHBOARDS_DIR, )
SCHEDULE_KEYS = ("cron", "db", "file", "type", "format", "to", )

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

def get_query(state, db, file):
    """
    Gets query content from the repo
    """
    assert Path(file).suffix in VALID_QUERY_EXTENSIONS, "Bad query extension"
    lang = utils.get_lang(file)
    query_path = os.path.join(db, file)
    query_str = _get_file_content(state, query_path)
    return query_str, lang

def get_query_viz(state, db, file):
    """
    Gets saved viz for given query
    """
    try:
        viz_path = os.path.join(db, f"{file}.json")
        viz_str = _get_file_content(state, viz_path)
    except:
        viz_str = "null" # this is read by JS
    return viz_str

def get_dashboard(state, file):
    """
    Get dashboard content from repo
    """
    assert Path(file).suffix in VALID_DASHBOARD_EXTENSIONS, "Bad dashboard extension"
    path = os.path.join(DASHBOARDS_DIR, file)
    raw_dashboard = _get_file_content(state, path)
    return json.loads(raw_dashboard)

def get_readme(state):
    """
    Gets readme content from the repo
    """
    try:
        readme = _get_file_content(state, "README.md")
        readme = markdown(readme)
    except Exception as e:
        # It is OK for README to be missing, fallback present in template
        logging.warning(f"Readme not specified: {str(e)}")
        readme = None
    return readme

def list_sources(state):
    """
    Lists all available sources (db + queries)
    """
    try:
        match state:
            case 'file':
                db_dirs = {db_dir for db_dir in os.scandir(DIR) if db_dir.is_dir() and db_dir.name not in QUERIES_EXCLUDE}
                sources = {db_dir.name: _list_file_names(db_dir) for db_dir in db_dirs}
            case hash:
                commit = REPO.revparse_single(hash)
                sources = dict()
                for path in (Path(el) for el in _get_tree_objects_generator(commit.tree)):
                    if len(path.parts) == 2: #files in 1st-level folder, all other ignored
                        db = str(path.parent)
                        query = str(path.name)
                        if db not in QUERIES_EXCLUDE:
                            try:
                                sources[db].add(query)
                            except:
                                sources[db] = set((query, ))
        sources = OrderedDict((db, _filter_extension(queries, VALID_QUERY_EXTENSIONS)) for db, queries in sorted(sources.items()))
    except Exception as e:
        raise RuntimeError(f"Sources at state {state} cannot be listed: {str(e)}")
    else:
        return sources

def list_dashboards(state):
    """
    List dasboards in repo
    """
    try:
        match state:
            case 'file':
                dashboards = _list_file_names(DASHBOARDS_FULL_PATH)
            case hash:
                commit = REPO.revparse_single(hash)
                repo_paths = (Path(el) for el in _get_tree_objects_generator(commit.tree))
                dashboards = tuple(path.name for path in repo_paths if (len(path.parts) == 2 and str(path.parent) == DASHBOARDS_DIR))
        dashboards = _filter_extension(dashboards, VALID_DASHBOARD_EXTENSIONS)
    except Exception as e:
        raise RuntimeError(f"Dashboards at state {state} cannot be listed: {str(e)}")
    else:
        return dashboards

def list_commits():
    """
    Function lists all commits present in current branch of the repo
    """
    headers = ("commit_hash", "author", "date", "message")
    commits = [("file", "N/A", "now", "N/A", ), ]
    for entry in REPO.walk(REPO.head.target):
        commit = _format_commit(entry)
        commits.append(commit)
    return headers, commits

def _format_commit(entry):
    """
    Format commit tuple
    """
    commit = (
        str(entry.id),
        str(entry.author),
        datetime.fromtimestamp(entry.commit_time).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
        entry.message.replace("\n", ""),
    )
    return commit

def save_dashboard(user, file, queries):
    """
    Save dashboard config into repo
    """
    path_obj = Path(file)
    assert file == path_obj.name, "Path passed"
    assert (path_obj.suffix in VALID_DASHBOARD_EXTENSIONS), f"Extension not in {str(VALID_DASHBOARD_EXTENSIONS)}"
    path = f"{DASHBOARDS_DIR}/{file}"
    assert _write_file_content(path, queries), "Writing query content failed"
    _commit(user, "save", (path, ))
    return True

def delete_dashboard(user, file):
    """
    Delete dashboard config
    """
    path = f"{DASHBOARDS_DIR}/{file}"
    assert _remove_file(path), f"Cannot remove {path}"
    _commit(user, "delete", (path, ))
    return True

def save_query(user, db, file, query, viz):
    """
    Save query into repo
    file refers to query file name
    """
    path_obj = Path(file)
    assert file == path_obj.name, "Path passed"
    assert (path_obj.suffix in VALID_QUERY_EXTENSIONS), f"Extension not in {str(VALID_QUERY_EXTENSIONS)}"
    query_path = f"{db}/{file}"
    viz_path = f"{query_path}.json"
    to_commit = [query_path, viz_path, ]
    assert _write_file_content(query_path, query), "Writing query content failed"
    assert _write_file_content(viz_path, viz), "Writing viz content failed"
    _commit(user, "save", to_commit)
    return True

def delete_query(user, db, file):
    """
    Delete query from the repo
    """
    query_path = f"{db}/{file}"
    viz_path = f"{query_path}.json"
    to_commit = [query_path, ]
    assert _remove_file(query_path), f"Cannot remove {query_path}"
    try:
        _remove_file(viz_path)
    except:
        pass
    else:
        to_commit.append(viz_path)
    #TODO: if fails error not caught, not recoverable in Gitbi, one needs to checkout manually
    _commit(user, "delete", to_commit)
    return True

def get_schedule(state):
    """
    Read and parse schedule file
    """
    try:
        schedule_str = _get_file_content(state, "schedule.json")
        schedule = json.loads(schedule_str)
        for entry in schedule:
            _validate_schedule_entry(entry)
    except Exception as e:
        # It is OK for schedule to be missing, nothing set then
        logging.warning(f"Schedule not specified: {str(e)}")
        schedule = []
    return schedule

def _validate_schedule_entry(entry):
    """
    Check if schedule entry is ok
    """
    assert set(SCHEDULE_KEYS) == set(entry.keys()), f"Bad keys in {str(entry)}"
    type = entry.get("type")
    assert type in ("report", "alert", ), f"Bad type {type}"
    format = entry.get("format")
    assert format in ("html", "text", "csv", "json", ), f"Bad format {format}"
    return True

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

def _write_file_content(path, content):
    """
    Change file contents on disk
    """
    full_path = os.path.join(DIR, path)
    with open(full_path, "w") as f:
        f.write(content)
    return True

def _remove_file(path):
    """
    Remove file from disk
    """
    full_path = os.path.join(DIR, path)
    assert os.path.exists(full_path), f"no file {path}"
    os.remove(full_path)
    return True

def _get_file_content(state, path):
    """
    Read file content from git or filesystem
    """
    try:
        match state:
            case 'file':
                with open(os.path.join(DIR, path), "r") as f:
                    content = f.read()
            case hash:
                commit = REPO.revparse_single(hash)
                blob = commit.tree / path
                content = blob.data.decode("UTF-8")
    except Exception as e:
        # Common error for atual no file, permission, repo error etc.
        raise RuntimeError(f"File {path} at state {state} cannot be accessed: {str(e)}")
    else:
        return content

def _get_tree_objects_generator(tree, prefix=""):
    """
    List files from given state of the repo
    """
    for obj in tree:
        if obj.type_str == "blob":
            yield os.path.join(prefix, obj.name)
        elif obj.type_str == "tree":
            new_prefix = os.path.join(prefix, obj.name)
            for entry in _get_tree_objects_generator(obj, new_prefix):
                yield entry

def _commit(user, operation, files):
    """
    Commit given file to repo
    """
    assert files, "empty list passed"
    files_msg = ", ".join(files)
    index = REPO.index
    for file in files:
        match operation:
            case "save":
                index.add(file)
            case "delete":
                index.remove(file)
            case operation:
                raise ValueError(f"Bad operation: {operation}")
    index.write()
    author = Signature(name=(user or "Gitbi (no auth)"), email="gitbi@gitbi.gitbi")
    REPO.create_commit(
        REPO.head.name, # reference_name
        author, # author
        author, # committer
        f"[gitbi] {operation} {files_msg}", # message
        index.write_tree(), # tree
        [REPO.head.target, ] # parents
    )
    return True

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
            value = _get_file_content('file', value_file)
        except Exception as e:
            raise NameError(f"Neither {key} nor valid {file_key} was set: {str(e)}")
    return value
