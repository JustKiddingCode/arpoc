"""
Conflict Resolution Module for ARPOC.

Provides functions to use to evaluate how Policies and Policy Sets
combine the results of the rules they use.

Every resolver should inherit from ConflictResolution.

"""
from enum import Enum
from typing import Callable, Dict, Optional

from .common import Effects


class ConflictResolution:
    """
    Base Class for all ConflictResolution Objects.
    Normally a child-class should just implement the update method
    """
    def __init__(self) -> None:
        self._results: Dict[str, Optional[Effects]] = dict()
        self._break: bool = False
        self._effect: Optional[Effects] = None

    def __str__(self) -> str:
        return "Effect: {}\nBreak:{}\nResults:{}".format(
            self._results, self._break, self._effect)

    def update(self, entity_id: str, result: Optional[Effects]) -> None:
        assert isinstance(
            result, Effects
        ) or result == None, "type was: %s, expected: None, Effects" % type(
            result)
        self._results[entity_id] = result

    def check_break(self) -> bool:
        return self._break

    def get_effect(self) -> Optional[Effects]:
        return self._effect


class AnyOfAny(ConflictResolution):
    """ Resolver that grants access as soon as a returned True """
    def update(self, entity_id: str, result: Optional[Effects]) -> None:
        super().update(entity_id, result)
        if self._effect == None and result == Effects.DENY:
            self._effect = Effects.DENY
        if result == Effects.GRANT:
            self._break = True
            self._effect = Effects.GRANT


class And(ConflictResolution):
    """ Resolver that grants access only if all rules returned True """
    def update(self, entity_id: str, result: Optional[Effects]) -> None:
        super().update(entity_id, result)
        if result == Effects.GRANT and self._effect == None:
            self._effect = Effects.GRANT
        if result == Effects.DENY:
            self._break = True
            self._effect = Effects.DENY


cr_switcher: Dict[str, Callable] = {
    "ANY": AnyOfAny,
    "AND": And,
}
