""""
Access Control Module for OIDC Proxy

"""
import os
import json

from abc import ABC
from enum import Enum
from typing import List, Union, Dict, Type, Any, Tuple, Callable, Optional, ClassVar, MutableMapping

import logging

from dataclasses import dataclass, InitVar

import lark.exceptions

from .conflict_resolution import *

#import oidcproxy
#import oidcproxy.ac
import oidcproxy.ac.common as common
import oidcproxy.ac.parser as parser

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger(__name__)

#__all__ = ["conflict_resolution", "common", "parser"]


@dataclass
class AC_Entity(ABC):
    """ Class for all access control entities (policy sets, policies, rules"""
    container: ClassVar[Optional['AC_Container']]

    entity_id: str
    target: str
    description: str

    def __str__(self) -> str:
        return "Entity: {}\nTarget: {}\nDescription: {}\n".format(
            self.entity_id, self.target, self.description)

    def evaluate(self, context: Dict, evaluation_cache: Dict
                 ) -> Tuple[Union[None, common.Effects], List[str]]:
        pass

    def _check_match(self, context: Dict[str, Dict]) -> bool:
        pass


@dataclass
class Policy_Set(AC_Entity):
    conflict_resolution: str
    policy_sets: List[str]
    policies: List[str]

    def __str__(self) -> str:
        basic = super().__str__()
        return "{}Conflict Resolution: {}\nPolicy Sets:{}\nPolicies: {}".format(
            basic, self.conflict_resolution, self.policy_sets, self.policies)

    def evaluate(self, context: Dict, evaluation_cache: Dict
                 ) -> Tuple[Union[None, common.Effects], List[str]]:
        """ Evaluate Policy Set"""
        missing_attr: List[str] = []
        evaluation_cache = evaluation_cache if evaluation_cache != None else dict(
        )
        try:
            cr = cr_switcher[self.conflict_resolution]()
        except KeyError:
            raise NotImplementedError(
                "Conflict Resolution %s is not implemented" %
                self.conflict_resolution)

        if self._check_match(context):
            assert self.container is not None
            for policy_set_id in self.policy_sets:
                if policy_set_id not in evaluation_cache:
                    LOGGER.debug("Considering policy set %s", policy_set_id)
                    try:
                        result, missing = self.container.policy_sets[
                            policy_set_id].evaluate(context, evaluation_cache)
                    except KeyError:
                        LOGGER.debug(
                            "{} requested ps {}, but was not found in container",
                            self.entity_id, policy_set_id)
                        raise
                    missing_attr += missing
                    evaluation_cache[policy_set_id] = result
                    cr.update(policy_set_id, result)

                    if cr.check_break():
                        break

            for policy_id in self.policies:
                if policy_id not in evaluation_cache:
                    LOGGER.debug("Considering policy %s", policy_id)
                    try:
                        result, missing = self.container.policies[
                            policy_id].evaluate(context, evaluation_cache)
                    except KeyError:
                        LOGGER.debug(
                            "{} requested p {}, but was not found in container",
                            self.entity_id, policy_id)
                        raise

                    missing_attr += missing
                    evaluation_cache[policy_id] = result
                cr.update(policy_id, evaluation_cache[policy_id])

                if cr.check_break():
                    break
            LOGGER.debug(evaluation_cache)
            LOGGER.debug(cr.get_effect())
        return cr.get_effect(), missing_attr

    def _check_match(self, context: Dict) -> bool:
        return parser.check_target(self.target, context)


@dataclass
class Policy(AC_Entity):
    conflict_resolution: str
    rules: List[str]

    def __str__(self) -> str:
        basic = super().__str__()
        return "{}Conflict Resolution: {}\nRules{}\n".format(
            basic, self.conflict_resolution, self.rules)

    def evaluate(self, context: Dict, evaluation_cache: Dict
                 ) -> Tuple[Union[None, common.Effects], List[str]]:
        evaluation_cache = evaluation_cache if evaluation_cache != None else dict(
        )
        try:
            cr = cr_switcher[self.conflict_resolution]()
        except KeyError:
            raise NotImplementedError(
                "Conflict Resolution %s is not implemented" %
                self.conflict_resolution)
        LOGGER.debug("policy %s before evaluation: %s", self.entity_id,
                     cr.get_effect())

        missing_attr: List[str] = []

        if self._check_match(context):
            assert self.container is not None
            for rules_id in self.rules:
                if rules_id not in evaluation_cache:
                    LOGGER.debug("Considering rule %s", rules_id)
                    try:
                        effect, missing = self.container.rules[
                            rules_id].evaluate(context, evaluation_cache)
                    except KeyError:
                        LOGGER.debug(
                            "{} requested r {}, but was not found in container",
                            self.entity_id, rules_id)
                        raise

                    missing_attr += missing
                    evaluation_cache[rules_id] = effect
                    LOGGER.debug(evaluation_cache[rules_id])
                cr.update(rules_id, evaluation_cache[rules_id])

                if cr.check_break():
                    break
        LOGGER.debug("policy %s evaluation_cache %s", self.entity_id,
                     evaluation_cache)
        LOGGER.debug("policy %s evaluated to %s", self.entity_id,
                     cr.get_effect())
        return (cr.get_effect(), missing_attr)

    def _check_match(self, context: Dict[str, Dict]) -> bool:
        return parser.check_target(self.target, context)


@dataclass
class Rule(AC_Entity):
    condition: str
    effect: InitVar[str]

    def __post_init__(self, effect: str) -> None:
        self.effect = common.Effects[effect]

    def __str__(self) -> str:
        basic = super().__str__()
        return "{}Condition: {}\nEffect: {}".format(basic, self.condition,
                                                    self.effect)

    def evaluate(self, context: Dict, evaluation_cache: Dict
                 ) -> Tuple[Union[None, common.Effects], List[str]]:
        evaluation_cache = evaluation_cache if evaluation_cache != None else dict(
        )
        try:
            if self._check_match(context):
                if self._check_condition(context):
                    return self.effect, []
                return common.Effects(not self.effect), []
        except lark.exceptions.VisitError as e:
            if e.orig_exc.__class__ == parser.SubjectAttributeMissing:
                print(e.orig_exc.attr)
                print(e.__class__)
                print(e.__traceback__)
                return (None, [e.orig_exc.attr])
            raise
        return None, []

    def _check_condition(self, context: Dict[str, Dict]) -> bool:
        return parser.check_condition(self.condition, context)

    def _check_match(self, context: Dict[str, Dict]) -> bool:
        return parser.check_target(self.target, context)


class AC_Container:
    def __init__(self) -> None:

        self.policies: Dict[str, Policy] = dict()
        self.policy_sets: Dict[str, Policy_Set] = dict()
        self.rules: Dict[str, Rule] = dict()

    def __str__(self) -> str:
        string = ""
        for policy_key, policy_val in self.policies.items():
            string += "\n{}\n{}".format(str(policy_key), str(policy_val))
        for ps_key, ps_val in self.policy_sets.items():
            string += "\n{}\n{}".format(str(ps_key), str(ps_val))
        for rule_key, rule_val in self.rules.items():
            string += "\n{}\n{}".format(str(rule_key), str(rule_val))

        return string

    def load_file(self, filename: str) -> None:
        with open(filename) as f:
            data = json.load(f)
            for entity_id, definition in data.items():
                self.add_entity(entity_id, definition)

    def load_dir(self, path: str) -> None:
        import glob
        for f in glob.glob(path + "/*.json"):
            self.load_file(f)

    def evaluate_by_entity_id(self,
                              entity_id: str,
                              context: Dict[str, MutableMapping],
                              evaluation_cache: Optional[Dict] = None
                              ) -> Tuple[Optional[common.Effects], List[str]]:
        if evaluation_cache is None:
            evaluation_cache = dict()

        if entity_id in evaluation_cache:
            return evaluation_cache[entity_id], []
        # Effect, Missing
        try:
            effect, missing = self.policy_sets[entity_id].evaluate(
                context, evaluation_cache)
        except KeyError:
            LOGGER.debug("Requested ps {}, but was not found in container",
                         entity_id)
            raise

        evaluation_cache[entity_id] = effect
        assert isinstance(
            effect, common.Effects
        ) or effect == None, "effect is %s" % effect.__class__
        assert isinstance(missing, list)
        return (effect, missing)

    def add_entity(self, entity_id: str, definition: Dict[str, str]) -> None:
        #        if AC_Entity.container is None:
        #    AC_Entity.container = self
        switcher = {"Policy": Policy, "PolicySet": Policy_Set, "Rule": Rule}
        switcher_dict: Dict[str, Dict[str, Any]] = {
            "Policy": self.policies,
            "PolicySet": self.policy_sets,
            "Rule": self.rules
        }

        cleaner = {
            "Description": "description",
            "Target": "target",
            "PolicySets": "policy_sets",
            "Policies": "policies",
            "Rules": "rules",
            "Resolver": "conflict_resolution",
            "Effect": "effect",
            "Condition": "condition",
            "Type": "--filter--"
        }
        kwargs = {
            cleaner[key]: value
            for (key, value) in definition.items()
            if cleaner.get(key) != "--filter--"
        }
        #        print(kwargs)
        LOGGER.debug('Creating %s with parameters %s', definition['Type'],
                     str(kwargs))
        try:
            obj: AC_Entity = switcher[definition['Type']](entity_id, **kwargs)
            obj.container = self

            obj_container: Dict[str, AC_Entity] = switcher_dict[
                definition['Type']]
            obj_container[entity_id] = obj
        except KeyError:
            LOGGER.debug("Cannot find ac entity type or cannot initialize")
            raise


container = AC_Container()
