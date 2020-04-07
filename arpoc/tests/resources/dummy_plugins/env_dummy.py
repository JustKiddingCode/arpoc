from typing import Any

from arpoc.plugins import _lib


class DummyEnv(_lib.EnvironmentAttribute):
    """ Returns the current time in HH:MM:SS format """

    target = "dummy"

    @staticmethod
    def run() -> Any:
        return True
