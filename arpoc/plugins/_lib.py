from abc import ABC
from typing import Any, Dict, Optional
import collections.abc

import arpoc.ac.common


class EnvironmentAttribute(ABC):
    target = ""

    @staticmethod
    def run() -> Any:
        return None


class ObjectSetter(ABC):
    name = ""

    def __init__(self, cfg: Dict) -> None:
        pass

    def run(self, data: Dict) -> Any:
        return None


class Obligation(ABC):
    name = ""

    def __init__(self) -> None:
        pass

    def run(self, effect: Optional[arpoc.ac.common.Effects], context: Dict,
            cfg: Dict) -> bool:
        pass


def deep_dict_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = deep_dict_update(d.get(k, {}), v)
        else:
            if v is None:
                del d[k]
            else:
                d[k] = v

    return d
