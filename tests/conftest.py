import os
from . import USERS

def pytest_configure(config):
    os.environ["GITBI_AUTH"] = USERS
    os.environ["GITBI_REPO_DIR"] = os.path.abspath("./tests/gitbi-testing")
    os.environ["GITBI_SQLITE_CONN"] = os.path.abspath("./tests/gitbi-testing/db.sqlite")
    os.environ["GITBI_SQLITE_TYPE"] = "sqlite"
