from abc import ABC
from typing import Any, Dict, Optional

import oidcproxy.ac.common

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

    def run(self, effect : Optional[oidcproxy.ac.common.Effects], context: Dict, cfg : Dict) -> bool:
        pass
