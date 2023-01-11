import os
import repo

# TODO execute query against db

def get_query(state, db, file):
    """
    """
    # conn_str = repo.get_conn_str(db)
    data = {
        "query": repo.get_query(state, db, file),
    }
    return data
