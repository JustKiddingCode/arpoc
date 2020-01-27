import oidcproxy

import requests
import requests_mock

from unittest.mock import mock_open, patch, PropertyMock, Mock

import io

import oidcproxy.config
import pytest

import time

import re

import json


def provider_config():
    return """{"issuer":"https://openid-provider.example.com/auth/realms/master","authorization_endpoint":"https://openid-provider.example.com/auth/realms/master/protocol/openid-connect/auth","token_endpoint":"https://openid-provider.example.com/auth/realms/master/protocol/openid-connect/token","token_introspection_endpoint":"https://openid-provider.example.com/auth/realms/master/protocol/openid-connect/token/introspect","userinfo_endpoint":"https://openid-provider.example.com/auth/realms/master/protocol/openid-connect/userinfo","end_session_endpoint":"https://openid-provider.example.com/auth/realms/master/protocol/openid-connect/logout","jwks_uri":"https://openid-provider.example.com/auth/realms/master/protocol/openid-connect/certs","check_session_iframe":"https://openid-provider.example.com/auth/realms/master/protocol/openid-connect/login-status-iframe.html","grant_types_supported":["authorization_code","implicit","refresh_token","password","client_credentials"],"response_types_supported":["code","none","id_token","token","id_token token","code id_token","code token","code id_token token"],"subject_types_supported":["public","pairwise"],"id_token_signing_alg_values_supported":["PS384","ES384","RS384","HS256","HS512","ES256","RS256","HS384","ES512","PS256","PS512","RS512"],"id_token_encryption_alg_values_supported":["RSA-OAEP","RSA1_5"],"id_token_encryption_enc_values_supported":["A128GCM","A128CBC-HS256"],"userinfo_signing_alg_values_supported":["PS384","ES384","RS384","HS256","HS512","ES256","RS256","HS384","ES512","PS256","PS512","RS512","none"],"request_object_signing_alg_values_supported":["PS384","ES384","RS384","ES256","RS256","ES512","PS256","PS512","RS512","none"],"response_modes_supported":["query","fragment","form_post"],"registration_endpoint":"https://openid-provider.example.com/auth/realms/master/clients-registrations/openid-connect","token_endpoint_auth_methods_supported":["private_key_jwt","client_secret_basic","client_secret_post","client_secret_jwt"],"token_endpoint_auth_signing_alg_values_supported":["RS256"],"claims_supported":["aud","sub","iss","auth_time","name","given_name","family_name","preferred_username","email"],"claim_types_supported":["normal"],"claims_parameter_supported":false,"scopes_supported":["openid","address","email","microprofile-jwt","offline_access","phone","profile","roles","test","web-origins"],"request_parameter_supported":true,"request_uri_parameter_supported":true,"code_challenge_methods_supported":["plain","S256"],"tls_client_certificate_bound_access_tokens":true,"introspection_endpoint":"https://openid-provider.example.com/auth/realms/master/protocol/openid-connect/token/introspect"}"""


@pytest.fixture
def setup_jwt():
    return "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ6cWlXUmpGTk53ZUkybVhjSjZRZUluaGVBSUNhYWZBVjF1TWlnbVk4ZDVnIn0.eyJqdGkiOiJmYTQxMWM3My05MGNjLTQwNWItYTdjYy1mYzM1NTdiNWZmZjkiLCJleHAiOjE1Nzk3Nzc0NzQsIm5iZiI6MCwiaWF0IjoxNTc5Nzc3NDE0LCJpc3MiOiJodHRwczovL29wZW5pZC1wcm92aWRlci5leGFtcGxlLmNvbS9hdXRoL3JlYWxtcy9tYXN0ZXIiLCJhdWQiOlsiZ2F0ZWtlZXBlciIsIm1hc3Rlci1yZWFsbSIsImFjY291bnQiXSwic3ViIjoiOWZlOWUwNmEtNjBjNi00ZGM1LWFkNWItNjYzZjAwNmNiNGY5IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiZDNkMjljMzctNGM4MC00NzY1LWJmM2MtNTgxYzVmYTg0OTY4IiwiYXV0aF90aW1lIjoxNTc5MTY5NTI5LCJzZXNzaW9uX3N0YXRlIjoiMzg3MGJlOGEtNWUyMi00NWNhLTg1NGQtYWQ1MjBmMDlhMzM4IiwiYWNyIjoiMCIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwOi8vbG9jYWxob3N0OjgwODAiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImNyZWF0ZS1yZWFsbSIsIm9mZmxpbmVfYWNjZXNzIiwiYWRtaW4iLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImdhdGVrZWVwZXIiOnsicm9sZXMiOlsidGVzdCJdfSwibWFzdGVyLXJlYWxtIjp7InJvbGVzIjpbInZpZXctaWRlbnRpdHktcHJvdmlkZXJzIiwidmlldy1yZWFsbSIsIm1hbmFnZS1pZGVudGl0eS1wcm92aWRlcnMiLCJpbXBlcnNvbmF0aW9uIiwiY3JlYXRlLWNsaWVudCIsIm1hbmFnZS11c2VycyIsInF1ZXJ5LXJlYWxtcyIsInZpZXctYXV0aG9yaXphdGlvbiIsInF1ZXJ5LWNsaWVudHMiLCJxdWVyeS11c2VycyIsIm1hbmFnZS1ldmVudHMiLCJtYW5hZ2UtcmVhbG0iLCJ2aWV3LWV2ZW50cyIsInZpZXctdXNlcnMiLCJ2aWV3LWNsaWVudHMiLCJtYW5hZ2UtYXV0aG9yaXphdGlvbiIsIm1hbmFnZS1jbGllbnRzIiwicXVlcnktZ3JvdXBzIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBvZmZsaW5lX2FjY2VzcyBlbWFpbCBwcm9maWxlIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJhZG1pbiJ9.uWLDJ9IkzgY9EzoGQHRv-Wlx--B16C4A2gnGvk1g-84vShA61Wt8BLiAKbZEJWBrRJsGP8LSGIhEWbdZ8_fJmz9QPAtQbyo4fAN-nh2MLJvEcO1gSf2NnHgp47e3MowVSeh0xx8Gx9N_2JCHLwkBfdgejJVqAngMcw2N6m-2BesHvpEm_5zSQ4ARqTbj3GbGClQm88ZLRKfLrijS4x5Hidajndi2mSsQaFgY-Ct2P9Pao7DoUXPDxv5dvU0qlo9lXjv7qTDOVsrBHMhBP57kejbvsnc_O7BNhOtoQMwszrgHFsAVPumyEQmoVcDwfMkHY7ejSdSDWMeLHvCBsReuqg"


def registration_response():
    response = """  {
   "client_id": "s6BhdRkqt3",
   "client_secret":
     "ZJYCqe3GGRvdrudKyZS0XhGv_Z45DuKhCUk0gBR1vZk",
   "client_secret_expires_at": 1577858400,
   "registration_access_token":
     "accesstoken",
   "registration_client_uri":
     "https://openid-provider.example.com/connect/register?client_id=s6BhdRkqt3",
   "token_endpoint_auth_method":
     "client_secret_basic",
   "application_type": "web",
   "redirect_uris":
     ["https://testhost.example.org/redirect"],
   "client_name": "My Example",
   "logo_uri": "https://client.example.org/logo.png",
   "subject_type": "pairwise",
   "sector_identifier_uri":
     "https://other.example.net/file_of_redirect_uris.json",
   "jwks_uri": "https://client.example.org/my_public_keys.jwks",
   "userinfo_encrypted_response_alg": "RSA1_5",
   "userinfo_encrypted_response_enc": "A128CBC-HS256",
   "contacts": ["test@example.com"],
   "request_uris":
     ["https://client.example.org/rf.txt
       #qpXaRLh_n93TTR9F252ValdatUQvQiJi5BDub2BeznA"]
  }"""
    return re.sub(r'\s+', ' ', response)


@pytest.fixture
def setup_oidc_handler():
    cfg = oidcproxy.config.OIDCProxyConfig(None, None)
    proxyconfig = oidcproxy.config.ProxyConfig(
        "", "", "testhost.example.com", ["test@example.com"],
        ["testhost.example.com/redirect"])
    cfg.proxy = proxyconfig
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


@patch('oidcproxy.cherrypy.session', {'refresh': time.time() + 100},
       create=True)
def test_check_session_refresh_no_time(setup_oidc_handler):
    oidc_handler = setup_oidc_handler
    #    oidcproxy.cherrypy.session['refresh'] = 1579702851 # Mi 22. Jan 15:21 2020
    assert not oidc_handler._check_session_refresh()


@pytest.fixture
def setup_oidchandler_provider(setup_oidc_handler):
    oidchandler = setup_oidc_handler
    provider_config_obj = oidcproxy.config.ProviderConfig(
        "test", "https://openid-provider.example.com/auth/realms/master",
        "abcdef")
    with requests_mock.mock() as m:
        m.get(
            "https://openid-provider.example.com/auth/realms/master/.well-known/openid-configuration",
            text=provider_config())
        m.post(
            "https://openid-provider.example.com/auth/realms/master/clients-registrations/openid-connect",
            text=registration_response())
        oidchandler.register_first_time("test", provider_config_obj)

    return oidchandler


@pytest.fixture
def setup_oidchandler_provider_registration(setup_oidc_handler):
    oidchandler = setup_oidc_handler
    provider_config_obj = oidcproxy.config.ProviderConfig(
        "test", "https://openid-provider.example.com/auth/realms/master", "",
        "abcdef",
        "https://openid-provider.example.com/auth/realms/master/registerme")
    with requests_mock.mock() as m:
        m.get(
            "https://openid-provider.example.com/auth/realms/master/.well-known/openid-configuration",
            text=provider_config())
        m.get(
            "https://openid-provider.example.com/auth/realms/master/registerme",
            text=registration_response())
        oidchandler.register_first_time("test", provider_config_obj)

    return oidchandler


def test_userinfo_from_at_registration(setup_oidchandler_provider_registration,
                                       setup_jwt):
    oidc_handler = setup_oidchandler_provider_registration
    access_token = setup_jwt

    token_introspection = {"active": True, "exp": 100}

    #    oidcproxy.oic.oauth2.base.requests = requests
    #    oidcproxy.oic.extension.message.requests = requests
    with requests_mock.mock() as m:
        userinfo = {"sub": "evil", "email": "evil@test.example.com"}
        m.register_uri(
            'POST',
            "https://openid-provider.example.com/auth/realms/master/protocol/openid-connect/userinfo",
            text=json.dumps(userinfo),
            headers={'content-type': 'application/json'})
        m.register_uri(
            'POST',
            "https://openid-provider.example.com/auth/realms/master/protocol/openid-connect/token/introspect",
            text=json.dumps(token_introspection),
            headers={'content-type': 'application/json'})
        valid, resp_userinfo = oidc_handler.get_userinfo_access_token(
            access_token)
        assert valid, dict(resp_userinfo) == (100, userinfo)

        assert m.call_count > 0


def test_userinfo_from_at(setup_oidchandler_provider, setup_jwt):
    oidc_handler = setup_oidchandler_provider
    access_token = setup_jwt

    #    oidcproxy.oic.oauth2.base.requests = requests
    #    oidcproxy.oic.extension.message.requests = requests
    with requests_mock.mock() as m:
        userinfo = {"sub": "evil", "email": "evil@test.example.com"}
        token_introspection = {"active": True, "exp": 100}
        m.register_uri(
            'POST',
            "https://openid-provider.example.com/auth/realms/master/protocol/openid-connect/userinfo",
            text=json.dumps(userinfo),
            headers={'content-type': 'application/json'})
        m.register_uri(
            'POST',
            "https://openid-provider.example.com/auth/realms/master/protocol/openid-connect/token/introspect",
            text=json.dumps(token_introspection),
            headers={'content-type': 'application/json'})
        valid, resp_userinfo = oidc_handler.get_userinfo_access_token(
            access_token)
        assert valid, dict(valid, resp_userinfo) == (100, userinfo)

        assert m.call_count > 0


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
