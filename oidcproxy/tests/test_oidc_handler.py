import oidcproxy

import requests_mock

from unittest.mock import mock_open, patch, PropertyMock

import io

import oidcproxy.config
import pytest

import time


@pytest.fixture
def setup_jwt():
    return "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ6cWlXUmpGTk53ZUkybVhjSjZRZUluaGVBSUNhYWZBVjF1TWlnbVk4ZDVnIn0.eyJqdGkiOiJmYTQxMWM3My05MGNjLTQwNWItYTdjYy1mYzM1NTdiNWZmZjkiLCJleHAiOjE1Nzk3Nzc0NzQsIm5iZiI6MCwiaWF0IjoxNTc5Nzc3NDE0LCJpc3MiOiJodHRwczovL29wZW5pZC1wcm92aWRlci5leGFtcGxlLmNvbS9hdXRoL3JlYWxtcy9tYXN0ZXIiLCJhdWQiOlsiZ2F0ZWtlZXBlciIsIm1hc3Rlci1yZWFsbSIsImFjY291bnQiXSwic3ViIjoiOWZlOWUwNmEtNjBjNi00ZGM1LWFkNWItNjYzZjAwNmNiNGY5IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiZDNkMjljMzctNGM4MC00NzY1LWJmM2MtNTgxYzVmYTg0OTY4IiwiYXV0aF90aW1lIjoxNTc5MTY5NTI5LCJzZXNzaW9uX3N0YXRlIjoiMzg3MGJlOGEtNWUyMi00NWNhLTg1NGQtYWQ1MjBmMDlhMzM4IiwiYWNyIjoiMCIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwOi8vbG9jYWxob3N0OjgwODAiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImNyZWF0ZS1yZWFsbSIsIm9mZmxpbmVfYWNjZXNzIiwiYWRtaW4iLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImdhdGVrZWVwZXIiOnsicm9sZXMiOlsidGVzdCJdfSwibWFzdGVyLXJlYWxtIjp7InJvbGVzIjpbInZpZXctaWRlbnRpdHktcHJvdmlkZXJzIiwidmlldy1yZWFsbSIsIm1hbmFnZS1pZGVudGl0eS1wcm92aWRlcnMiLCJpbXBlcnNvbmF0aW9uIiwiY3JlYXRlLWNsaWVudCIsIm1hbmFnZS11c2VycyIsInF1ZXJ5LXJlYWxtcyIsInZpZXctYXV0aG9yaXphdGlvbiIsInF1ZXJ5LWNsaWVudHMiLCJxdWVyeS11c2VycyIsIm1hbmFnZS1ldmVudHMiLCJtYW5hZ2UtcmVhbG0iLCJ2aWV3LWV2ZW50cyIsInZpZXctdXNlcnMiLCJ2aWV3LWNsaWVudHMiLCJtYW5hZ2UtYXV0aG9yaXphdGlvbiIsIm1hbmFnZS1jbGllbnRzIiwicXVlcnktZ3JvdXBzIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBvZmZsaW5lX2FjY2VzcyBlbWFpbCBwcm9maWxlIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJhZG1pbiJ9.uWLDJ9IkzgY9EzoGQHRv-Wlx--B16C4A2gnGvk1g-84vShA61Wt8BLiAKbZEJWBrRJsGP8LSGIhEWbdZ8_fJmz9QPAtQbyo4fAN-nh2MLJvEcO1gSf2NnHgp47e3MowVSeh0xx8Gx9N_2JCHLwkBfdgejJVqAngMcw2N6m-2BesHvpEm_5zSQ4ARqTbj3GbGClQm88ZLRKfLrijS4x5Hidajndi2mSsQaFgY-Ct2P9Pao7DoUXPDxv5dvU0qlo9lXjv7qTDOVsrBHMhBP57kejbvsnc_O7BNhOtoQMwszrgHFsAVPumyEQmoVcDwfMkHY7ejSdSDWMeLHvCBsReuqg"

@pytest.fixture
def setup_oidc_handler():
    cfg = oidcproxy.config.OIDCProxyConfig(None, None)
    service_cfg = oidcproxy.config.ServiceConfig("", "", "")
    oidc_handler = oidcproxy.OidcHandler(cfg)
    return oidc_handler


@patch('oidcproxy.cherrypy.session', {'refresh': 1579702851}, create=True)
def test_check_session_refresh(setup_oidc_handler):
    oidc_handler = setup_oidc_handler
    #    oidcproxy.cherrypy.session['refresh'] = 1579702851 # Mi 22. Jan 15:21 2020
    assert oidc_handler._check_session_refresh()


@patch('oidcproxy.cherrypy.session', {'refresh': time.time() + 30},
       create=True)
def test_check_session_refresh_in_future(setup_oidc_handler):
    oidc_handler = setup_oidc_handler
    #    oidcproxy.cherrypy.session['refresh'] = 1579702851 # Mi 22. Jan 15:21 2020
    assert not oidc_handler._check_session_refresh()


@patch('oidcproxy.cherrypy.session', {}, create=True)
def test_check_session_refresh_no_time(setup_oidc_handler):
    oidc_handler = setup_oidc_handler
    #    oidcproxy.cherrypy.session['refresh'] = 1579702851 # Mi 22. Jan 15:21 2020
    assert not oidc_handler._check_session_refresh()

def test_userinfo_from_at(setup_oidc_handler, setup_jwt):
    access_token = setup_jwt
    oidc_handler = setup_oidc_handler
    
    

#
#
#def test_proxy_post(setup_proxy):
#    proxy = setup_proxy
#    oidcproxy.cherrypy.request.method = "POST"
#    with requests_mock.mock() as m:
#        m.post("http://proxyme.example.com", text='post')
#
#        oidcproxy.cherrypy.request.body = io.StringIO("some mocked up data")
#        resp = proxy._proxy("http://proxyme.example.com/")
#        assert resp.text == "post"
#        assert m.call_count == 1
#
#def test_bearer(setup_proxy_bearer):
#    proxy = setup_proxy_bearer
#    oidcproxy.cherrypy.request.method = "GET"
#    with requests_mock.mock() as m:
#        m.get("http://proxyme.example.com", text='get',request_headers={'Authorization': 'Bearer 1234'})
#        resp = proxy._proxy("http://proxyme.example.com/")
#        assert resp.text == "get"
#        assert m.call_count == 1
#
#def test_send_403(setup_proxy):
#    mock = setup_proxy._send_403("test")
#    assert "test" in mock
#
