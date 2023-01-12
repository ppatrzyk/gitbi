import os
import repo
import prettytable
import sqlite3

# TODO execute query against db
DATABASES = {
    "sqlite": sqlite3,
}

def get_query_data(state, db, file):
    """
    """
    driver, conn_str = _get_db_params(db)
    query = repo.get_query(state, db, file)
    result = _execute_query(driver, conn_str, query)
    data = {
        "query": query,
        "result": result,
    }
    return data

def _get_db_params(db):
    """
    """
    db_type_key = f"GITBI_{db.upper()}_TYPE"
    conn_str_key = f"GITBI_{db.upper()}_CONN"
    try:
        db_type = os.environ[db_type_key]
        conn_str = os.environ[conn_str_key]
    except:
        raise NameError(f"DB variables ({db_type_key} and {conn_str_key}) not set")
    try:
        driver = DATABASES[db_type]
    except:
        raise ValueError(f"DB type {db_type} not supported")
    return driver, conn_str

def _execute_query(driver, conn_str, query):
    """
    """
    try:
        conn = driver.connect(conn_str)
        cursor = conn.cursor()
        result = cursor.execute(query)
        table = prettytable.from_db_cursor(result)
        table_formatted = table.get_html_string()
    except Exception as e:
        raise ValueError(f"Error executing query: {str(e)}")
    finally:
        try:
            conn.close()
        except:
            pass
    return table_formatted
