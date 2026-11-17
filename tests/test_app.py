import json

from starlette.testclient import TestClient

from app.main import app

from . import USER_HTTPX

client = TestClient(app)


def test_listing():
    assert client.get("/", auth=USER_HTTPX).status_code == 200
    assert client.get("/badpath", auth=USER_HTTPX).status_code == 404
    assert client.get("/badpath").status_code == 401


def test_query():
    assert client.get("/query/postgres/query.sql").status_code == 401
    assert client.get("/query/postgres/query.sql", auth=USER_HTTPX).status_code == 200
    assert (
        client.get("/query/postgres/incorrectfile.sql", auth=USER_HTTPX).status_code
        == 404
    )
    assert client.get("/query/sqlite/myquery.sql", auth=USER_HTTPX).status_code == 200
    assert (
        client.get("/query/sqlite/myquery_bad.sql", auth=USER_HTTPX).status_code == 200
    )
    assert (
        client.get("/query/sqlite/myquery_empty.sql", auth=USER_HTTPX).status_code
        == 200
    )
    assert (
        client.get("/query/sqlite/myquery_multi.sql", auth=USER_HTTPX).status_code
        == 200
    )
    # empty query, validations on db and query done on execute
    assert client.get("/query/sqlite").status_code == 401
    assert client.get("/query/sqlite", auth=USER_HTTPX).status_code == 200
    assert client.get("/query/postgres", auth=USER_HTTPX).status_code == 200
    assert client.get("/query/baddb", auth=USER_HTTPX).status_code == 404


def test_execute():
    assert client.post("/execute/postgres/", data={}).status_code == 401
    assert (
        client.post("/execute/postgres/", data={}, auth=USER_HTTPX).status_code == 500
    )
    assert client.post("/execute/baddb/", data={}, auth=USER_HTTPX).status_code == 500
    assert client.post("/execute/sqlite/", data={}, auth=USER_HTTPX).status_code == 500
    assert (
        client.post(
            "/execute/sqlite/", data={"baddata": 666}, auth=USER_HTTPX
        ).status_code
        == 500
    )
    assert (
        client.post(
            "/execute/sqlite/",
            data={"data": json.dumps({"query": "select badfunc();"})},
            auth=USER_HTTPX,
        ).status_code
        == 500
    )
    assert (
        client.post(
            "/execute/sqlite/",
            data={
                "data": json.dumps(
                    {
                        "query": "select badfunc();",
                        "viz": "foobar",
                        "echart_id": "foobar",
                        "query_lang": "sql",
                        "format": "bad",
                    }
                )
            },
            auth=USER_HTTPX,
        ).status_code
        == 500
    )
    assert (
        client.post(
            "/execute/sqlite/",
            data={
                "data": json.dumps(
                    {
                        "query": "select 1;",
                        "viz": "",
                        "echart_id": "",
                        "query_lang": "",
                        "format": "",
                    }
                )
            },
            auth=USER_HTTPX,
        ).status_code
        == 500
    )
    assert (
        client.post(
            "/execute/sqlite/",
            data={
                "data": json.dumps(
                    {
                        "query": "select 1;",
                        "viz": "foobar",
                        "echart_id": "foobar",
                        "query_lang": "sql",
                        "format": "text",
                    }
                )
            },
            auth=USER_HTTPX,
        ).status_code
        == 200
    )
    assert (
        client.get("/report/sqlite/incorrectfile", auth=USER_HTTPX).status_code == 404
    )
    assert (
        client.get("/report/sqlite/incorrectfile.sql", auth=USER_HTTPX).status_code
        == 404
    )
    assert (
        client.get("/report/sqlite/incorrectfile.prql", auth=USER_HTTPX).status_code
        == 404
    )
    assert client.get("/report/sqlite/myquery.sql", auth=USER_HTTPX).status_code == 404
    assert (
        client.get("/report/sqlite/myquery.sql/html", auth=USER_HTTPX).status_code
        == 200
    )
    assert (
        client.get("/report/sqlite/myquery.sql/text", auth=USER_HTTPX).status_code
        == 200
    )
    assert (
        client.get("/report/sqlite/myquery.sql/json", auth=USER_HTTPX).status_code
        == 200
    )
    assert (
        client.get("/report/sqlite/myquery.sql/invalid", auth=USER_HTTPX).status_code
        == 500
    )


def test_dashboard():
    assert client.get("/dashboard/test_dashboard.json").status_code == 401
    assert (
        client.get("/dashboard/test_dashboard.json", auth=USER_HTTPX).status_code == 200
    )
    assert client.get("/dashboard/bad_spec.json", auth=USER_HTTPX).status_code == 500
    assert client.get("/dashboard/bad_name", auth=USER_HTTPX).status_code == 500
    assert client.get("/dashboard/nonexistent.json", auth=USER_HTTPX).status_code == 404
