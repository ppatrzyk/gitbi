from starlette.testclient import TestClient
from app.main import app
import json
from . import USER_HTTPX

client = TestClient(app)

def test_listing():
    assert client.get("/home/HEAD/").status_code == 401
    assert client.get("/home/HEAD/", auth=("baduser", "badpass")).status_code == 401
    assert client.get("/home/HEAD/", auth=USER_HTTPX).status_code == 200
    assert client.get("/home/badstate", auth=USER_HTTPX).status_code == 404
    assert client.get("/badpath", auth=USER_HTTPX).status_code == 404
    assert client.get("/badpath").status_code == 401

def test_query():
    assert client.get("/query/postgres/query.sql/HEAD").status_code == 401
    assert client.get("/query/postgres/query.sql/HEAD", auth=USER_HTTPX).status_code == 200
    assert client.get("/query/postgres/query.sql/badstate", auth=USER_HTTPX).status_code == 404
    assert client.get("/query/postgres/incorrectfile.sql/HEAD", auth=USER_HTTPX).status_code == 404
    assert client.get("/query/sqlite/incorrectfile.prql/HEAD", auth=USER_HTTPX).status_code == 404
    assert client.get("/query/sqlite/myquery.sql/HEAD", auth=USER_HTTPX).status_code == 200
    assert client.get("/query/sqlite/myquery_bad.sql/HEAD", auth=USER_HTTPX).status_code == 200
    assert client.get("/query/sqlite/myquery_empty.sql/HEAD", auth=USER_HTTPX).status_code == 200
    assert client.get("/query/sqlite/myquery_multi.sql/HEAD", auth=USER_HTTPX).status_code == 200
    # empty query, validations on db and query done on execute
    assert client.get("/query/sqlite").status_code == 401
    assert client.get("/query/sqlite", auth=USER_HTTPX).status_code == 200
    assert client.get("/query/postgres", auth=USER_HTTPX).status_code == 200
    assert client.get("/query/baddb", auth=USER_HTTPX).status_code == 404
    # TODO? save not tested, would need to reinit repo every time

def test_execute():
    assert client.post("/execute/postgres/", data={}).status_code == 401
    assert client.post("/execute/postgres/", data={}, auth=USER_HTTPX).status_code == 500
    assert client.post("/execute/baddb/", data={}, auth=USER_HTTPX).status_code == 500
    assert client.post("/execute/sqlite/", data={}, auth=USER_HTTPX).status_code == 500
    assert client.post("/execute/sqlite/", data={"baddata": 666}, auth=USER_HTTPX).status_code == 500
    assert client.post("/execute/sqlite/", data={"data": json.dumps({"query": "select badfunc();"})}, auth=USER_HTTPX).status_code == 500
    assert client.post("/execute/sqlite/", data={"data": json.dumps({"query": "select badfunc();", "viz": "foobar", "echart_id": "foobar", "file": "file.sql", "format": "bad"})}, auth=USER_HTTPX).status_code == 500
    assert client.post("/execute/sqlite/", data={"data": json.dumps({"query": "select 1;", "viz": "", "echart_id": "", "file": "", "format": ""})}, auth=USER_HTTPX).status_code == 500
    assert client.post("/execute/sqlite/", data={"data": json.dumps({"query": "select 1;", "viz": "foobar", "echart_id": "foobar", "file": "file.sql", "format": "text"})}, auth=USER_HTTPX).status_code == 200
    assert client.get("/report/sqlite/incorrectfile/HEAD", auth=USER_HTTPX).status_code == 404
    assert client.get("/report/sqlite/incorrectfile.sql/HEAD", auth=USER_HTTPX).status_code == 404
    assert client.get("/report/sqlite/incorrectfile.prql/HEAD", auth=USER_HTTPX).status_code == 404
    assert client.get("/report/sqlite/myquery.sql/HEAD", auth=USER_HTTPX).status_code == 404
    assert client.get("/report/sqlite/myquery.sql/HEAD/html", auth=USER_HTTPX).status_code == 200
    assert client.get("/report/sqlite/myquery.sql/HEAD/text", auth=USER_HTTPX).status_code == 200
    assert client.get("/report/sqlite/myquery.sql/HEAD/json", auth=USER_HTTPX).status_code == 200
    assert client.get("/report/sqlite/myquery.sql/HEAD/invalid", auth=USER_HTTPX).status_code == 500
    assert client.get("/email/sqlite/incorrectfile/HEAD/html", auth=USER_HTTPX).status_code == 500
    assert client.get("/email/sqlite/incorrectfile.prql/HEAD/html", auth=USER_HTTPX).status_code == 500
    assert client.get("/email/sqlite/myquery.sql/HEAD/html", auth=USER_HTTPX).status_code == 500
    assert client.get("/email/sqlite/myquery.sql/HEAD/html?to=email@email.com", auth=USER_HTTPX).status_code == 500

def test_dashboard():
    assert client.get("/dashboard/test_dashboard.json/HEAD").status_code == 401
    assert client.get("/dashboard/test_dashboard.json/HEAD", auth=USER_HTTPX).status_code == 200
    assert client.get("/dashboard/test_dashboard.json/file", auth=USER_HTTPX).status_code == 200
    assert client.get("/dashboard/test_dashboard.json/67aa8bd9b58e0ed496a440812bea4719a1361f10", auth=USER_HTTPX).status_code == 404
    assert client.get("/dashboard/bad_spec.json/HEAD", auth=USER_HTTPX).status_code == 500
    assert client.get("/dashboard/bad_name/HEAD", auth=USER_HTTPX).status_code == 500
    assert client.get("/dashboard/nonexistent.json/HEAD", auth=USER_HTTPX).status_code == 404
