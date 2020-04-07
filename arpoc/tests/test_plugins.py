import os
from unittest.mock import patch

import arpoc
import arpoc.config
import arpoc.plugins
from arpoc.plugins._lib import deep_dict_update

dummy_plugins = os.path.join(os.path.dirname(__file__), "resources",
                             "dummy_plugins")

proxy_cfg = arpoc.config.ProxyConfig("",
                                         "",
                                         "",
                                         "",
                                         plugin_dirs=[dummy_plugins])
service_cfg = arpoc.config.ServiceConfig("", "", "",
                                             {"dummysetter": {
                                                 "enable": True
                                             }})
app_config = arpoc.config.OIDCProxyConfig(None, None)
app_config.proxy = proxy_cfg
app_config.services["dummy"] = service_cfg


@patch('arpoc.config.cfg', app_config, create=True)
def test_import():
    arpoc.plugins.import_plugins()
    assert len(arpoc.plugins.plugins) > 0


def test_env():
    env_dict = arpoc.plugins.EnvironmentDict()
    assert env_dict["dummy"]
    # lets do this twice, to get caching coverage
    assert env_dict["dummy"]


@patch('arpoc.config.cfg', app_config, create=True)
def test_obj():
    print(arpoc.config.cfg.services)
    dummysetter = {"dummysetter": {"enable": True}}
    obj_dict = arpoc.plugins.ObjectDict(dummysetter)
    assert obj_dict['dummy']
    assert obj_dict['dummy']  # again, for caching


def test_deep_dict_update():
    logger_cfg = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "obligation_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "obligation.log",
                "maxBytes": 1024,
                "backupCount": 3
            }
        },
        "loggers": {
            "obligation_logger": {
                "level": "INFO",
                "handlers": ["obligation_file"]
            }
        }
    }
    new_cfg = {"handlers": {"obligation_file": {"filename": "new.log"}}}
    merged = deep_dict_update(logger_cfg, new_cfg)
    assert merged['handlers']['obligation_file']['filename'] == "new.log"
    assert merged['handlers']['obligation_file']['maxBytes'] == 1024
    assert merged['loggers']['obligation_logger']['level'] == "INFO"
