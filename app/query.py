"""
Functions to process SQL queries
"""
from clickhouse_driver import dbapi as clickhouse
from prettytable import PrettyTable
import json
import psycopg
import os
import re
import repo
import sqlite3
import sqlparse

DATABASES = {
    "sqlite": sqlite3,
    "postgres": psycopg,
    "clickhouse": clickhouse
}

def list_tables(db):
    """
    List tables in db
    """
    db_type, conn_str = repo.get_db_params(db)
    driver = DATABASES[db_type]
    match driver:
        case sqlite3:
            query = "SELECT * FROM sqlite_master where type='table';"
    _col_names, rows = _execute_query(driver, conn_str, query)
    tables = tuple(el[1] for el in rows)
    return tables

def execute(db, query, vega):
    """
    Executes query and returns formatted table
    """
    db_type, conn_str = repo.get_db_params(db)
    driver = DATABASES[db_type]
    col_names, rows = _execute_query(driver, conn_str, query)
    table = _format_table(col_names, rows)
    vega_viz = _format_vega(col_names, rows, vega)
    return table, vega_viz

def execute_from_file(state, db, file):
    """
    Reads query from repo and executes it
    # TODO currently not used, left for alerts and reports
    """
    query, vega = repo.get_query(state, db, file)
    return execute(db, query, vega)

def _format_table(col_names, rows):
    """
    Format query result as html table
    """
    try:
        table = PrettyTable()
        table.field_names = col_names
        table.add_rows(rows)
        table_formatted = "" if table is None else table.get_html_string()
        table_formatted = re.sub("<table>", """<table role="grid">""", table_formatted)
    except Exception as e:
        table_formatted = f"<p>Formatting error: {str(e)}</p>"
    return table_formatted

def _format_vega(col_names, rows, vega):
    """
    Joins passed vega lite specification with received data
    """
    try:
        assert vega, "No vega specification"
        vega = json.loads(vega)
        data = tuple(tuple({col: row[i]} for i, col in enumerate(col_names, start=0)) for row in rows)
        vega = {**vega, "$schema": "/static/js/vega/v5.json", "data": {"values": data}}
        vega_viz = f"<p>TODO: {vega}</p>"
    except Exception as e:
        vega_viz = f"<p>Formatting error: {str(e)}</p>"
    return vega_viz

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
        col_names = tuple(el[0] for el in cursor.description)
        rows = result.fetchall()
    except Exception as e:
        raise ValueError(f"Error executing query: {str(e)}")
    finally:
        try:
            conn.close()
        except:
            pass
    return col_names, rows
