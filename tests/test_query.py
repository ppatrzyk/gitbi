import pytest
from contextlib import nullcontext as does_not_raise
from app.query import *

def test_get_query_result():
    with pytest.raises(ValueError):
        get_query_result('HEAD', 'sqlite', 'myquery_bad.sql')
    with pytest.raises(RuntimeError):
        get_query_result('HEAD', 'sqlite', 'badfile')
    with pytest.raises(NameError):
        get_query_result('HEAD', 'baddb', 'badfile')
    with does_not_raise():
        get_query_result('HEAD', 'sqlite', 'myquery_empty.sql')
    with does_not_raise():
        get_query_result('HEAD', 'sqlite', 'myquery_multi.sql')
    with does_not_raise():
        get_query_result('HEAD', 'sqlite', 'myquery.sql')
