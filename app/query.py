"""
Functions to process SQL queries
"""
from clickhouse_driver import dbapi as clickhouse
import os
import prettytable
import psycopg
import re
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
    driver, conn_str = _get_db_params(db)
    query = repo.get_query(state, db, file)
    table_formatted = _execute_query(driver, conn_str, query)
    data = {
        "query": query,
        "table": table_formatted,
    }
    return data

def _get_db_params(db):
    """
    Reads database configuration from environment variables
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
        conn = driver.connect(conn_str)
        cursor = conn.cursor()
        statements = tuple(el for el in sqlparse.split(query) if not re.search(r"^\s?--", el))
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
