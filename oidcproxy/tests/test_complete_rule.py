import pytest
import ac

from ac.common import Effects

import importlib.resources

import os

Container = ac.AC_Container()
with importlib.resources.path(
        'tests.resources.acl',
        'policies.json') as path_p, importlib.resources.path(
            'tests.resources.acl',
            'rules.json') as path_r, importlib.resources.path(
                'tests.resources.acl', 'policysets.json') as path_ps:

    Container.load_file(path_p)
    Container.load_file(path_r)
    Container.load_file(path_ps)


def test_alwaysGrant():
    context = {"subject": {}, "object": {}, "environment": {}}
    assert Container.evaluate_by_entity_id(
        "com.example.policysets.alwaysGrant", context) == Effects.GRANT


def test_loggedIn():
    context = {
        "subject": {
            'email': 'admin@example.com'
        },
        "object": {
            'url': 'notSecure'
        },
        "environment": {}
    }
    assert Container.evaluate_by_entity_id("com.example.policysets.loggedIn",
                                           context) == Effects.GRANT
    context = {
        "subject": {
            'email': 'admin@example.com'
        },
        "object": {
            'url': 'admin'
        },
        "environment": {}
    }
    assert Container.evaluate_by_entity_id("com.example.policysets.loggedIn",
                                           context) == Effects.GRANT


def test_normalUser_wants_admin():
    context = {
        "subject": {
            'email': 'normaluser@example.com'
        },
        "object": {
            'url': 'admin'
        },
        "environment": {}
    }
    assert Container.evaluate_by_entity_id("com.example.policysets.loggedIn",
                                           context) == Effects.DENY
