""""
Access Control Module for ARPOC

"""
import os
import json

import traceback

from abc import ABC
from enum import Enum
from typing import List, Union, Dict, Type, Any, Tuple, Callable, Optional, ClassVar, MutableMapping

import itertools

import logging
from collections.abc import Mapping

from dataclasses import dataclass, InitVar, field

import lark.exceptions

from arpoc.exceptions import *
#import arpoc
#import arpoc.ac
import arpoc.ac.common as common
import arpoc.ac.parser as parser

from .conflict_resolution import *
#logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger(__name__)


#__all__ = ["conflict_resolution", "common", "parser"]
@dataclass
class EvaluationResult:
    missing_attr: List[str] = field(default_factory=list)
    results: Dict[str, Optional[common.Effects]] = field(default_factory=dict)
    obligations: List[Any] = field(default_factory=list)


@dataclass
class AC_Entity(ABC):
    """ Class for all access control entities (policy sets, policies, rules"""
    container: ClassVar[Optional['AC_Container']]

    entity_id: str
    target: str
    description: str
    obligations: List[str]

    def _evaluate(self, entity_id: str, getter: Dict,
                  evaluation_result: EvaluationResult, cr: ConflictResolution,
                  context: Dict) -> None:
        if entity_id not in evaluation_result.results:
            LOGGER.debug("Considering entity_id %s", entity_id)
            try:
                evaluation_result = getter[entity_id].evaluate(
                    context, evaluation_result)
            except KeyError:
                raise ACEntityMissing(entity_id)
            cr.update(entity_id, evaluation_result.results[entity_id])

    def evaluate(
            self,
            context: Dict,
            evaluation_result: Optional[EvaluationResult] = None
    ) -> EvaluationResult:
        """ Evaluate Policy Set"""
        evaluation_result = evaluation_result if evaluation_result is not None else EvaluationResult(
        )
        try:
            cr_str = getattr(self, "conflict_resolution")
            cr_obj = cr_switcher[cr_str]()
        except KeyError:
            raise NotImplementedError(
                "Conflict Resolution %s is not implemented" % cr_str)
        except AttributeError:
            # This happens if we are evaluating a rule here
            pass

        try:
            if self._check_match(context):
                assert self.container is not None
                if hasattr(self, "policy_sets"):
                    for policy_set_id in getattr(self, "policy_sets"):
                        self._evaluate(policy_set_id,
                                       self.container.policy_sets,
                                       evaluation_result, cr_obj, context)
                        if cr_obj.check_break():
                            break
                if hasattr(self, "policies"):
                    for policy_id in getattr(self, "policies"):
                        self._evaluate(policy_id, self.container.policies,
                                       evaluation_result, cr_obj, context)
                        if cr_obj.check_break():
                            break
                if hasattr(self, "rules"):
                    for rule_id in getattr(self, "rules"):
                        self._evaluate(rule_id, self.container.rules,
                                       evaluation_result, cr_obj, context)
                        if cr_obj.check_break():
                            break
                evaluation_result.obligations.extend(self.obligations)
        except ACEntityMissing as excep:
            LOGGER.warning(
                "%s requested entity %s, but was not found in container",
                self.entity_id, excep.args[0])
            LOGGER.warning(traceback.format_exc())
            evaluation_result.results[self.entity_id] = None
            return evaluation_result
        except lark.exceptions.VisitError as e:
            if e.orig_exc.__class__ == parser.SubjectAttributeMissing:
                evaluation_result.results[self.entity_id] = None
                evaluation_result.missing_attr.append(e.orig_exc.attr)
                return evaluation_result
            if e.orig_exc.__class__ == parser.ObjectAttributeMissing:
                evaluation_result.results[self.entity_id] = None
                return evaluation_result
            if e.orig_exc.__class__ == parser.EnvironmentAttributeMissing:
                evaluation_result.results[self.entity_id] = None
                return evaluation_result

            raise

        # Update Evaluation Result
        evaluation_result.results[self.entity_id] = cr_obj.get_effect()
        return evaluation_result

    def _check_match(self, context: Dict) -> bool:
        return parser.check_target(self.target, context)


@dataclass
class Policy_Set(AC_Entity):
    conflict_resolution: str
    policy_sets: List[str]
    policies: List[str]



@dataclass
class Policy(AC_Entity):
    conflict_resolution: str
    rules: List[str]



@dataclass
class Rule(AC_Entity):
    condition: str
    effect: InitVar[str]

    def __post_init__(self, effect: str) -> None:
        self.effect = common.Effects[effect]

    def evaluate(
        self,
        context: Dict,
        evaluation_result: Optional[EvaluationResult] = None
    ) -> EvaluationResult:
        evaluation_result = evaluation_result if evaluation_result is not None else EvaluationResult(
        )
        try:
            evaluate_to_if_missing = None
            if self._check_match(context):
                evaluate_to_if_missing = common.Effects(not self.effect)
                if self._check_condition(context):
                    evaluation_result.results[self.entity_id] = self.effect
                else:
                    evaluation_result.results[self.entity_id] = common.Effects(
                        not self.effect)
                evaluation_result.obligations.extend(self.obligations)
                return evaluation_result

            evaluation_result.results[self.entity_id] = None
            return evaluation_result

        except lark.exceptions.VisitError as e:
            if e.orig_exc.__class__ == parser.SubjectAttributeMissing:
                evaluation_result.results[
                    self.entity_id] = evaluate_to_if_missing
                evaluation_result.missing_attr.append(e.orig_exc.attr)
                return evaluation_result
            if e.orig_exc.__class__ == parser.ObjectAttributeMissing:
                evaluation_result.results[
                    self.entity_id] = evaluate_to_if_missing
                return evaluation_result
            if e.orig_exc.__class__ == parser.EnvironmentAttributeMissing:
                evaluation_result.results[
                    self.entity_id] = evaluate_to_if_missing
                return evaluation_result
            raise
        return evaluation_result

    def _check_condition(self, context: Dict[str, Dict]) -> bool:
        return parser.check_condition(self.condition, context)



class AC_Container:
    def __init__(self) -> None:

        self.policies: Dict[str, Policy] = dict()
        self.policy_sets: Dict[str, Policy_Set] = dict()
        self.rules: Dict[str, Rule] = dict()

    def __str__(self) -> str:
        string = ""
        for key, val in itertools.chain(self.policies.items(),
                                        self.policy_sets.items(),
                                        self.rules.items()):
            string += "\n{}\n{}".format(str(key), str(val))

        return string

    def load_file(self, filename: str) -> None:
        try:
            with open(filename) as f:
                data = json.load(f)
                for entity_id, definition in data.items():
                    self.add_entity(entity_id, definition)
        except json.decoder.JSONDecodeError:
            LOGGER.error("JSON File %s is no valid json", filename)
        except TypeError:
            LOGGER.error("Error handling file: %s", filename)

    def load_dir(self, path: str) -> None:
        import glob
        for f in glob.glob(path + "/*.json"):
            self.load_file(f)

    def evaluate_by_entity_id(
        self,
        entity_id: str,
        context: Dict[str, MutableMapping],
        evaluation_result: Optional[EvaluationResult] = None
    ) -> EvaluationResult:
        if evaluation_result is None:
            evaluation_result = EvaluationResult()

        if entity_id in evaluation_result.results:
            return evaluation_result
        # Effect, Missing
        try:
            evaluation_result = self.policy_sets[entity_id].evaluate(
                context, evaluation_result)
        except KeyError:
            LOGGER.debug("Requested ps %s, but was not found in container",
                         entity_id)
            raise ACEntityMissing(entity_id)

        return evaluation_result

    def add_entity(self, entity_id: str, definition: Dict[str, str]) -> None:
        if not isinstance(definition, Dict):
            LOGGER.warning("Cannot find ac entity type or cannot initialize")
            LOGGER.warning('Error at: %s', definition)
            raise TypeError("Cannot add ac entity without definition as dict")
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
            "Obligations": "obligations",
            "Type": "--filter--"
        }
        kwargs = {
            cleaner[key]: value
            for (key, value) in definition.items()
            if cleaner.get(key) != "--filter--"
        }
        LOGGER.debug('Creating %s with parameters %s', definition['Type'],
                     str(kwargs))
        try:
            obj: AC_Entity = switcher[definition['Type']](entity_id, **kwargs)
            AC_Entity.container = self

            obj_container: Dict[str,
                                AC_Entity] = switcher_dict[definition['Type']]
            obj_container[entity_id] = obj
        except KeyError:
            LOGGER.warning("Cannot find ac entity type or cannot initialize")
            LOGGER.warning('Error at: %s', definition)
        except TypeError:
            LOGGER.warning("Probably error in AC Entity Definition")
            LOGGER.warning('Error at: %s with parameters %s',
                           definition['Type'], str(kwargs))

    def check(self) -> bool:
        consistent = True
        for key, entity in itertools.chain(self.policy_sets.items(), self.policies.items(), self.rules.items()):
            if hasattr(entity, "conflict_resolution"):
                cr_str = getattr(entity, "conflict_resolution")
                if cr_str not in cr_switcher:
                    print("Conflict Resolution %s not found requested by %s" % (cr_str, key))
            if hasattr(entity, "policy_sets"):
                for policy_set in getattr(entity, "policy_sets"):
                    if policy_set not in self.policy_sets:
                        consistent = False
                        print("Could not find policy set %s requested by %s" % (policy_set, key))
            if hasattr(entity, "policies"):
                for policy in getattr(entity, "policies"):
                    if policy not in self.policies:
                        consistent = False
                        print("Could not find policy %s requested by %s" % (policy, key))
            if hasattr(entity, "rules"):
                for rule in getattr(entity, "rules"):
                    if rule not in self.rules:
                        consistent = False
                        print("Could not find rule %s requested by %s" % (policy, key))
            if not parser.parseable(parser.lark_target, entity.target):
                consistent = False
                print("Target rule is not parseable: %s in %s" % (entity.target, key))
            if hasattr(entity, "condition"):
                if not parser.parseable(parser.lark_condition, getattr(entity, "condition")):
                    consistent = False
                    print("Target rule is not parseable: %s in %s" % (getattr(entity, "condition"), key))

        return consistent




def print_sample_ac() -> None:
    ac = """
{
    "com.example.policysets.default": {
		"Type": "PolicySet",
		"Description": "Default Policy Set",
		"Target": "True",
		"Policies": ["com.example.policies.default"],
		"PolicySets": [],
		"Resolver": "ANY",
		"Obligations" : []
    },
    "com.example.policies.default": {
		"Type": "Policy",
		"Description": "Default Policy",
		"Target" : "True",
		"Rules" : [ "com.example.rules.default" ],
		"Resolver": "AND",
		"Obligations" : []
    },
    "com.example.rules.default" : {
		"Type": "Rule",
		"Target": "True",
		"Description": "Default Rule",
		"Condition" : "True",
		"Effect": "GRANT",
		"Obligations" : []
    }
}
    """
    print(ac)


container = AC_Container()
