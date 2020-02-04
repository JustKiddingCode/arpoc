import requests

from oidcproxy.plugins._lib import ObjectSetter

from typing import Any, Dict


class obj_dummy(ObjectSetter):
    """ Calls a url, parses the json it gets and returns the dictionary """
    name = "dummysetter"

    def __init__(self, cfg: Dict) -> None:
        self.cfg = cfg

    def run(self, data: Dict) -> Any:
        data["dummy"] = True
