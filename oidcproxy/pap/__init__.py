from jinja2 import Environment, FileSystemLoader

from dataclasses import dataclass, field
from typing import List

import os

import oidcproxy.ac as ac

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
    policy_sets: List[object]
    policies: List[object]
    rules: List[object]


def create_PAPNode_Rule(rule: ac.Rule):
    return PAPNode(rule.entity_id, "rule", "", rule.target, rule.effect,
                   rule.condition, None, None, None)


def create_PAPNode_Policy(policy: ac.Policy):
    rules = [create_PAPNode_Rule(ac.container.rules[x]) for x in policy.rules]
    return PAPNode(policy.entity_id, "policy", policy.conflict_resolution,
                   policy.target, "", "", None, None, rules)


def create_PAPNode_Policy_Set(policy_set: ac.Policy_Set):
    policies = [
        create_PAPNode_Policy(ac.container.policies[x])
        for x in policy_set.policies
    ]
    policy_sets = [
        create_PAPNode_Policy_Set(ac.container.policy_set[x])
        for x in policy_set.policy_sets
    ]
    return PAPNode(policy_set.entity_id, "policy set",
                   policy_set.conflict_resolution, policy_set.target, "", "",
                   policy_sets, policies, None)


class PolicyAdministrationPoint:
    def __init__(self):
        pass

    def index(self):
        tmpl = env.get_template('pap.html')
        s = []
        for ps in ac.container.policy_sets:
            s.append(create_PAPNode_Policy_Set(ac.container.policy_sets[ps]))

        return tmpl.render(pap_nodes=s)
