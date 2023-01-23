from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)
htmx_headers = {"HX-Request": "True"}

def test_home():
    assert client.get("/home/HEAD/").status_code == 200
    assert client.get("/home/badstate").status_code == 404

def test_query():
    assert client.get("/query/postgres/query.sql/HEAD").status_code == 200
    assert client.get("/query/postgres/query.sql/badstate").status_code == 404
    assert client.get("/query/postgres/incorrectfile/HEAD").status_code == 404
    assert client.get("/query/sqlite/incorrectfile/HEAD").status_code == 404
    assert client.get("/query/sqlite/myquery.sql/HEAD").status_code == 200
    assert client.get("/query/sqlite/myquery_bad.sql/HEAD").status_code == 200
    assert client.get("/query/sqlite/myquery_empty.sql/HEAD").status_code == 200
    assert client.get("/query/sqlite/myquery_multi.sql/HEAD").status_code == 200
    # empty query, validations on db and query done on execute
    assert client.get("/query/sqlite").status_code == 200
    assert client.get("/query/postgres").status_code == 200
    assert client.get("/query/baddb").status_code == 404

def test_execute():
    assert client.post("/execute/postgres/", data={"query": "--", "vega": ""}).status_code == 500
    assert client.post("/execute/baddb/", data={"query": "--", "vega": ""}).status_code == 500
    assert client.post("/execute/sqlite/", data={"query": "--", "vega": ""}).status_code == 500
    assert client.post("/execute/sqlite/", data={"query": "select badfunc();", "vega": ""}).status_code == 500
    assert client.post("/execute/sqlite/", data={"query": "select 1;", "vega": ""}).status_code == 200
    # htmx responses always return 200 even if there was an error
    assert client.post("/execute/sqlite/", data={"query": "select badfunc();", "vega": ""}, headers=htmx_headers).status_code == 200
    assert client.post("/execute/sqlite/", data={"query": "select 1;", "vega": ""}, headers=htmx_headers).status_code == 200

def test_db():
    assert client.get("/db/postgres/HEAD").status_code == 500
    assert client.get("/db/sqlite/HEAD").status_code == 200
    assert client.get("/db/baddb/HEAD").status_code == 404
