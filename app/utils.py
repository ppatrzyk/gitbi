import os
import re

DIR = os.environ["gitbi_repo_dir"]
# TODO think if this should be last git version or last file on disk
# https://stackoverflow.com/a/9684612

def get_readme():
    """
    """
    readme_path = os.path.join(DIR, "README.md")
    try:
        with open(readme_path, "r") as f:
            readme = f.read()
            assert re.sub("\s", "", readme), "empty file"
    except:
        readme = None
    finally:
        return readme

def list_sources():
    """
    """
    db_dirs = {db_dir.path for db_dir in os.scandir(DIR) if db_dir.is_dir() and db_dir.name != ".git"}
    sources = {db_dir: tuple(el.path for el in os.scandir(db_dir) if el.is_file()) for db_dir in db_dirs}
    return sources

# TODO get conn strings for listed databases
