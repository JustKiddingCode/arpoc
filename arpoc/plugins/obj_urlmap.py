from typing import Any, Dict
import re
import logging

from ._lib import ObjectSetter

LOGGING = logging.getLogger(__name__)


#pylint: disable=too-few-public-methods
class ObjUrlmap(ObjectSetter):
    """ Maps a path based on the regex supplied in configuration """
    name = "urlmap"

    def __init__(self, cfg: Dict) -> None:
        super().__init__(cfg)
        self.cfg = cfg

    def run(self, data: Dict) -> Any:
        # must change data dict
        regexes = self.cfg['mappings']
        for regex in regexes:
            try:
                match_object = re.match(regex, data['path'])
                if match_object is not None:
                    LOGGING.debug("Matched path, dict %s",
                                  match_object.groupdict())
                    data.update(match_object.groupdict())
            except re.error:
                LOGGING.info("Failed to parse regex %s", regex)
        return data
