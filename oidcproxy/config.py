""" Configuration Module of OIDC Proxy 

After importing this file you have access to
the configuration with the `config.cfg` variable.
"""

import yaml

import os

from dataclasses import dataclass, field, replace, asdict
from typing import List


@dataclass
class ProviderConfig:
    """ Configuration for a single Open ID Connect Provider"""
    human_readable_name: str
    configuration_url: str = ""
    configuration_token: str = ""
    registration_token: str = ""
    registration_url: str = ""

    def __getitem__(self, key):
        return getattr(self, key)


@dataclass
class ProxyConfig:
    """ Configuration for the Proxy Setup """
    keyfile: str
    certfile: str
    hostname: str
    contacts: List[str]
    redirect_uris: List[str]
    address: str = "0.0.0.0"
    port: int = 443
    username: str = "www-data"
    groupname: str = "www-data"
    secrets: str = "/var/lib/oidc-proxy/secrets.yml"
    redirect: str = "/secure/redirect_uris"

    def __getitem__(self, key):
        return getattr(self, key)


@dataclass
class ServiceConfig:
    """ Configuration for a single proxied Service"""
    origin_URL: str
    proxy_URL: str
    AC: str
    objectsetters: dict = field(default_factory=dict)
    authentication: dict = field(default_factory=dict)

    def __getitem__(self, key):
        return getattr(self, key)


def default_json_dir():
    return ["/etc/oidc-proxy/acl"]


@dataclass
class ACConfig:
    """ Configuration for the access control """
    json_dir: List[str] = field(default_factory=default_json_dir)

    def __getitem__(self, key):
        return getattr(self, key)


class ConfigError(Exception):
    pass


class OIDCProxyConfig:
    def __init__(self,
                 config_file=None,
                 std_config='/etc/oidc-proxy/config.yml'):
        self.__cfg = {
            "openid_providers": {},
            "proxy": None,
            "services": {},
            'access_control': ACConfig()
        }

        default_paths = [std_config]
        if 'OIDC_PROXY_CONFIG' in os.environ:
            default_paths.append(os.environ['OIDC_PROXY_CONFIG'])

        if config_file:
            default_paths.append(config_file)

        for filepath in default_paths:
            if filepath:
                try:
                    self.read_file(filepath)
                except IOError:
                    pass

    def __getattr__(self, name):
        if name == "cfg":
            return self.__cfg
        if name in self.__cfg.keys():
            return self.__cfg[name]

    def __getitem__(self, key):
        if key == "cfg":
            return self.__cfg
        if key in self.__cfg.keys():
            return self.__cfg[key]

    def print_sample_config(self):
        provider = ProviderConfig("", "", "", "", "")
        proxy = ProxyConfig("", "", "", [""], [""])
        service = ServiceConfig("", "", "", {}, {})
        ac = ACConfig()

        cfg = {
            "openid_providers": {
                "example": asdict(provider)
            },
            "proxy": asdict(proxy),
            "services": {
                "example": asdict(service)
            },
            "access_control": asdict(ac)
        }
        print(yaml.dump(cfg))

    def check_config(self):
        # there needs to be three keys in the config
        cfg_keys = set(
            ['openid_providers', 'proxy', 'services', 'access_control'])
        if cfg_keys != set(self.__cfg.keys()):
            raise ConfigError("Only top-level keys allowed are: %s" % cfg_keys)

    def merge_config(self, new_cfg):
        if 'services' in new_cfg:
            for key, val in new_cfg['services'].items():
                service_cfg = ServiceConfig(**val)
                self.__cfg['services'][key] = service_cfg
        if 'openid_providers' in new_cfg:
            for key, val in new_cfg['openid_providers'].items():
                provider_cfg = ProviderConfig(**val)
                self.__cfg['openid_providers'][key] = provider_cfg
        if 'access_control' in new_cfg:
            self.__cfg['access_control'] = ACConfig(
                **new_cfg['access_control'])

        if 'proxy' in new_cfg:
            if self.__cfg['proxy']:
                replace(self.__cfg['proxy'], **new_cfg['proxy'])
            else:
                self.__cfg['proxy'] = ProxyConfig(**new_cfg['proxy'])

    def read_file(self, filepath):
        with open(filepath, 'r') as ymlfile:
            new_cfg = yaml.safe_load(ymlfile)

        self.merge_config(new_cfg)

    def print_config(self):
        cfg = dict()
        cfg['services'] = dict()
        cfg['openid_providers'] = dict()

        for key, val in self.__cfg['services'].items():
            cfg['services'][key] = asdict(val)
        for key, val in self.__cfg['openid_providers'].items():
            cfg['openid_providers'][key] = asdict(val)
        cfg['proxy'] = asdict(self.__cfg['proxy'])
        cfg['access_control'] = asdict(self.__cfg['access_control'])
        print(yaml.dump(cfg))


cfg = None

if __name__ == "__main__":
    cfg = OIDCProxyConfig()
    #cfg.check_config()
    #    cfg.read_file("oidcproxy/config2.yml")
    cfg.print_sample_config()
    #cfg.print_config()
