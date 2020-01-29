""""
Access Control Module for OIDC Proxy

"""
import os
import json

from abc import ABC
from enum import Enum
from typing import List, Union, Dict, Type, Any, Tuple

import logging

import lark.exceptions

from .conflict_resolution import *

import oidcproxy.ac.common
import oidcproxy.ac.parser as parser

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger(__name__)

#__all__ = ["conflict_resolution", "common", "parser"]


class AC_Entity(ABC):
    """ Class for all access control entities (policy sets, policies, rules"""
    container: AC_Container

    def __init__(self, entity_id: str, target: str, description: str) -> None:
        self.entity_id = entity_id
        self.target = target
        self.description = description

    def __str__(self):
        return "Entity: {}\nTarget: {}\nDescription: {}\n".format(
            self.entity_id, self.target, self.description)

    def evaluate(
            self, context: Dict, evaluation_cache: Dict
    ) -> Tuple[Union[None, oidcproxy.ac.common.Effects], List[str]]:
        pass

    def _check_match(self, context):
        pass


class Policy_Set(AC_Entity):
    def __init__(self, entity_id, target, description, conflict_resolution,
                 policy_sets, policies):
        super().__init__(entity_id, target, description)
        self.conflict_resolution = conflict_resolution
        self.policy_sets = policy_sets
        self.policies = policies

    def __str__(self):
        basic = super().__str__()
        return "{}Conflict Resolution: {}\nPolicy Sets:{}\nPolicies: {}".format(
            basic, self.conflict_resolution, self.policy_sets, self.policies)

    def evaluate(
            self, context: Dict, evaluation_cache: Dict
    ) -> Tuple[Union[None, oidcproxy.ac.common.Effects], List[str]]:
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

    def _check_match(self, context):
        return parser.check_target(self.target, context)


class Policy(AC_Entity):
    def __init__(self, entity_id, target, description, conflict_resolution,
                 rules):
        super().__init__(entity_id, target, description)
        self.conflict_resolution = conflict_resolution
        LOGGER.debug(self.conflict_resolution)
        self.rules = rules

    def __str__(self):
        basic = super().__str__()
        return "{}Conflict Resolution: {}\nRules{}\n".format(
            basic, self.conflict_resolution, self.rules)

    def evaluate(
            self, context: Dict, evaluation_cache: Dict
    ) -> Tuple[Union[None, oidcproxy.ac.common.Effects], List[str]]:
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

    def _check_match(self, context):
        return parser.check_target(self.target, context)


class Rule(AC_Entity):
    def __init__(self, entity_id: str, target: str, description: str,
                 condition: str, effect: str) -> None:
        super().__init__(entity_id, target, description)
        self.condition = condition
        self.effect = oidcproxy.ac.common.Effects[effect]

    def __str__(self):
        basic = super().__str__()
        return "{}Condition: {}\nEffect: {}".format(basic, self.condition,
                                                    self.effect)

    def evaluate(
            self, context: Dict, evaluation_cache: Dict
    ) -> Tuple[Union[None, oidcproxy.ac.common.Effects], List[str]]:
        evaluation_cache = evaluation_cache if evaluation_cache != None else dict(
        )
        try:
            if self._check_match(context):
                if self._check_condition(context):
                    return self.effect, []
                return oidcproxy.ac.common.Effects(not self.effect), []
        except lark.exceptions.VisitError as e:
            if e.orig_exc.__class__ == parser.SubjectAttributeMissing:
                print(e.orig_exc.attr)
                print(e.__class__)
                print(e.__traceback__)
                return (None, [e.orig_exc.attr])
            raise
        return None, []

    def _check_condition(self, context):
        return parser.check_condition(self.condition, context)

    def _check_match(self, context):
        return parser.check_target(self.target, context)


class AC_Container:
    def __init__(self) -> None:

        self.policies: Dict[str, Policy] = dict()
        self.policy_sets: Dict[str, Policy_Set] = dict()
        self.rules: Dict[str, Rule] = dict()

    def __str__(self):
        string = ""
        for key, val in self.policies.items():
            string += "\n{}\n{}".format(str(key), str(val))
        for key, val in self.policy_sets.items():
            string += "\n{}\n{}".format(str(key), str(val))
        for key, val in self.rules.items():
            string += "\n{}\n{}".format(str(key), str(val))

        return string

    def load_file(self, filename):
        with open(filename) as f:
            data = json.load(f)
            for entity_id, definition in data.items():
                self.add_entity(entity_id, definition)

    def load_dir(self, path):
        import glob
        for f in glob.glob(path + "/*.json"):
            self.load_file(f)

    def evaluate_by_entity_id(self, entity_id, context, evaluation_cache=None):
        evaluation_cache = evaluation_cache if evaluation_cache != None else dict(
        )

        if entity_id in evaluation_cache:
            return evaluation_cache[entity_id], []
        # Effect, Missing
        effect, missing = self.policy_sets.get(entity_id, None).evaluate(
            context, evaluation_cache)

        evaluation_cache[entity_id] = effect
        assert isinstance(
            effect, oidcproxy.ac.common.Effects
        ) or effect == None, "effect is %s" % effect.__class__
        assert isinstance(missing, list)
        return (effect, missing)

    def add_entity(self, entity_id, definition: Dict[str, str]):
        if AC_Entity.container == None:
            AC_Entity.container = self
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

            obj_container: Dict[str, AC_Entity] = switcher_dict[
                definition['Type']]
            obj_container[entity_id] = obj
        except KeyError:
            LOGGER.debug("Cannot find ac entity type or cannot initialize")
            raise


container = AC_Container()
