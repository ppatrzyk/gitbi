import repo

# TODO execute query against db

def get_query(db, file):
    """
    """
    conn_str = repo.get_conn_str(db)
    query = repo.get_query(db, file)
    return query
