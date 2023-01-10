import os
import re
from pygit2 import Repository

DIR = os.environ["GITBI_REPO_DIR"]
REPO = Repository(DIR)

def get_conn_str(db):
    """
    """
    var_name = f"GITBI_{db.upper()}_CONN"
    return os.environ[var_name]

def get_file_content(path):
    """
    """
    # TODO think if this should be last git version or last file on disk
    # https://stackoverflow.com/a/9684612
    with open(path, "r") as f:
        content = f.read()
        assert re.sub("\s", "", content), "File is empty"
    return content

def get_query(db, file):
    """
    """
    query_path = os.path.join(DIR, db, file)
    return get_file_content(query_path)

def get_readme():
    """
    """
    readme_path = os.path.join(DIR, "README.md")
    return get_file_content(readme_path)

def list_sources():
    """
    """
    db_dirs = {db_dir for db_dir in os.scandir(DIR) if db_dir.is_dir() and db_dir.name != ".git"}
    sources = {db_dir.name: tuple(el.name for el in os.scandir(db_dir) if el.is_file()) for db_dir in db_dirs}
    return sources
