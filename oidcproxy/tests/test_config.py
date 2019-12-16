from config import *

cfg = OIDCProxyConfig(std_config=None)

def test_merge_config():
    new_cfg = {'services': {'bla' : { }}, 'openid_providers': {} }
    expected = {'openid_providers': {}, 'proxy': {'address': '0.0.0.0', 'port': 443, 'username': 'www-data', 'groupname': 'www-data', 'secrets': '/var/lib/oidc-proxy/secrets.yml', 'redirect': '/secure/redirect_uris'}, 'services': {'bla': {}}, 'access_control': {}}
    cfg.merge_config(new_cfg)
    assert cfg.cfg == expected
