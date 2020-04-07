from dataclasses import dataclass, field
from typing import List, Tuple, Union, Optional, Dict

import ast

from collections.abc import Mapping

import os

import itertools

from jinja2 import Environment, FileSystemLoader

from arpoc.base import ServiceProxy, ObjectDict, EnvironmentDict
import arpoc.ac as ac

env = Environment(loader=FileSystemLoader(
    os.path.join(os.path.dirname(__file__), 'resources', 'templates')))


@dataclass
class PAPNode:
    ID: str
    node_type: str
    resolver: str
    target: str
    effect: str
    condition: str
    policy_sets: Optional[List['PAPNode']]
    policies: Optional[List['PAPNode']]
    rules: Optional[List['PAPNode']]


def create_PAPNode_Rule(rule: ac.Rule) -> PAPNode:
    return PAPNode(rule.entity_id, "rule", "", rule.target, str(rule.effect),
                   rule.condition, None, None, None)


def create_PAPNode_Policy(policy: ac.Policy) -> PAPNode:
    rules = [create_PAPNode_Rule(ac.container.rules[x]) for x in policy.rules]
    return PAPNode(policy.entity_id, "policy", policy.conflict_resolution,
                   policy.target, "", "", None, None, rules)


def create_PAPNode_Policy_Set(policy_set: ac.Policy_Set) -> PAPNode:
    policies = [
        create_PAPNode_Policy(ac.container.policies[x])
        for x in policy_set.policies
    ]
    policy_sets = [
        create_PAPNode_Policy_Set(ac.container.policy_sets[x])
        for x in policy_set.policy_sets
    ]
    return PAPNode(policy_set.entity_id, "policy set",
                   policy_set.conflict_resolution, policy_set.target, "", "",
                   policy_sets, policies, None)


class PolicyAdministrationPoint(ServiceProxy):
    #    def __init__(self):
    #        pass

    def _proxy(self, url: str, access: Dict) -> str:
        context = {}

        if url.startswith('pap/testbed'):
            services = self._oidc_handler.cfg.services.keys()
            s = []
            result: Optional[ac.EvaluationResult] = None
            obj_setters = False
            env_setters = False
            try:
                # access.query_dict
                entity_id, sub, obj, acc, env_attr, service = (
                    access['query_dict'][x].strip() for x in
                    ['entity', 'subject', 'object', 'access', 'environment', 'service'])
                if "object_setters" in access['query_dict']:
                    obj_setters = True
                if "environment_setters" in access['query_dict']:
                    env_setters = True
            except KeyError:
                pass
            else:
                if service not in services:
                    return ""
                entity_obj: ac.AC_Entity
                # get the entity_id object
                if entity_id in ac.container.policy_sets:
                    typ = "policy_set"
                    entity_obj = ac.container.policy_sets[entity_id]
                    s.append(create_PAPNode_Policy_Set(entity_obj))
                elif entity_id in ac.container.policies:
                    typ = "policy"
                    entity_obj = ac.container.policies[entity_id]
                    s.append(create_PAPNode_Policy(entity_obj))
                elif entity_id in ac.container.rules:
                    typ = "rule"
                    entity_obj = ac.container.rules[entity_id]
                    s.append(create_PAPNode_Rule(entity_obj))
                else:
                    return ""
                try:
                    sub_dict = ast.literal_eval(sub)
                except SyntaxError:
                    sub_dict = {}
                try:
                    obj_dict = ast.literal_eval(obj)
                except SyntaxError:
                    obj_dict = {}
                try:
                    env_dict = ast.literal_eval(env_attr)
                except SyntaxError:
                    env_dict = {}
                try:
                    acc_dict = ast.literal_eval(acc)
                except SyntaxError:
                    acc_dict = {}

                obj_dict['service'] = service

                if obj_setters:
                    obj_dict = ObjectDict(self._oidc_handler.cfg.services[service].objectsetters)
                if env_setters:
                    env_dict = EnvironmentDict()
                context = {
                    'subject': sub_dict,
                    'object': obj_dict,
                    'environment': env_dict,
                    'access': acc_dict
                }
                result = entity_obj.evaluate(context)



            entity_ids = itertools.chain(ac.container.policy_sets.keys(),
                                         ac.container.policies.keys(),
                                         ac.container.rules.keys())


            tmpl = env.get_template('testbed.html')
            return tmpl.render(pap_nodes=s,
                               entity_ids=entity_ids,
                               result=result, services=services, **context)

        tmpl = env.get_template('pap.html')
        s = []
        for ps in ac.container.policy_sets:
            s.append(create_PAPNode_Policy_Set(ac.container.policy_sets[ps]))
        #url.startswith('pap/view')
        return tmpl.render(pap_nodes=s)
