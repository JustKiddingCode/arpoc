from abc import ABC

from typing import Dict, Any


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
