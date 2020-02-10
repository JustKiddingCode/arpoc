import importlib.resources
import os

import lark
import pytest

import oidcproxy.ac
import oidcproxy.exceptions
from oidcproxy.ac.common import Effects


test_acls = 'oidcproxy.tests.resources.acl'


@pytest.fixture
def Container():
    Container = oidcproxy.ac.AC_Container()
    for f in importlib.resources.contents(test_acls):
        if f.endswith(".json"):
            with importlib.resources.path(test_acls, f) as path_p:
                Container.load_file(path_p)
    return Container


def test_only_init_lark(benchmark):
    benchmark(lark.Lark, oidcproxy.ac.parser.grammar, start="condition")


def test_alwaysGrant(benchmark, Container):
    context = {"subject": {}, "object": {}, "environment": {}}
    evaluation_result = benchmark(Container.evaluate_by_entity_id,
                                  "com.example.policysets.alwaysGrant",
                                  context)
    assert evaluation_result.results[
        "com.example.policysets.alwaysGrant"] == Effects.GRANT

def test_obligations(Container):
    context = {"subject": {}, "object": {}, "environment": {}}
    print(Container.policy_sets.keys())
    ps = Container.policy_sets["policyset_with_obligation"]
    res = ps.evaluate(context)
    assert res.obligations == ['obl_log_failed']

def test_missing_entities(Container):
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


def test_container_to_string(Container):
    container_str = str(Container)
    assert "Policy(" in container_str
    assert "Policy_Set(" in container_str
    assert "Rule" in container_str


def test_broken_json(caplog, Container):
    with importlib.resources.path(test_acls, "broken_json") as path_p:
        Container.load_file(path_p)
    assert "JSON File" in caplog.text
    assert "is no valid json" in caplog.text


def test_broken_definitions(caplog, Container):
    with importlib.resources.path(test_acls, "broken_definitions") as path_p:
        Container.load_file(path_p)
    assert "Probably error in AC Entity Definition" in caplog.text


def test_json_no_ac_format(caplog, Container):
    with importlib.resources.path(test_acls, "json_no_ac_format") as path_p:
        Container.load_file(path_p)
    assert "Error handling file" in caplog.text


def test_loggedIn(benchmark, Container):
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


def test_loggedInAdmin(benchmark, Container):
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


def test_normalUser_wants_admin(benchmark, Container):
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
