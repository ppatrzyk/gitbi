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

def get_file_content(path):
    """
    """
    with open(path, "r") as f:
        content = f.read()
        assert re.sub("\s", "", content), "File is empty"
    return content

# https://stackoverflow.com/a/9684612
def get_tree_objects(tree):
    """
    """
    return tuple(get_tree_objects_generator(tree, prefix=""))

def get_tree_objects_generator(tree, prefix=""):
    """
    """
    for obj in tree:
        if obj.type_str == "blob":
            yield os.path.join(prefix, obj.name)
        elif obj.type_str == "tree":
            new_prefix = os.path.join(prefix, obj.name)
            for entry in get_tree_objects_generator(obj, new_prefix):
                yield entry

def get_file_content_git(tree, path):
    """
    """
    #TODO path is relative without DIR, unify later
    blob = tree / path
    return blob.data.decode("UTF-8")

# head = REPO.revparse_single('HEAD')
# commits = tuple(commit for commit in REPO.walk(REPO.head.target))
