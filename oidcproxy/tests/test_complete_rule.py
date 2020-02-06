import importlib.resources
import os

import lark
import pytest

import oidcproxy.ac
import oidcproxy.exceptions
from oidcproxy.ac.common import Effects

Container = oidcproxy.ac.AC_Container()

test_acls = 'oidcproxy.tests.resources.acl'

for f in importlib.resources.contents(test_acls):
    if f.endswith(".json"):
        with importlib.resources.path(test_acls, f) as path_p:
            Container.load_file(path_p)


def test_only_init_lark(benchmark):
    benchmark(lark.Lark, oidcproxy.ac.parser.grammar, start="condition")


def test_alwaysGrant(benchmark):
    context = {"subject": {}, "object": {}, "environment": {}}
    evaluation_result = benchmark(Container.evaluate_by_entity_id,
                                  "com.example.policysets.alwaysGrant",
                                  context)
    assert evaluation_result.results[
        "com.example.policysets.alwaysGrant"] == Effects.GRANT


def test_missing_entities():
    context = {"subject": {}, "object": {}, "environment": {}}
    # A Service with missing policy set should raise an exception
    with pytest.raises(oidcproxy.exceptions.ACEntityMissing):
        effect, _ = Container.evaluate_by_entity_id("not-existing", context)
    # Everything else should return none
    assert Container.policies["policy_with_missing_rule"].evaluate(
        context).results["policy_with_missing_rule"] is None
    assert Container.policy_sets["policyset_with_missing_policyset"].evaluate(
        context).results["policyset_with_missing_policyset"] is None
    assert Container.policy_sets["policyset_with_missing_policy"].evaluate(
        context).results["policyset_with_missing_policy"] is None


def test_container_to_string():
    container_str = str(Container)
    assert "Policy(" in container_str
    assert "Policy_Set(" in container_str
    assert "Rule" in container_str


def test_broken_json(caplog):
    with importlib.resources.path(test_acls, "broken_json") as path_p:
        Container.load_file(path_p)
    assert "JSON File" in caplog.text
    assert "is no valid json" in caplog.text


def test_broken_definitions(caplog):
    with importlib.resources.path(test_acls, "broken_definitions") as path_p:
        Container.load_file(path_p)
    assert "Probably error in AC Entity Definition" in caplog.text


def test_json_no_ac_format(caplog):
    with importlib.resources.path(test_acls, "json_no_ac_format") as path_p:
        Container.load_file(path_p)
    assert "Error handling file" in caplog.text


def test_loggedIn(benchmark):
    context = {
        "subject": {
            'email': 'admin@example.com'
        },
        "object": {
            'url': 'notSecure'
        },
        "environment": {}
    }

    evaluation_result = benchmark(Container.evaluate_by_entity_id,
                                  "com.example.policysets.loggedIn", context)
    assert evaluation_result.results[
        "com.example.policysets.loggedIn"] == Effects.GRANT


def test_loggedInAdmin(benchmark):
    context = {
        "subject": {
            'email': 'admin@example.com'
        },
        "object": {
            'url': 'admin'
        },
        "environment": {}
    }
    test = "com.example.policysets.loggedIn"
    evaluation_result = benchmark(Container.evaluate_by_entity_id, test,
                                  context)
    assert evaluation_result.results[test] == Effects.GRANT


def test_normalUser_wants_admin(benchmark):
    context = {
        "subject": {
            'email': 'normaluser@example.com'
        },
        "object": {
            'url': 'admin'
        },
        "environment": {}
    }
    test = "com.example.policysets.loggedIn"
    evaluation_result = benchmark(Container.evaluate_by_entity_id, test,
                                  context)
    assert evaluation_result.results[test] == Effects.DENY
