# import all modules in this directory,
# from user ted @ https://stackoverflow.com/a/59054776
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Callable, Optional, List, Type, TypeVar

from queue import PriorityQueue
import collections
from dataclasses import dataclass, field
from typing import Any
import os

from collections.abc import Mapping

from . import _lib
from arpoc.ac.common import Effects
import arpoc.config as config
from arpoc.exceptions import DuplicateKeyError

import logging
LOGGING = logging.getLogger()

__all__ = [
    f"{f.stem}" for f in Path(__file__).parent.glob("*.py")
    if not str(f.stem).startswith("_")
]

for m in __all__:
    importlib.import_module("." + m, "arpoc.plugins")

plugins = []


def import_plugins() -> None:
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
                        spec = importlib.util.spec_from_file_location(
                            module_name, wholepath)
                        if spec is None or not isinstance(
                                spec.loader, importlib.abc.Loader):
                            raise RuntimeError("Failed to load %s", wholepath)
                        module = importlib.util.module_from_spec(spec)
                        plugins.append(module)
                        spec.loader.exec_module(module)


@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any = field(compare=False)


class ObjectDict(collections.UserDict):
    def __init__(self,
                 objsetter: Dict,
                 initialdata: Optional[Dict] = None) -> None:
        if not initialdata:
            initialdata = {}
        super().__init__(initialdata)
        self._executed_flag = False
        # sort "plugins" according to priority
        self._queue: PriorityQueue = PriorityQueue()
        for plugin in _lib.ObjectSetter.__subclasses__():
            LOGGING.debug("Found object setter %s, name: %s", plugin,
                          plugin.name)
            if plugin.name in objsetter:
                plugin_cfg = objsetter[plugin.name]
                if plugin_cfg['enable']:
                    # give configuration to the plugin and set priority
                    priority = plugin_cfg[
                        'priority'] if 'priority' in plugin_cfg else 100
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


class ObligationsDict():
    def __init__(self) -> None:
        self.__get_obligations_dict()
        LOGGING.debug("Obligations found %s", self._obligations)

    def __get_obligations_dict(self) -> None:
        d: Dict[str, Callable] = dict()
        for plugin in _lib.Obligation.__subclasses__():
            if plugin.name in d.keys():
                DuplicateKeyError(
                    "key {} is already in target in a plugin".format(
                        plugin.name))
            d[plugin.name] = plugin.run


#        def () -> arpoc.plugins._lib.Obligation
        T = TypeVar('T', bound='_lib.Obligation')

        self._obligations: Dict[str, Callable] = d

    def run_all(self, obligations: List[str], effect: Optional[Effects],
                context: Dict, cfg: Dict) -> List[bool]:
        results: List[bool] = []
        LOGGING.debug("Obligations found %s", self._obligations)
        for key in obligations:
            obl = self.get(key)

            if obl is not None:
                obl_cfg = cfg[key] if key in cfg else {}
                results.append(obl(effect, context, obl_cfg))
            else:
                LOGGING.debug("Failed to run obligation %s", key)
                raise ValueError
        return results

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __getitem__(self, key: str) -> Any:
        return self._obligations[key]


class EnvironmentDict(collections.UserDict):
    def __init__(self, initialdata: Dict = None) -> None:
        if not initialdata:
            initialdata = {}
        super().__init__(initialdata)
        self.__get_env_attr_dict()

    def __get_env_attr_dict(self) -> None:
        d: Dict[str, Callable] = dict()
        for plugin in _lib.EnvironmentAttribute.__subclasses__():
            if plugin.target in d.keys():
                DuplicateKeyError(
                    "key {} is already in target in a plugin".format(
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
