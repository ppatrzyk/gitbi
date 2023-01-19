"""
Functions to interact with config repository
"""
from datetime import datetime
from markdown import markdown
import os
from pathlib import Path
from pygit2 import Repository

DIR = os.environ["GITBI_REPO_DIR"]
REPO = Repository(DIR)
VALID_DB_TYPES = ("sqlite", "postgres", "clickhouse", )

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
    return _get_file_content(state, query_path)

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
                        file = str(path.name)
                        try:
                            sources[db].add(file)
                        except:
                            sources[db] = set((file, ))
    except Exception as e:
        raise RuntimeError(f"Sources at state {state} cannot be listed: {str(e)}")
    else:
        return {db: tuple(sorted(queries)) for db, queries in sources.items()}

def list_commits():
    """
    Function lists all commits present in current branch of the repo
    """
    commits = [{"hash": "file", "msg": "Current filesystem"}, ]
    for el in REPO.walk(REPO.head.target):
        commit = {
            "hash": str(el.id),
            "msg": el.message.replace("\n", ""),
            "date": datetime.fromtimestamp(el.commit_time).isoformat(),
        }
        commits.append(commit)
    return commits

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
