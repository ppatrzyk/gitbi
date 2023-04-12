"""
Functions to process SQL queries
"""
from clickhouse_driver import dbapi as clickhouse
from time import time
import duckdb
import os
import prql_python as prql
import psycopg
import repo
import sqlite3
import sqlparse
import utils

DATABASES = {
    "sqlite": sqlite3,
    "postgres": psycopg,
    "clickhouse": clickhouse,
    "duckdb": duckdb,
}

def list_tables(db):
    """
    List tables in db
    """
    db_type, _conn_str = repo.get_db_params(db)
    match db_type:
        case "sqlite" | "duckdb":
            query = "SELECT tbl_name FROM sqlite_master where type='table';"
        case "postgres":
            query = "SELECT concat(schemaname, '.', tablename) FROM pg_catalog.pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema');"
        case "clickhouse":
            query = "SELECT name FROM system.tables where database == currentDatabase();"
        case other_db:
            raise ValueError(f"Bad DB: {other_db}")
    _col_names, rows, _duration_ms = execute(db, query, "sql")
    tables = sorted(el[0] for el in rows)
    return tables

def list_table_data_types(db, tables):
    """
    List columns and their data types for given tables in DB
    """
    db_type, _conn_str = repo.get_db_params(db)
    if tables:
        match db_type:
            # Every query must return table with 3 cols: table_name, column_name, data_type
            case "sqlite" | "duckdb":
                query = " union all ".join(f"select '{table}', name, type from pragma_table_info('{table}')" for table in tables)
            case "postgres":
                tables_joined = ', '.join(f"\'{table}\'" for table in tables)
                query = f"""
                select * from
                (select concat(table_schema, '.', table_name) as table, column_name, data_type from information_schema.columns) as tables
                where tables.table in ({tables_joined});
                """
            case "clickhouse":
                tables_joined = ', '.join(f"\'{table}\'" for table in tables)
                query = f"""
                SELECT table, name, type FROM system.columns
                where database == currentDatabase() and table in ({tables_joined});
                """
            case other_db:
                raise ValueError(f"Bad DB: {other_db}")
        _col_names, rows, _duration_ms = execute(db, query, "sql")
    else:
        rows = tuple()
    col_names = ("table", "column", "type", )
    table = utils.format_htmltable(utils.random_id(), utils.random_id(), col_names, rows, True)
    return table

def execute(db, query, lang):
    """
    Executes query and returns formatted table
    """
    db_type, conn_str = repo.get_db_params(db)
    driver = DATABASES[db_type]
    start = time()
    if lang == "prql":
        query = prql.compile(query)
    col_names, rows = _execute_query(driver, conn_str, query)
    duration_ms = round(1000*(time()-start))
    return col_names, rows, duration_ms

def _execute_query(driver, conn_str, query):
    """
    Executes SQL query against DB using suitable driver
    """
    try:
        if driver in (sqlite3, duckdb, ) and conn_str != ":memory:":
            assert os.path.exists(conn_str), f"No DB file at path: {conn_str}"
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
