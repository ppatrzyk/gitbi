from app.query import *
import pytest
from contextlib import nullcontext as does_not_raise

def test_get_query_data():
    with pytest.raises(ValueError):
        get_query_data('HEAD', 'sqlite', 'myquery_bad.sql')
    with does_not_raise():
        get_query_data('HEAD', 'sqlite', 'myquery_empty.sql')
    with does_not_raise():
        get_query_data('HEAD', 'sqlite', 'myquery_multi.sql')
    with does_not_raise():
        get_query_data('HEAD', 'sqlite', 'myquery.sql')