import pytest
from app.repo import *

def test_get_readme():
    assert get_readme("incorrect_commit_hash") is None
    assert get_readme("f76d73c56b16bb3d74535e7f5b672066c11e17af") == "<h1>gitbi-testing</h1>"
    latest = "<h1>gitbi-testing</h1>\n<p>new content</p>"
    assert get_readme("81b3c23584459b4e3693d6428e3fc608aab7252a") == latest
    assert get_readme("5bb043654572d1d768df503e04c4dbdd3606d65f") == latest
    assert get_readme("836bd2dced3aad27abb0c1def6de4696e0722dfe") == latest
    assert get_readme("bdd50332c25777feaaee7b3f40a4a42ab173ae18") == latest
    assert get_readme("38ceabd502ad82f828f640e418fce0bd1d45a2bd") == latest
    assert get_readme("67aa8bd9b58e0ed496a440812bea4719a1361f10") == latest
    assert get_readme("47725449de77fc06fcae8d1f9bebbcacad4f5864") == latest
    assert get_readme("HEAD") == latest
    assert get_readme("file") == latest

def test_get_query():
    with pytest.raises(RuntimeError):
        get_query("incorrect_commit_hash", "postgres", "query.sql")
    with pytest.raises(RuntimeError):
        get_query("f76d73c56b16bb3d74535e7f5b672066c11e17af", "postgres", "query.sql")
    assert get_query("81b3c23584459b4e3693d6428e3fc608aab7252a", "postgres", "query.sql") == ("", "")
    query_sql_latest = "script file content\n"
    assert get_query("5bb043654572d1d768df503e04c4dbdd3606d65f", "postgres", "query.sql") == (query_sql_latest, "")
    assert get_query("836bd2dced3aad27abb0c1def6de4696e0722dfe", "postgres", "query.sql") == (query_sql_latest, "")
    assert get_query("bdd50332c25777feaaee7b3f40a4a42ab173ae18", "postgres", "query.sql") == (query_sql_latest, "")
    assert get_query("38ceabd502ad82f828f640e418fce0bd1d45a2bd", "postgres", "query.sql") == (query_sql_latest, "")
    assert get_query("67aa8bd9b58e0ed496a440812bea4719a1361f10", "postgres", "query.sql") == (query_sql_latest, "")
    assert get_query("47725449de77fc06fcae8d1f9bebbcacad4f5864", "postgres", "query.sql") == (query_sql_latest, "")
    assert get_query("HEAD", "postgres", "query.sql") == (query_sql_latest, "")
    assert get_query("file", "postgres", "query.sql") == (query_sql_latest, "")
    with pytest.raises(RuntimeError):
        get_query("file", "postgres", "nonexistent.sql")
    myquery_sql_latest = "select * from mytable;\n-- comment\n"
    assert get_query("836bd2dced3aad27abb0c1def6de4696e0722dfe", "sqlite", "myquery.sql") == (myquery_sql_latest, "")
    assert get_query("bdd50332c25777feaaee7b3f40a4a42ab173ae18", "sqlite", "myquery.sql") == (myquery_sql_latest, "")
    assert get_query("38ceabd502ad82f828f640e418fce0bd1d45a2bd", "sqlite", "myquery.sql") == (myquery_sql_latest, "")
    assert get_query("67aa8bd9b58e0ed496a440812bea4719a1361f10", "sqlite", "myquery.sql") == (myquery_sql_latest, "")
    assert get_query("47725449de77fc06fcae8d1f9bebbcacad4f5864", "sqlite", "myquery.sql") == (myquery_sql_latest, "")
    assert get_query("HEAD", "sqlite", "myquery.sql") == (myquery_sql_latest, "")
    assert get_query("file", "sqlite", "myquery.sql") == (myquery_sql_latest, "")

def test_get_dashboard():
    latest = [["sqlite", "myquery.sql", ], ]
    assert get_dashboard("file", "test_dashboard.json") == latest
    assert get_dashboard("47725449de77fc06fcae8d1f9bebbcacad4f5864", "test_dashboard.json") == latest
    with pytest.raises(Exception):
        get_dashboard("67aa8bd9b58e0ed496a440812bea4719a1361f10", "test_dashboard.json")
    with pytest.raises(Exception):
        get_dashboard("47725449de77fc06fcae8d1f9bebbcacad4f5864", "bad_spec.json")
    with pytest.raises(Exception):
        get_dashboard("47725449de77fc06fcae8d1f9bebbcacad4f5864", "nonexistent.json")

def test_list_sources():
    with pytest.raises(RuntimeError):
        list_sources("incorrect_commit_hash")
    assert list_sources("f76d73c56b16bb3d74535e7f5b672066c11e17af") == {}
    assert list_sources("81b3c23584459b4e3693d6428e3fc608aab7252a") == {"postgres": ("query.sql", )}
    assert list_sources("5bb043654572d1d768df503e04c4dbdd3606d65f") == {"postgres": ("query.sql", )}
    assert list_sources("836bd2dced3aad27abb0c1def6de4696e0722dfe") == {"postgres": ("query.sql", ), "sqlite": ("myquery.sql", )}
    latest = {"postgres": ("query.sql", ), "sqlite": ("myquery.sql", "myquery_bad.sql", "myquery_empty.sql",  "myquery_multi.sql")}
    assert list_sources("bdd50332c25777feaaee7b3f40a4a42ab173ae18") == latest
    assert list_sources("38ceabd502ad82f828f640e418fce0bd1d45a2bd") == latest
    assert list_sources("67aa8bd9b58e0ed496a440812bea4719a1361f10") == latest
    assert list_sources("47725449de77fc06fcae8d1f9bebbcacad4f5864") == latest
    assert list_sources("HEAD") == latest
    assert list_sources("file") == latest

def test_list_commits():
    _headers, commits = list_commits()
    assert commits[0][0] == "file"
    assert commits[1][0] == "47725449de77fc06fcae8d1f9bebbcacad4f5864"
    assert commits[2][0] == "67aa8bd9b58e0ed496a440812bea4719a1361f10"
    assert commits[3][0] == "38ceabd502ad82f828f640e418fce0bd1d45a2bd"

def test_list_dashboards():
    latest = ("bad_spec.json", "test_dashboard.json", )
    assert list_dashboards("file") == latest
    assert list_dashboards("47725449de77fc06fcae8d1f9bebbcacad4f5864") == latest
    assert list_dashboards("67aa8bd9b58e0ed496a440812bea4719a1361f10") == tuple()
