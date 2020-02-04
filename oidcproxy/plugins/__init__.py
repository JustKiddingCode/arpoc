# import all modules in this directory,
# from user ted @ https://stackoverflow.com/a/59054776
import importlib
from pathlib import Path
from typing import Dict, Callable, Optional


from queue import PriorityQueue
import collections
from dataclasses import dataclass, field
from typing import Any
import os

from . import _lib
import oidcproxy.config as config
from oidcproxy.exceptions import DuplicateKeyError

import logging
LOGGING = logging.getLogger()

__all__ = [
    f".{f.stem}" for f in Path(__file__).parent.glob("*.py")
    if "__" not in f.stem
]

plugins = []

def import_plugins():
    global plugins
    if config.cfg:
        for plugin_dir in config.cfg.proxy.plugin_dirs:
            for entry in os.listdir(plugin_dir):
                wholepath = os.path.join(plugin_dir, entry)
                if os.path.isfile(wholepath):
                    module_name = os.path.splitext(entry)[0]
                    LOGGING.debug("module_name: %s", module_name)
                    LOGGING.debug("wholepath: %s", wholepath)
                    if wholepath.endswith(".py"):
                        spec = importlib.util.spec_from_file_location(module_name, wholepath)
                        module = importlib.util.module_from_spec(spec)
                        plugins.append(module)
                        spec.loader.exec_module(module)


@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any = field(compare=False)


class ObjectDict(collections.UserDict):
    def __init__(self, service_name: str,
                 initialdata: Optional[Dict] = None) -> None:
        if not initialdata:
            initialdata = {}
        super().__init__(initialdata)
        self._executed_flag = False
        # sort "plugins" according to priority
        self._queue: PriorityQueue = PriorityQueue()
        assert config.cfg is not None
        assert isinstance(config.cfg.services, dict)
        for plugin in _lib.ObjectSetter.__subclasses__():
            LOGGING.debug("Found object setter %s, name: %s", plugin, plugin.name)
            priority = 100
            if plugin.name in config.cfg.services[service_name][
                    'objectsetters']:
                plugin_cfg = config.cfg.services[service_name][
                    'objectsetters'][plugin.name]
                if plugin_cfg['enable']:
                    # give configuration to the plugin and set priority
                    if priority in plugin_cfg:
                        priority = plugin_cfg['priority']
                    item = PrioritizedItem(priority, plugin(plugin_cfg))
                    self._queue.put(item)

    def get(self, key: str, default: Any = None) -> Any:
        if key in self.data:
            return self.data[key]

        if not self._executed_flag:
            while not self._queue.empty():
                self._queue.get().item.run(self.data)
            if key in self.data:
                return self.data[key]
        return default

    def __getitem__(self, key: str) -> Any:
        elem = self.get(key)
        if elem == None:
            raise KeyError
        return elem


class EnvironmentDict(collections.UserDict):
    def __init__(self, initialdata: Dict = None) -> None:
        if not initialdata:
            initialdata = {}
        super().__init__(initialdata)
        self.__get_env_attr_dict()

    def __get_env_attr_dict(self) -> Dict[str, Callable]:
        d: Dict[str, Callable] = dict()
        for plugin in _lib.EnvironmentAttribute.__subclasses__():
            if plugin.target in d.keys():
                DuplicateKeyError("key {} is already in target in a plugin".format(
                    plugin.target))
            d[plugin.target] = plugin.run

        self._getter = d

    def get(self, key: str, default: Any = None) -> Any:
        if key in self.data:
            return self.data[key]
        if key in self._getter:
            self.data[key] = self._getter[key]()
            return self.data[key]
        return default

    def __getitem__(self, key: str) -> Any:
        elem = self.get(key)
        if elem == None:
            raise KeyError
        return elem
