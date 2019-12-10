""""
Access Control Module for OIDC Proxy

"""

import json

from abc import ABC
from enum import Enum

import logging

from .conflict_resolution import *
from .common import *
from .parser import check_condition, check_target

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger(__name__)

__all__ = ["conflict_resolution", "common", "parser"]


class AC_Entity(ABC):
    def __init__(self, entity_id, target, description):
        self.entity_id = entity_id
        self.target = target
        self.description = description

    def __str__(self):
        return "Entity: {}\nTarget: {}\nDescription: {}\n".format(
            self.entity_id, self.target, self.description)

    def evaluate(self, context, evaluation_cache):
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

    def evaluate(self, context, evaluation_cache=None):
        """ Evaluate Policy Set"""
        evaluation_cache = evaluation_cache or dict()
        cr = cr_switcher.get(self.conflict_resolution, None)()
        if self._check_match(context):
            for policy_set_id in self.policy_sets:
                if policy_set_id not in evaluation_cache:
                    LOGGER.debug("Considering policy set %s", policy_set_id)
                    result = container.policy_sets.get(policy_set_id).evaluate(
                        context, evaluation_cache)
                    evaluation_cache[policy_set_id] = result
                    cr.update(policy_set_id, result)

                    if cr.check_break():
                        break

            for policy_id in self.policies:
                if policy_id not in evaluation_cache:
                    LOGGER.debug("Considering policy %s", policy_id)
                    result = container.policies.get(policy_id).evaluate(
                        context, evaluation_cache)
                    evaluation_cache[policy_id] = result
                cr.update(policy_id, evaluation_cache[policy_id])

                if cr.check_break():
                    break
            LOGGER.debug(evaluation_cache)
            LOGGER.debug(cr.get_effect())
        return cr.get_effect()

    def _check_match(self, context):
        return check_target(self.target, context)


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

    def evaluate(self, context, evaluation_cache=None):
        evaluation_cache = evaluation_cache or dict()
        cr = cr_switcher.get(self.conflict_resolution, None)()
        LOGGER.debug("policy %s before evaluation: %s", self.entity_id,
                     cr.get_effect())
        if self._check_match(context):
            for rules_id in self.rules:
                if rules_id not in evaluation_cache:
                    LOGGER.debug("Considering rule %s", rules_id)
                    result = container.rules.get(rules_id).evaluate(
                        context, evaluation_cache)
                    evaluation_cache[rules_id] = result
                cr.update(rules_id, evaluation_cache[rules_id])

                if cr.check_break():
                    break
        LOGGER.debug("policy %s evaluation_cache %s", self.entity_id,
                     evaluation_cache)
        LOGGER.debug("policy %s evaluated to %s", self.entity_id,
                     cr.get_effect())
        return cr.get_effect()

    def _check_match(self, context):
        return check_target(self.target, context)


class Rule(AC_Entity):
    def __init__(self, entity_id, target, description, condition, effect):
        super().__init__(entity_id, target, description)
        self.condition = condition
        self.effect = Effects[effect]

    def __str__(self):
        basic = super().__str__()
        return "{}Condition: {}\nEffect: {}".format(basic, self.condition,
                                                    self.effect)

    def evaluate(self, context, evaluation_cache=None):
        evaluation_cache = evaluation_cache or dict()
        if self._check_match(context):
            if self._check_condition(context):
                return self.effect
            else:
                return Effects(not self.effect)

    def _check_condition(self, context):
        return check_condition(self.condition, context)

    def _check_match(self, context):
        return check_target(self.target, context)


class AC_Container:
    def __init__(self):

        self.policies = dict()
        self.policy_sets = dict()
        self.rules = dict()

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

    def evaluate_by_entity_id(self, entity_id, context):
        LOGGER.debug(context)
        return self.policy_sets.get(entity_id, None).evaluate(context)

    def add_entity(self, entity_id, definition):
        switcher = {"Policy": Policy, "PolicySet": Policy_Set, "Rule": Rule}
        switcher_dict = {
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
            cleaner.get(key): value
            for (key, value) in definition.items()
            if cleaner.get(key) != "--filter--"
        }
        #        print(kwargs)
        LOGGER.debug('Creating %s with parameters %s', definition['Type'],
                     str(kwargs))
        obj = switcher.get(definition['Type'], None)(entity_id, **kwargs)
        switcher_dict.get(definition['Type'], None)[entity_id] = obj


container = AC_Container()

policies_path = pkg_resources.resource_filename(
    __name__, os.path.join(os.pardir, 'resources', 'acl', 'policies.json'))
rules_path = pkg_resources.resource_filename(
    __name__, os.path.join(os.pardir, 'resources', 'acl', 'prules.json'))
ps_path = pkg_resources.resource_filename(
    __name__, os.path.join(os.pardir, 'resources', 'acl', 'policysets.json'))
container.load_file(policies_path)
container.load_file(rules_path)
container.load_file(ps_path)
