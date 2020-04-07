from typing import Any, Dict

import requests

from arpoc.plugins._lib import ObjectSetter


class obj_dummy(ObjectSetter):
    """ Calls a url, parses the json it gets and returns the dictionary """
    name = "dummysetter"

    def __init__(self, cfg: Dict) -> None:
        self.cfg = cfg

    def run(self, data: Dict) -> Any:
        data["dummy"] = True
