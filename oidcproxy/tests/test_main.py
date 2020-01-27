import oidcproxy

cfg = oidcproxy.config.OIDCProxyConfig(None, None)
cfg.proxy = oidcproxy.config.ProxyConfig("", "", "testhost.example.com/",
                                         ["test@example.com"],
                                         ["testhost.example.com/redirect"])
cfg.services['default'] = oidcproxy.config.ServiceConfig(
    "foo", "/bar", "policyset")

oidc_handler = oidcproxy.OidcHandler(cfg)
service_a = oidcproxy.ServiceProxy("default", oidc_handler)


def test_build_url():
    assert service_a._build_url("") == "foo/"
    kwargs = {'foo': 'bar', 'bar': 'foo'}
    url = service_a._build_url("", **kwargs)
    assert url == "foo/?foo=bar&bar=foo" or url == "foo/?bar=foo&foo=bar"


def test_build_proxy_url():
    assert service_a._build_proxy_url("") == "testhost.example.com/bar/"
    kwargs = {'foo': 'bar', 'bar': 'foo'}
    url = service_a._build_proxy_url("", **kwargs)
    assert url == "testhost.example.com/bar/?foo=bar&bar=foo" or url == "testhost.example.com/bar/?bar=foo&foo=bar"


def test_true():
    assert True
