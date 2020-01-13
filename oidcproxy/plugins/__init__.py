# import all modules in this directory,
# from user ted @ https://stackoverflow.com/a/59054776
from importlib import import_module
from pathlib import Path

from . import _lib

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
