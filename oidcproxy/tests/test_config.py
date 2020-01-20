import oidcproxy.config


cfg = oidcproxy.config.OIDCProxyConfig(std_config=None)


#def test_merge_config():
#    new_cfg = {'services': {'bla': {}}, 'openid_providers': {}}
#    expected = {
#        'openid_providers': {},
#        'proxy': {
#            'address': '0.0.0.0',
#            'port': 443,
#            'username': 'www-data',
#            'groupname': 'www-data',
#            'secrets': '/var/lib/oidc-proxy/secrets.yml',
#            'redirect': '/secure/redirect_uris'
#        },
#        'services': {
#            'bla': { 
#             'origin_URL' : "https://example.com/", 
#             'proxy_URL' : "/bla",
#             'AC' : "policyset"
#                }
#        },
#        'access_control': {}
#    }
#
#    cfg.merge_config(new_cfg)
#    assert cfg.cfg == expected
