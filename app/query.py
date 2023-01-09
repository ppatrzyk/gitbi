import utils

# TODO execute query against db

def get_query(db, file):
    """
    """
    conn_str = utils.get_conn_str(db)
    query = utils.get_query(db, file)
    return query
