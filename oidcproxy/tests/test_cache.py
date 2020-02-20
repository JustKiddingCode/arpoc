from unittest.mock import Mock, patch

import pytest
import oidcproxy.cache

import oidcproxy.utils


def test_double_entries():
    cache = oidcproxy.cache.Cache()
    now = oidcproxy.utils.now()
    cache.put("a", 1, now + 10 )
    with pytest.raises(Exception):
        cache.put("a", 2, now + 10 )

def test_normal_access():
    cache = oidcproxy.cache.Cache()
    now = oidcproxy.utils.now()
    cache.put("a", 1, now + 10 )
    cache.put("b", 2, now + 10 )
    cache.put("c", 3, now + 10 )
    cache.put("d", 4, now + 10 )
    cache.put("e", 5, now + 10 )
    cache.put("f", 6, now + 10 )
    assert cache["a"] == 1
    assert cache["b"] == 2
    assert cache["c"] == 3
    assert cache["d"] == 4
    assert cache["e"] == 5
    assert cache["f"] == 6

    assert cache.get("g") is None

def test_expire():
    cache = oidcproxy.cache.Cache()
    now = oidcproxy.utils.now()
    cache.put("a", 1, now + 10)
    cache.put("b", 2, now + 5)

    with patch('oidcproxy.utils.now', Mock(return_value=now+6)):
        assert cache.get("b") == None
        assert cache.get("a") == 1
