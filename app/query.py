"""
Functions to process SQL queries
"""
from clickhouse_driver import dbapi as clickhouse
import prettytable
import psycopg
import os
import repo
import sqlite3
import sqlparse

DATABASES = {
    "sqlite": sqlite3,
    "postgres": psycopg,
    "clickhouse": clickhouse
}

def get_query_data(state, db, file):
    """
    Main function to get all data about the query
    """
    db_type, conn_str = repo.get_db_params(db)
    try:
        driver = DATABASES[db_type]
    except:
        raise ValueError(f"DB type {db_type} not supported")
    query = repo.get_query(state, db, file)
    table_formatted = _execute_query(driver, conn_str, query)
    data = {
        "query": query,
        "table": table_formatted,
    }
    return data

def _format_query(result):
    """
    Format query result as html table
    TODO this might need to be changed in the future if there are paged results
    """
    try:
        table = prettytable.from_db_cursor(result)
        table_formatted = "" if table is None else table.get_html_string()
    except Exception as e:
        raise ValueError(f"Formatting error: {str(e)}")
    return table_formatted

def _execute_query(driver, conn_str, query):
    """
    Executes query against DB using suitable driver
    """
    try:
        if driver == sqlite3:
            assert os.path.exists(conn_str), f"No sqlite DB at {conn_str}"
        conn = driver.connect(conn_str)
        cursor = conn.cursor()
        statements = (sqlparse.format(s, strip_comments=True).strip() for s in sqlparse.split(query))
        statements = tuple(el for el in statements if el)
        assert statements, f"No valid SQL statements in: {query}"
        for statement in statements:
            result = cursor.execute(statement)
        table_formatted = _format_query(result)
    except Exception as e:
        raise ValueError(f"Error executing query: {str(e)}")
    finally:
        try:
            conn.close()
        except:
            pass
    return table_formatted
