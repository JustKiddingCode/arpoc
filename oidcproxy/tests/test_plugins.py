import os
from unittest.mock import patch

import oidcproxy
import oidcproxy.config
import oidcproxy.plugins

dummy_plugins = os.path.join(os.path.dirname(__file__), "resources",
                             "dummy_plugins")

proxy_cfg = oidcproxy.config.ProxyConfig("",
                                         "",
                                         "",
                                         "",
                                         plugin_dirs=[dummy_plugins])
service_cfg = oidcproxy.config.ServiceConfig("", "", "",
                                             {"dummysetter": {
                                                 "enable": True
                                             }})
app_config = oidcproxy.config.OIDCProxyConfig(None, None)
app_config.proxy = proxy_cfg
app_config.services["dummy"] = service_cfg


@patch('oidcproxy.config.cfg', app_config, create=True)
def test_import():
    oidcproxy.plugins.import_plugins()
    assert len(oidcproxy.plugins.plugins) > 0


def test_env():
    env_dict = oidcproxy.plugins.EnvironmentDict()
    assert env_dict["dummy"]
    # lets do this twice, to get caching coverage
    assert env_dict["dummy"]


@patch('oidcproxy.config.cfg', app_config, create=True)
def test_obj():
    print(oidcproxy.config.cfg.services)
    dummysetter = {"dummysetter": {"enable": True}}
    obj_dict = oidcproxy.plugins.ObjectDict(dummysetter)
    assert obj_dict['dummy']
    assert obj_dict['dummy']  # again, for caching
