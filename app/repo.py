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
    conn_str_file_key = f"GITBI_{db.upper()}_CONN_FILE"
    try:
        db_type = os.environ[db_type_key]
    except:
        raise NameError(f"{db_type_key} not set")
    if db_type not in VALID_DB_TYPES:
        raise ValueError(f"DB type {db_type} not supported")
    try:
        conn_str = os.environ[conn_str_key]
    except:
        try:
            conn_str_file = os.environ[conn_str_file_key]
            conn_str = _get_file_content('file', conn_str_file)
        except:
            raise NameError(f"Neither {conn_str_key} nor valid {conn_str_file_key} was set")
    return db_type, conn_str

def get_query(state, db, file):
    """
    Gets query content from the repo
    """
    query_path = os.path.join(db, file)
    try:
        vega_path = os.path.join(db, f"{file}.json")
        vega = _get_file_content(state, vega_path)
    except:
        vega = ""
    return _get_file_content(state, query_path), vega

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

def get_crontab(state):
    """
    Read and parse crontab for shceduling
    """
    try:
        crontab = _get_file_content(state, "crontab")
        # TODO parse file to return (cron, path) tuples
    except:
        # It is OK for crontab to be missing, nothing set then
        crontab = []
    # return crontab
    return [("* * * * *", "pokemon/stats_by_type1.sql"), ]

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
                        file = str(path.name)
                        try:
                            sources[db].add(file)
                        except:
                            sources[db] = set((file, ))
    except Exception as e:
        raise RuntimeError(f"Sources at state {state} cannot be listed: {str(e)}")
    else:
        return OrderedDict((db, _filter_queries(queries)) for db, queries in sorted(sources.items()))

def list_commits():
    """
    Function lists all commits present in current branch of the repo
    """
    commits = [
        {"hash": "file", "short_hash": "file", "msg": "Current filesystem"},
    ]
    for el in REPO.walk(REPO.head.target):
        commit_hash = str(el.id)
        commit = {
            "hash": commit_hash,
            "short_hash": _short_str(commit_hash),
            "msg": el.message.replace("\n", ""),
            "date": datetime.fromtimestamp(el.commit_time).isoformat(),
        }
        commits.append(commit)
    return commits

def save(db, file, query, vega=None):
    """
    Save query into repo
    file refers to query file name
    """
    path_obj = Path(file)
    assert file == path_obj.name, "Path passed"
    assert (path_obj.suffix in VALID_QUERY_EXTENSIONS), "Invalid query extension"
    path = f"{db}/{file}"
    index = REPO.index
    assert _write_file_content(path, query), "Writing file content failed"
    index.add(path)
    if vega is not None:
        vega_path = f"{path}.json"
        assert _write_file_content(vega_path, vega), "Writing file content failed"
        index.add(vega_path)
    index.write()
    author = Signature(name='Gitbi', email="gitbi@gitbi.gitbi")
    REPO.create_commit(
        REPO.head.name, # reference_name
        author, # author
        author, # committer
        f"[gitbi] DB {db}, saving {file}", # message
        index.write_tree(), # tree
        [REPO.head.target, ] # parents
    )
    return True

def _short_str(s):
    """
    Make shorter version of string for presentation
    """
    if len(s) > 11:
        short = f"{s[:4]}...{s[-4:]}"
    else:
        short = s
    return short

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
    with open(os.path.join(DIR, path), "w") as f:
        f.write(content)
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
