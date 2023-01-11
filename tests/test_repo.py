from app.repo import *
import pytest

def test_get_readme():
    assert get_readme("f76d73c56b16bb3d74535e7f5b672066c11e17af") == "# gitbi-testing"
    assert get_readme("81b3c23584459b4e3693d6428e3fc608aab7252a") == "# gitbi-testing\nnew content\n"
    assert get_readme("5bb043654572d1d768df503e04c4dbdd3606d65f") == "# gitbi-testing\nnew content\n"
    assert get_readme("HEAD") == "# gitbi-testing\nnew content\n"
    assert get_readme("file") == "# gitbi-testing\nnew content\n"

def test_get_query():
    with pytest.raises(Exception):
        get_query("f76d73c56b16bb3d74535e7f5b672066c11e17af", "postgres", "query.sql")
    with pytest.raises(Exception):
        get_query("81b3c23584459b4e3693d6428e3fc608aab7252a", "postgres", "query.sql")
    assert get_query("5bb043654572d1d768df503e04c4dbdd3606d65f", "postgres", "query.sql") == "script file content\n"
    assert get_query("HEAD", "postgres", "query.sql") == "script file content\n"
    assert get_query("file", "postgres", "query.sql") == "script file content\n"
    with pytest.raises(Exception):
        get_query("file", "postgres", "nonexistent.sql")

def test_list_sources():
    assert list_sources("f76d73c56b16bb3d74535e7f5b672066c11e17af") == {}
    assert list_sources("81b3c23584459b4e3693d6428e3fc608aab7252a") == {"postgres": ["query.sql", ]}
    assert list_sources("5bb043654572d1d768df503e04c4dbdd3606d65f") == {"postgres": ["query.sql", ]}
    assert list_sources("HEAD") == {"postgres": ["query.sql", ]}
    assert list_sources("file") == {"postgres": ["query.sql", ]}
