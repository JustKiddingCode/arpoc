import pytest
import ac

from ac.common import Effects


def test_alwaysGrant():
    context = {"subject": {}, "object": {}, "environment": {}}
    assert ac.container.evaluate_by_entity_id(
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
    assert ac.container.evaluate_by_entity_id(
        "com.example.policysets.loggedIn", context) == Effects.GRANT
    context = {
        "subject": {
            'email': 'admin@example.com'
        },
        "object": {
            'url': 'admin'
        },
        "environment": {}
    }
    assert ac.container.evaluate_by_entity_id(
        "com.example.policysets.loggedIn", context) == Effects.GRANT


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
    assert ac.container.evaluate_by_entity_id(
        "com.example.policysets.loggedIn", context) == Effects.DENY
