import pytest
from contextlib import nullcontext as does_not_raise
from app.query import *

def test_execute():
    with pytest.raises(NameError):
        execute("baddb", "badquery", "sql")
    with pytest.raises(ValueError):
        execute("sqlite", "select badfunc();", "sql")
    with pytest.raises(Exception):
        execute("sqlite", "~", "prql")
    with does_not_raise():
        execute("sqlite", "select 1;", "sql")

def test_execute_saved():
    with pytest.raises(Exception):
        execute_saved("sqlite", "myquery_bad.sql", "HEAD")
    with does_not_raise():
        execute_saved("sqlite", "myquery.sql", "HEAD")

def test_list_tables():
    assert list_tables("sqlite") == ["mytable", ]
    with pytest.raises(NameError):
        list_tables("baddb")
    with pytest.raises(NameError):
        list_tables("postgres")
