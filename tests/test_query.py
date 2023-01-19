import pytest
from contextlib import nullcontext as does_not_raise
from app.query import *

def test_execute_from_file():
    with pytest.raises(ValueError):
        execute_from_file('HEAD', 'sqlite', 'myquery_bad.sql')
    with pytest.raises(RuntimeError):
        execute_from_file('HEAD', 'sqlite', 'badfile')
    with pytest.raises(NameError):
        execute_from_file('HEAD', 'baddb', 'badfile')
    with does_not_raise():
        execute_from_file('HEAD', 'sqlite', 'myquery_empty.sql')
    with does_not_raise():
        execute_from_file('HEAD', 'sqlite', 'myquery_multi.sql')
    with does_not_raise():
        execute_from_file('HEAD', 'sqlite', 'myquery.sql')

def test_list_tables():
    assert list_tables("sqlite") == ("mytable", )
    with pytest.raises(NameError):
        list_tables("baddb")
    with pytest.raises(NameError):
        list_tables("postgres")
