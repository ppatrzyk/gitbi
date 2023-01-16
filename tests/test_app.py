from starlette.testclient import TestClient
from app.main import app

def test_routes():
    client = TestClient(app)
    assert client.get('/').status_code == 200
    assert client.get('/query/postgres/query.sql').status_code == 500
    assert client.get('/query/postgres/incorrectfile').status_code == 500
    assert client.get('/query/sqlite/incorrectfile').status_code == 404
    assert client.get('/query/sqlite/myquery.sql').status_code == 200
    assert client.get('/query/sqlite/myquery_bad.sql').status_code == 500
    assert client.get('/query/sqlite/myquery_empty.sql').status_code == 200
    assert client.get('/query/sqlite/myquery_multi.sql').status_code == 200
