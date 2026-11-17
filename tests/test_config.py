import pytest

from app.config import *


def test_get_readme():
    latest = "<h1>gitbi-testing</h1>\n<p>new content</p>"
    assert get_readme() == latest


def test_get_query():
    query_sql_latest = (
        "script file content\n",
        "sql",
    )
    query_sql_latest_viz = "null"
    assert get_query("postgres", "query.sql") == query_sql_latest
    assert get_query_viz("postgres", "query.sql") == query_sql_latest_viz
    with pytest.raises(RuntimeError):
        get_query("postgres", "nonexistent.sql")
    myquery_sql_latest = (
        "select * from mytable;\n-- comment\n",
        "sql",
    )
    myquery_sql_latest_viz = ""
    assert get_query("sqlite", "myquery.sql") == myquery_sql_latest
    assert get_query_viz("sqlite", "myquery.sql") == myquery_sql_latest_viz


def test_get_dashboard():
    latest = [
        [
            "sqlite",
            "myquery.sql",
        ],
    ]
    assert get_dashboard("test_dashboard.json") == latest
    with pytest.raises(Exception):
        get_dashboard("bad_spec.json")
    with pytest.raises(Exception):
        get_dashboard("nonexistent.json")


def test_list_sources():
    latest = {
        "postgres": ("query.sql",),
        "sqlite": (
            "myquery.sql",
            "myquery_bad.sql",
            "myquery_empty.sql",
            "myquery_multi.sql",
        ),
    }
    assert list_sources() == latest


def test_list_dashboards():
    latest = (
        "bad_spec.json",
        "test_dashboard.json",
    )
    assert list_dashboards() == latest
