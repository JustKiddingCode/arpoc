import io
from unittest.mock import mock_open, patch

import pytest
import requests_mock

import oidcproxy
import oidcproxy.config


@pytest.fixture
def setup_proxy():
    cfg = oidcproxy.config.OIDCProxyConfig(None, None)
    cfg.proxy = oidcproxy.config.ProxyConfig("", "", "testhost.example.com",
                                             ["test@example.com"],
                                             ["testhost.example.com/redirect"])
    cfg.services['default'] = oidcproxy.config.ServiceConfig(
        "url_orig", "pathproxied", "policyset")
    oidc_handler = oidcproxy.OidcHandler(cfg)
    service_a = oidcproxy.ServiceProxy("default", oidc_handler,
                                       cfg.services['default'])
    return (oidc_handler, service_a)


@pytest.fixture
def setup_proxy_bearer():
    cfg = oidcproxy.config.OIDCProxyConfig(None, None)
    cfg.proxy = oidcproxy.config.ProxyConfig("", "", "testhost.example.com",
                                             ["test@example.com"],
                                             ["testhost.example.com/redirect"])
    cfg.services['default'] = oidcproxy.config.ServiceConfig("url_orig",
                                                             "pathproxied",
                                                             "policyset", {},
                                                             authentication={
                                                                 "type":
                                                                 "Bearer",
                                                                 "token": 1234
                                                             })
    oidc_handler = oidcproxy.OidcHandler(cfg)
    service_a = oidcproxy.ServiceProxy("default", oidc_handler,
                                       cfg.services['default'])
    return service_a


def test_proxy_get(setup_proxy):
    _, proxy = setup_proxy
    oidcproxy.cherrypy.request.method = "GET"
    with requests_mock.mock() as m:
        m.get("http://proxyme.example.com", text='get')
        access = proxy.build_access_dict()
        resp = proxy._proxy("http://proxyme.example.com/", access)
        assert resp.text == "get"
        assert m.call_count == 1


def test_proxy_post(setup_proxy):
    _, proxy = setup_proxy
    oidcproxy.cherrypy.request.method = "POST"
    with requests_mock.mock() as m:
        m.post("http://proxyme.example.com", text='post')
        oidcproxy.cherrypy.request.body = io.StringIO("some mocked up data")
        access = proxy.build_access_dict()
        resp = proxy._proxy("http://proxyme.example.com/", access)
        assert resp.text == "post"
        assert m.call_count == 1


def test_bearer(setup_proxy_bearer):
    proxy = setup_proxy_bearer
    oidcproxy.cherrypy.request.method = "GET"
    with requests_mock.mock() as m:
        m.get("http://proxyme.example.com",
              text='get',
              request_headers={'Authorization': 'Bearer 1234'})
        access = proxy.build_access_dict()
        resp = proxy._proxy("http://proxyme.example.com/", access)
        assert resp.text == "get"
        assert m.call_count == 1


def test_send_403(setup_proxy):
    _, proxy = setup_proxy
    mock = proxy._send_403("test")
    assert "test" in mock
