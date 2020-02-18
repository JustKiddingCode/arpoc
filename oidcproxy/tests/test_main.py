import oidcproxy

cfg = oidcproxy.config.OIDCProxyConfig(None, None)
cfg.proxy = oidcproxy.config.ProxyConfig("",
                                         "",
                                         "testhost.example.com",
                                         ["test@example.com"],
                                         redirect=["/redirect"])
cfg.services['default'] = oidcproxy.config.ServiceConfig(
    "foo", "/bar", "policyset")

oidc_handler = oidcproxy.OidcHandler(cfg)
service_a = oidcproxy.ServiceProxy("default", oidc_handler,
                                   cfg.services['default'])


def test_build_url():
    assert service_a._build_url("") == "foo/"
    kwargs = {'foo': 'bar', 'bar': 'foo'}
    url = service_a._build_url("", **kwargs)
    assert url == "foo/?foo=bar&bar=foo" or url == "foo/?bar=foo&foo=bar"


def test_build_proxy_url():
    assert service_a._build_proxy_url(
        "") == "https://testhost.example.com/bar/"
    kwargs = {'foo': 'bar', 'bar': 'foo'}
    url = service_a._build_proxy_url("", **kwargs)
    assert url in [
        "https://testhost.example.com/bar/?foo=bar&bar=foo",
        "https://testhost.example.com/bar/?bar=foo&foo=bar"
    ]


def test_retry():
    def retry_me(l: list):
        l.append(1)
        if len(l) < 5:
            raise Exception

    l = []
    app = oidcproxy.App()
    app.retry(retry_me, (Exception), l, retry_delay=2)
    app._scheduler.run()

    assert l == [1, 1, 1, 1, 1]
