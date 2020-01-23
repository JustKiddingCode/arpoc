import oidcproxy

import requests_mock

from unittest.mock import mock_open, patch

import io

import oidcproxy.config
import pytest


@pytest.fixture
def setup_proxy():
    cfg = oidcproxy.config.OIDCProxyConfig(None, None)
    service_cfg = oidcproxy.config.ServiceConfig("", "", "")
    cfg.services = {"test": service_cfg}
    oidc_handler = oidcproxy.OidcHandler(cfg)
    proxy = oidcproxy.ServiceProxy("test", oidc_handler)
    return proxy


@pytest.fixture
def setup_proxy_bearer():
    cfg = oidcproxy.config.OIDCProxyConfig(None, None)
    service_cfg = oidcproxy.config.ServiceConfig("", "", "", {}, {
        "type": "Bearer",
        "token": 1234
    })
    cfg.services = {"test": service_cfg}
    oidc_handler = oidcproxy.OidcHandler(cfg)
    proxy = oidcproxy.ServiceProxy("test", oidc_handler)
    return proxy


def test_proxy_get(setup_proxy):
    proxy = setup_proxy
    oidcproxy.cherrypy.request.method = "GET"
    with requests_mock.mock() as m:
        m.get("http://proxyme.example.com", text='get')
        access = proxy.build_access_dict()
        resp = proxy._proxy("http://proxyme.example.com/", access)
        assert resp.text == "get"
        assert m.call_count == 1


def test_proxy_post(setup_proxy):
    proxy = setup_proxy
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
    mock = setup_proxy._send_403("test")
    assert "test" in mock
