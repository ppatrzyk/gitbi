"""
Functions to process SQL queries
"""
from clickhouse_driver import dbapi as clickhouse
from time import time
import psycopg
import os
import repo
import sqlite3
import sqlparse
import utils

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

def list_tables(db):
    """
    List tables in db
    """
    db_type, _conn_str = repo.get_db_params(db)
    query = TABLE_QUERIES[db_type]
    _col_names, rows, _duration_ms = execute(db, query)
    tables = sorted(el[0] for el in rows)
    return tables

def list_table_data_types(db, tables):
    """
    List columns and their data types for given tables in DB
    """
    db_type, _conn_str = repo.get_db_params(db)
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
    _col_names, rows, _duration_ms = execute(db, query)
    data_types = {table: [] for table in tables}
    for row in rows:
        data_types[row[0]].append((row[1], row[2], ))
    headers = ("column_name", "data_type", )
    data_types = {table: utils.format_table(utils.random_id(), headers, rows, True) for table, rows in data_types.items()}
    return data_types

def execute(db, query):
    """
    Executes query and returns formatted table
    """
    db_type, conn_str = repo.get_db_params(db)
    driver = DATABASES[db_type]
    start = time()
    col_names, rows = _execute_query(driver, conn_str, query)
    duration_ms = round(1000*(time()-start))
    return col_names, rows, duration_ms

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
