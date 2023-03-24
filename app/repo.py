"""
Functions to interact with config repository
"""
from collections import OrderedDict
from datetime import datetime
from markdown import markdown
import os
from pathlib import Path
from pygit2 import Repository, Signature

DIR = os.environ["GITBI_REPO_DIR"]
REPO = Repository(DIR)
VALID_DB_TYPES = ("sqlite", "postgres", "clickhouse", )
VALID_QUERY_EXTENSIONS = (".sql", )

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
    query_path = os.path.join(db, file)
    try:
        viz_path = os.path.join(db, f"{file}.json")
        viz_str = _get_file_content(state, viz_path)
    except:
        viz_str = ""
    query_str = _get_file_content(state, query_path)
    return query_str, viz_str

def get_dashboard(state, file):
    """
    Get dashboard content from repo
    """
    # TODO
    return f"todo dashboard config {file}"

def get_readme(state):
    """
    Gets readme content from the repo
    """
    try:
        readme = _get_file_content(state, "README.md")
        readme = markdown(readme)
    except:
        # It is OK for README to be missing, fallback present in template
        readme = None
    return readme

def list_sources(state):
    """
    Lists all available sources (db + queries)
    """
    try:
        match state:
            case 'file':
                db_dirs = {db_dir for db_dir in os.scandir(DIR) if db_dir.is_dir() and db_dir.name != ".git"}
                sources = {db_dir.name: set(el.name for el in os.scandir(db_dir) if el.is_file()) for db_dir in db_dirs}
            case hash:
                commit = REPO.revparse_single(hash)
                sources = dict()
                for path in (Path(el) for el in _get_tree_objects_generator(commit.tree)):
                    if len(path.parts) == 2:
                        db = str(path.parent)
                        query = str(path.name)
                        try:
                            sources[db].add(query)
                        except:
                            sources[db] = set((query, ))
    except Exception as e:
        raise RuntimeError(f"Sources at state {state} cannot be listed: {str(e)}")
    else:
        return OrderedDict((db, _filter_queries(queries)) for db, queries in sorted(sources.items()))

def list_dashboards(state):
    """
    List dasboards in repo
    """
    # TODO
    return ["d1", "d2", ]

def list_commits():
    """
    Function lists all commits present in current branch of the repo
    """
    headers = ("commit_hash", "author", "date", "message")
    commits = [("file", "N/A", "now", "N/A", ), ]
    for el in REPO.walk(REPO.head.target):
        commit = (
            str(el.id),
            str(el.author),
            datetime.fromtimestamp(el.commit_time).isoformat(),
            el.message.replace("\n", ""),
        )
        commits.append(commit)
    return headers, commits

def save_dashboard(user, file, queries):
    """
    Save dashboard config into repo
    """
    # TODO
    return True

def delete_dashboard(user, file):
    """
    Save dashboard config into repo
    """
    # TODO
    return True

def save_query(user, db, file, query, viz):
    """
    Save query into repo
    file refers to query file name
    """
    path_obj = Path(file)
    assert file == path_obj.name, "Path passed"
    assert (path_obj.suffix in VALID_QUERY_EXTENSIONS), "Invalid query extension"
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

def _filter_queries(queries):
    """
    Filter which query files are valid
    """
    queries = tuple(sorted(q for q in queries if Path(q).suffix in VALID_QUERY_EXTENSIONS))
    return queries

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
        except:
            raise NameError(f"Neither {key} nor valid {file_key} was set")
    return value
