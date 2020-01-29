"""
Conflict Resolution Module for OIDC Proxy.

Provides functions to use to evaluate how Policies and Policy Sets
combine the results of the rules they use.

Every resolver should inherit from ConflictResolution.

"""
from enum import Enum

from .common import Effects


class ConflictResolution:
    """
    Base Class for all ConflictResolution Objects.
    Normally a child-class should just implement the update method
    """
    def __init__(self):
        self._results = dict()
        self._break = False
        self._effect = None

    def __str__(self):
        return "Effect: {}\nBreak:{}\nResults:{}".format(
            self._results, self._break, self._effect)

    def update(self, entity_id, result):
        assert isinstance(
            result, Effects
        ) or result == None, "type was: %s, expected: None, Effects" % type(
            result)
        self._results[entity_id] = result

    def check_break(self):
        return self._break

    def get_effect(self):
        return self._effect


class AnyOfAny(ConflictResolution):
    """ Resolver that grants access as soon as a returned True """
    def update(self, entity_id, result):
        super().update(entity_id, result)
        if self._effect == None and result == Effects.DENY:
            self._effect = Effects.DENY
        if result == Effects.GRANT:
            self._break = True
            self._effect = Effects.GRANT


class And(ConflictResolution):
    """ Resolver that grants access only if all rules returned True """
    def update(self, entity_id, result):
        super().update(entity_id, result)
        if result == Effects.GRANT and self._effect == None:
            self._effect = Effects.GRANT
        if result == Effects.DENY:
            self._break = True
            self._effect = Effects.DENY


cr_switcher = {
    "ANY": AnyOfAny,
    "AND": And,
}
