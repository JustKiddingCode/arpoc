from dataclasses import dataclass, field
from typing import Any

import collections
import heapq

import time


@dataclass(order=True)
class CacheItem:
    timestamp: int
    item: Any = field(compare=False)


class Cache(collections.UserDict):
    def __init__(self):
        super().__init__({})
        self.__valid = []

    def expire(self):
        while len(
                self.__valid) > 0 and self.__valid[0].timestamp < time.time():
            elem = heapq.heappop(self.__valid)
            if elem.item in self.data:
                del self.data[elem.item]

    def put(self, key, data, valid):
        self.expire()
        if key in self.data:
            raise Exception
        self.data[key] = data
        heapq.heappush(self.__valid, CacheItem(valid, key))

    def __getitem__(self, key):
        self.expire()
        return self.data[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
