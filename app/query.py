"""
Functions to process SQL queries
"""
from clickhouse_driver import dbapi as clickhouse
from prettytable import PrettyTable
from time import time
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
    "clickhouse": clickhouse,
}
TABLE_QUERIES = {
    "sqlite": "SELECT tbl_name FROM sqlite_master where type='table';",
    "postgres": "SELECT concat(schemaname, '.', tablename) FROM pg_catalog.pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema');",
    "clickhouse": "SELECT name FROM system.tables where database == currentDatabase();",
}
VEGA_DEFAULTS = {
    "config": {
        "font": "system-ui",
        "axis": {"labelFontSize": 16, "titleFontSize": 20},
        "legend": {"labelFontSize": 16},
        "header": {"labelFontSize": 16},
        "text": {"fontSize": 16},
        "title": {"fontSize": 24},
    },
}

def list_tables(db):
    """
    List tables in db
    """
    db_type, conn_str = repo.get_db_params(db)
    driver = DATABASES[db_type]
    query = TABLE_QUERIES[db_type]
    _col_names, rows = _execute_query(driver, conn_str, query)
    tables = sorted(el[0] for el in rows)
    return tables

def list_table_data_types(db, tables):
    """
    List columns and their data types for given tables in DB
    """
    db_type, conn_str = repo.get_db_params(db)
    driver = DATABASES[db_type]
    match db_type:
        # Every query must return table with 3 cols: table_name, column_name, data_type
        case "sqlite":
            query = " union all ".join(f"select '{table}', name, type from pragma_table_info('{table}')" for table in tables)
        case "postgres":
            tables_joined = ', '.join(f"\'{table}\'" for table in tables)
            query = f"""
            select * from
            (select concat(table_schema, '.', table_name) as table, column_name, data_type from information_schema.columns) as tables
            where tables.table in ({tables_joined});
            """
        case "clickhouse":
            query = "SELECT table, name, type FROM system.columns where database == currentDatabase();"
        case other_db:
            raise ValueError(f"Bad DB: {other_db}")
    _col_names, rows = _execute_query(driver, conn_str, query)
    data_types = {table: [] for table in tables}
    for row in rows:
        data_types[row[0]].append((row[1], row[2], ))
    return data_types

def execute(db, query, vega):
    """
    Executes query and returns formatted table
    """
    db_type, conn_str = repo.get_db_params(db)
    driver = DATABASES[db_type]
    start = time()
    col_names, rows = _execute_query(driver, conn_str, query)
    duration_ms = round(1000*(time()-start))
    table = _format_table(col_names, rows)
    if vega is not None:
        vega_viz = _format_vega(col_names, rows, vega)
    else:
        vega_viz = None
    return table, vega_viz, duration_ms, len(rows)

def _format_table(col_names, rows):
    """
    Format query result as html table
    """
    try:
        table = PrettyTable()
        table.field_names = col_names
        table.add_rows(rows)
        table_formatted = "" if table is None else table.get_html_string()
        table_formatted = re.sub("<table>", """<table id="results-table" role="grid">""", table_formatted)
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
        data = tuple({col: row[i] for i, col in enumerate(col_names, start=0)} for row in rows)
        vega = {**VEGA_DEFAULTS, "data": {"values": data}, **vega}
    except Exception as e:
        vega = {"error": str(e)}
    return json.dumps(vega)

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
            cursor.execute(statement)
        col_names = tuple(el[0] for el in cursor.description)
        rows = cursor.fetchall()
    except Exception as e:
        raise ValueError(f"Error executing query: {str(e)}")
    finally:
        try:
            conn.close()
        except:
            pass
    return col_names, rows
