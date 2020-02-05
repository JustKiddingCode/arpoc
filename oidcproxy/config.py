""" Configuration Module of OIDC Proxy 

After importing this file you have access to
the configuration with the `config.cfg` variable.
"""

import logging
import os
from dataclasses import InitVar, asdict, dataclass, field, replace
from typing import Dict, List, Union, Any

import yaml

LOGGING = logging.getLogger()


@dataclass
class ProviderConfig:
    """ Configuration for a single Open ID Connect Provider"""
    human_readable_name: str
    configuration_url: str = ""
    configuration_token: str = ""
    registration_token: str = ""
    registration_url: str = ""
    special_claim2scope: InitVar[dict] = None
    claim2scope: dict = field(init=False)

    def __post_init__(self, special_claim2scope: Dict) -> None:
        self.claim2scope = {
            "name": ['profile'],
            "family_name": ['profile'],
            "given_name": ['profile'],
            "middle_name": ['profile'],
            "nickname": ['profile'],
            "preferred_username": ['profile'],
            "profile": ['profile'],
            "picture": ['profile'],
            "website": ['profile'],
            "gender": ['profile'],
            "birthdate": ['profile'],
            "zoneinfo": ['profile'],
            "locale": ['profile'],
            "updated_at": ['profile'],
            "email": ["email"],
            "email_verified": ["email"],
            "address": ["address"],
            "phone": ["phone"],
            "phone_number_verified": ["phone"]
        }
        if special_claim2scope:
            for key, val in special_claim2scope.items():
                self.claim2scope[key] = val

    def __getitem__(self, key: str) -> Any:
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
    plugin_dirs: List[str] = field(default_factory=list)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


@dataclass
class ServiceConfig:
    """ Configuration for a single proxied Service"""
    origin_URL: str
    proxy_URL: str
    AC: str
    objectsetters: dict = field(default_factory=dict)
    authentication: dict = field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


def default_json_dir() -> List:
    return ["/etc/oidc-proxy/acl"]


@dataclass
class ACConfig:
    """ Configuration for the access control """
    json_dir: List[str] = field(default_factory=default_json_dir)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class ConfigError(Exception):
    pass


class OIDCProxyConfig:
    def __init__(self,
                 config_file: Union[None, str] = None,
                 std_config: Union[None, str] = '/etc/oidc-proxy/config.yml'):

        self.openid_providers: Dict[str, ProviderConfig] = {}
        self.proxy: Optional[ProxyConfig] = None
        self.services: Dict[str, ServiceConfig] = {}
        self.access_control = ACConfig()

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
        self.check_config()

    def add_provider(self, name: str, cfg: ProviderConfig) -> None:
        self.openid_providers[name] = cfg

    def print_sample_config(self) -> None:
        provider = ProviderConfig("", "", "", "", "")
        proxy = ProxyConfig("", "", "", [""], [""])
        service = ServiceConfig("", "", "", {}, {})
        ac = ACConfig()

        # delete the default values of claim2scope
        provider_dict = asdict(provider)
        del provider_dict['claim2scope']

        cfg = {
            "openid_providers": {
                "example": provider_dict
            },
            "proxy": asdict(proxy),
            "services": {
                "example": asdict(service)
            },
            "access_control": asdict(ac)
        }
        print(yaml.dump(cfg))

    def check_config_proxy_url(self) -> None:
        l: List[str] = []
        for key, service in self.services.items():
            if service.proxy_URL in l:
                raise ConfigError()
            l.append(service.proxy_URL)

    def check_config(self) -> None:
        LOGGING.debug("checking config consistency")
        self.check_config_proxy_url()

    def merge_config(self, new_cfg: Dict) -> None:
        if 'services' in new_cfg:
            for key, val in new_cfg['services'].items():
                service_cfg = ServiceConfig(**val)
                self.services[key] = service_cfg
        if 'openid_providers' in new_cfg:
            for key, val in new_cfg['openid_providers'].items():
                provider_cfg = ProviderConfig(**val)
                self.openid_providers[key] = provider_cfg
        if 'access_control' in new_cfg:
            self.access_control = ACConfig(**new_cfg['access_control'])

        if 'proxy' in new_cfg:
            if self.proxy:
                replace(self.proxy, **new_cfg['proxy'])
            else:
                self.proxy = ProxyConfig(**new_cfg['proxy'])

    def read_file(self, filepath: str) -> None:
        with open(filepath, 'r') as ymlfile:
            new_cfg = yaml.safe_load(ymlfile)

        self.merge_config(new_cfg)

    def print_config(self) -> None:
        cfg: Dict[str, Dict] = dict()
        cfg['services'] = dict()
        cfg['openid_providers'] = dict()

        for services_key, services_obj in self.services.items():
            cfg['services'][services_key] = asdict(services_obj)
        for providers_key, providers_obj in self.openid_providers.items():
            cfg['openid_providers'][providers_key] = asdict(providers_obj)
        cfg['proxy'] = asdict(self.proxy)
        cfg['access_control'] = asdict(self.access_control)
        print(yaml.dump(cfg))


cfg: Union[None, OIDCProxyConfig] = None

if __name__ == "__main__":
    cfg = OIDCProxyConfig()
    #cfg.check_config()
    #    cfg.read_file("oidcproxy/config2.yml")
    cfg.print_sample_config()
    #cfg.print_config()
