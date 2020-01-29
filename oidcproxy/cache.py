import collections
import heapq
import time
from dataclasses import dataclass, field
from typing import Any, List


@dataclass(order=True)
class CacheItem:
    timestamp: int
    item: Any = field(compare=False)


class Cache(collections.UserDict):
    def __init__(self) -> None:
        super().__init__({})
        self.__valid: List = []

    def expire(self) -> None:
        while len(
                self.__valid) > 0 and self.__valid[0].timestamp < time.time():
            elem = heapq.heappop(self.__valid)
            if elem.item in self.data:
                del self.data[elem.item]

    def put(self, key, data, valid) -> None:
        self.expire()
        if key in self.data:
            raise Exception
        self.data[key] = data
        heapq.heappush(self.__valid, CacheItem(valid, key))

    def __getitem__(self, key) -> Any:
        self.expire()
        return self.data[key]

    def get(self, key, default=None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default
