import importlib.resources
import yaml

import os

class ConfigError(Exception):
    pass

class OIDCProxyConfig:
    def __init__(self,config_file=None,std_config='/etc/oidc-proxy/config.yml'):
        self.__cfg = {"openid_providers" : {}, "proxy" : {}, "services" : {}, 'access_control' : {} }
        # read fallback
        with importlib.resources.path('resources','config.yml') as config_path:
            self.read_file(config_path)

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

    def __getattr__(self,name):
        if name == "cfg":
            return self.__cfg
        if name in self.__cfg.keys():
            return self.__cfg[name]

    def print_sample_config(self):
        with importlib.resources.path('resources','config.yml') as config_path:
            with open(config_path, 'r') as fp:
                print(fp.read())

    def check_config(self):
        # there needs to be three keys in the config
        cfg_keys = set(['openid_providers','proxy', 'services', 'access_control'])
        if cfg_keys != set(self.__cfg.keys()):
            raise ConfigError("Only top-level keys allowed are: %s" % cfg_keys)

    def merge_config(self,new_cfg):
        # merge new_cfg in self.__cfg
        for key in new_cfg:
            if key in ['services', 'openid_providers', 'access_control']:
                self.__cfg[key] = new_cfg[key]
            else:
                self.__cfg[key].update(new_cfg[key])


    def read_file(self, filepath):
        with open(filepath, 'r') as ymlfile:
            new_cfg = yaml.safe_load(ymlfile)
        self.merge_config(new_cfg)

    def print_config(self):
        print(self.__cfg)


if __name__ == "__main__":
    cfg = Config()
    cfg.check_config()
    #    cfg.read_file("oidcproxy/config2.yml")
    cfg.print_config()
