import arpoc.plugins.obj_urlmap

import logging


def test_urlmap_valid():
    data = {"path": "this/is/a/test/string"}
    cfg = {
        "mappings": [
            r"(?P<level1>\w+)/(?P<level2>\w+)/(?P<level3>\w+)/(?P<level4>\w+)/",
            r"(?P<map1>\w+)/(?P<map2>\w+)/(?P<map3>\w+)/(?P<map4>\w+)/(?P<map5>\w+)",
            r"this/i(?P<foo1>\w+)/(?P<foo2>\w+)/(?P<foo3>\w+)/(?P<foo4>\w+)",
            r"(?P<bar1>\w+)/(?P<bar2>\w+)/(?P<bar3>\w+)/(?P<bar4>\w+)/(?P<bar5>\w+/(?P<bar6>\w+/)",  # won't match
        ]
    }
    plugin = arpoc.plugins.obj_urlmap.ObjUrlmap(cfg)
    plugin.run(data)
    print(data)
    assert data['level1'] == 'this'
    assert data['level2'] == 'is'
    assert data['level3'] == 'a'
    assert data['level4'] == 'test'
    assert data['foo1'] == 's'
    assert 'bar1' not in data.keys()


def test_urlmap_invalid(caplog):
    caplog.set_level(logging.INFO)
    data = {"path": "this/is/a/test/string"}
    cfg = {
        "mappings": [
            r"(/inbalanced",
        ]
    }

    plugin = arpoc.plugins.obj_urlmap.ObjUrlmap(cfg)
    plugin.run(data)
    print(data)
    assert "Failed to parse regex" in caplog.text
