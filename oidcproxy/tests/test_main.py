from __init__ import *

cfg = config.OIDCProxyConfig()
oidc_handler = OidcHandler(cfg)

serviceConfig = {
    "proxy": {
        "hostname": "PROXY/"
    },
    "services": {
        "a": {
            "origin_URL": 'foo',
            "proxy_URL": "/bar"
        }
    }
}
cfg.merge_config(serviceConfig)
service_a = ServiceProxy("a", oidc_handler)


def test_build_url():
    assert service_a._build_url("") == "foo/"
    kwargs = {'foo': 'bar', 'bar': 'foo'}
    url = service_a._build_url("", **kwargs)
    assert url == "foo/?foo=bar&bar=foo" or url == "foo/?bar=foo&foo=bar"


def test_build_proxy_url():
    assert service_a._build_proxy_url("") == "PROXY/bar/"
    kwargs = {'foo': 'bar', 'bar': 'foo'}
    url = service_a._build_proxy_url("", **kwargs)
    assert url == "PROXY/bar/?foo=bar&bar=foo" or url == "PROXY/bar/?bar=foo&foo=bar"


def test_true():
    assert True
