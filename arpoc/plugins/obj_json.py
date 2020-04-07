from typing import Any, Dict

import requests

from ._lib import ObjectSetter


class obj_json(ObjectSetter):
    """ Calls a url, parses the json it gets and returns the dictionary """
    name = "jsonsetter"

    def __init__(self, cfg: Dict) -> None:
        self.cfg = cfg

    def run(self, data: Dict) -> Any:
        resp = requests.get(url=self.cfg['url'], params=data)
        resp_data = resp.json()
        data.update(resp_data)
        return data
