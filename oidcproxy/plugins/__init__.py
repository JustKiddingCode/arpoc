# import all modules in this directory,
# from user ted @ https://stackoverflow.com/a/59054776
from importlib import import_module
from pathlib import Path

from . import _lib

from queue import PriorityQueue

import config

__all__ = [
    import_module(f".{f.stem}", __package__)
    for f in Path(__file__).parent.glob("*.py") if "__" not in f.stem
]


class DuplicateKeyError(Exception):
    pass


def get_env_attr_dict():
    d = dict()
    for plugin in _lib.EnvironmentAttribute.__subclasses__():
        if plugin.target in d.keys():
            DuplicateKeyError("key {} is already in target in a plugin".format(
                plugin.target))
        d[plugin.target] = plugin.run

    return d


import collections
from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)



class ObjectDict(collections.UserDict):
    def __init__(self, initialdata=None):
        if not initialdata:
            initialdata = {}
        super().__init__(initialdata)
        self._executed_flag = False
        # sort "plugins" according to priority
        self._queue = PriorityQueue()
#        for plugin in _lib.ObjectAttribute.__subclasses__():
#            priority = 100
#            # we need the configuration here.
#            if plugin.name in config.cfg['objectsetters']:
#                # give configuration to the plugin and set priority
#                if priority in config.cfg['objectsetters']['name']:
#                    priority = config.cfg['objectsetters']['name']['priority']
#            item = PrioritizedItem(priority, plugin)
#            self._queue.put(item)



    def get(self, key, default=None):
        return None
        if key in self.data:
            return self.data[key]
        if key in self._getter:
            self.data[key] = self._getter[key]()
            return self.data[key]
        return default

    def __getitem__(self, key):
        elem = self.get(key)
        if elem == None:
            raise KeyError
        return elem


class EnvironmentDict(collections.UserDict):
    def __init__(self, initialdata=None):
        if not initialdata:
            initialdata = {}
        super().__init__(initialdata)
        self._getter = get_env_attr_dict()

    def get(self, key, default=None):
        if key in self.data:
            return self.data[key]
        if key in self._getter:
            self.data[key] = self._getter[key]()
            return self.data[key]
        return default

    def __getitem__(self, key):
        elem = self.get(key)
        if elem == None:
            raise KeyError
        return elem
