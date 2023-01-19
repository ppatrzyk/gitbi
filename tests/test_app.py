from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)
htmx_headers = {"HX-Request": "True"}

def test_home():
    assert client.get("/home/HEAD/").status_code == 200

def test_query():
    assert client.get("/query/postgres/query.sql/HEAD").status_code == 200
    assert client.get("/query/postgres/incorrectfile/HEAD").status_code == 404
    assert client.get("/query/sqlite/incorrectfile/HEAD").status_code == 404
    assert client.get("/query/sqlite/myquery.sql/HEAD").status_code == 200
    assert client.get("/query/sqlite/myquery_bad.sql/HEAD").status_code == 200
    assert client.get("/query/sqlite/myquery_empty.sql/HEAD").status_code == 200
    assert client.get("/query/sqlite/myquery_multi.sql/HEAD").status_code == 200 

def test_execute():
    assert client.get("/execute/postgres/query.sql/HEAD").status_code == 500
    assert client.get("/execute/postgres/incorrectfile/HEAD").status_code == 500
    assert client.get("/execute/sqlite/incorrectfile/HEAD").status_code == 404
    assert client.get("/execute/sqlite/myquery.sql/HEAD").status_code == 200
    assert client.get("/execute/sqlite/myquery_bad.sql/HEAD").status_code == 500
    assert client.get("/execute/sqlite/myquery_empty.sql/HEAD").status_code == 200
    assert client.get("/execute/sqlite/myquery_multi.sql/HEAD").status_code == 200
    # htmx responses always return 200 even if there was an error
    assert client.get("/execute/postgres/incorrectfile/HEAD", headers=htmx_headers).status_code == 200
    assert client.get("/execute/sqlite/incorrectfile/HEAD", headers=htmx_headers).status_code == 200
