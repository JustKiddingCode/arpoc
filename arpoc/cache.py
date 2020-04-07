""" Cache Module for OIDCPROXY"""

import collections
import heapq
import time
from dataclasses import dataclass, field
from typing import Any, List

import arpoc.utils

@dataclass(order=True)
class CacheItem:
    """ CacheItem -- A item in the Cache
        timestamp: An Unix Timestamp in seconds since beginning of the epoch.
        item: The Item
    """
    timestamp: int
    item: Any = field(compare=False)


class Cache(collections.UserDict):
    """ The cache. On Every action (get, put) a clean up procedure is triggered """
    def __init__(self) -> None:
        super().__init__({})
        self.__valid: List = []

    def expire(self) -> None:
        """ Deletes invalid entries from the cache"""
        while len(
                self.__valid) > 0 and self.__valid[0].timestamp < arpoc.utils.now():
            elem = heapq.heappop(self.__valid)
            if elem.item in self.data:
                del self.data[elem.item]

    def put(self, key: str, data: Any, valid: int) -> None:
        """ Inserts the element <data> with <key> into the cache. 
            Expiration time <valid>.
        """
        self.expire()
        if key in self.data:
            raise Exception
        self.data[key] = data
        heapq.heappush(self.__valid, CacheItem(valid, key))

    def __getitem__(self, key: str) -> Any:
        self.expire()
        return self.data[key]

    def get(self, key: str, default: Any = None) -> Any:
        """ Returns the element in the cache referenced by key.
            If no element exists with the key, <default> is returned
        """
        try:
            return self[key]
        except KeyError:
            return default
