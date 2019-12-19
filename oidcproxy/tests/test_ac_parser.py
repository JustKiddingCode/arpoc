import pytest

from ac.parser import *
from lark.exceptions import *


def test_plain():
    context = {"subject": {}, "object": {}, "environment": {}}
    assert check_condition('True', context)
    assert not check_condition('False', context)


def test_object_attr():
    context = {"subject": {}, "object": {'test': True}, "environment": {}}
    assert check_condition('object.test == True', context)
    with pytest.warns(ObjectAttributeMissingWarning):
        assert not check_condition('exists object.NotExisting', context)

def test_time_comp():
    context = {"subject": {}, "object": {}, "environment": {"time" : "10:28"}}
    assert check_condition("environment.time < '10:30' and environment.time > '10:20'", context)


def test_subject_attr():
    context = {
        "subject": {
            'email': 'bla'
        },
        "object": {},
        "environment": {
            'time': 123
        }
    }
    assert check_condition('exists subject.email', context)
    with pytest.warns(SubjectAttributeMissingWarning):
        assert not check_condition('exists subject.NotExisting', context)


def test_environment_attr():
    context = {"subject": {}, "object": {}, "environment": {'time': 123}}
    assert check_condition('environment.time < 1000', context)
    with pytest.warns(EnvironmentAttributeMissingWarning):
        assert not check_condition('exists environment.NotExisting', context)


def test_regex():
    context = {
        "subject": {
            'name': 'fritz.mueller'
        },
        "object": {},
        "environment": {}
    }
    assert check_condition('subject.name matches ".*\.mueller"', context)


def test_startswith():
    context = {"subject": {}, "object": {}, "environment": {}}
    assert check_condition('"abcdef" startswith "abc"', context)


def test_startswith_bad_semantics():
    context = {"subject": {}, "object": {}, "environment": {}}
    assert check_condition('"123456789" startswith "123"', context)
    with pytest.raises(VisitError):
        assert check_condition('123456789 startswith 123', context)
    with pytest.raises(VisitError):
        assert check_condition('"apfel" startswith 123', context)


def test_in_list():
    context = {
        "subject": {
            'groups': ['admin', 'user', 'group']
        },
        "object": {},
        "environment": {}
    }
    assert check_condition('5 in [5,4,3]', context)
    assert check_condition("'admin' in subject.groups", context)
    assert check_condition('"admin" in subject.groups', context)
    assert not check_condition('"root" in subject.groups', context)
    context = {"subject": {}, "object": {}, "environment": {}}
    with pytest.warns(SubjectAttributeMissingWarning):
        assert not check_condition("'root' in subject.groups", context)
        assert isinstance(check_condition("'root' in subject.groups", context),
                          bool)


def test_combination():
    context = {"subject": {'email': 'bla'}, "object": {}, "environment": {}}
    assert check_condition('True and True', context)


def test_integer_comparison():
    context = {"subject": {}, "object": {}, "environment": {}}
    assert check_condition('5 < 6', context)
    assert check_condition('6 > 5', context)
    assert check_condition('5 == 5', context)
    assert not check_condition('5 > 6', context)
    assert not check_condition('6 < 5', context)
    assert not check_condition('6 == 7', context)
    assert not check_condition('6 < 6', context)
    assert not check_condition('6 > 6', context)


def test_integer_comparison_bad_semantics():
    context = {"subject": {}, "object": {}, "environment": {}}
    with pytest.raises(VisitError):
        assert check_condition('"bla" < 6', context)
    with pytest.raises(VisitError):
        assert check_condition('6 > "bla"', context)


def test_email_string():
    context = {
        "subject": {
            'email': 'info@example.com'
        },
        "object": {},
        "environment": {}
    }
    assert check_condition('subject.email == "info@example.com"', context)


#    assert not check_condition('exists subject.NotExisting',context)
def test_email_string_single_quoted():
    context = {
        "subject": {
            'email': 'info@example.com'
        },
        "object": {},
        "environment": {}
    }
    assert check_condition("subject.email == 'info@example.com'", context)


def test_None_mixed():
    context = {
        "subject": {
            'email': 'info@example.com'
        },
        "object": {},
        "environment": {}
    }
    with pytest.warns(ObjectAttributeMissingWarning):
        assert not check_condition("subject.email == object.email", context)


def test_lists():
    context = {"subject": {}, "object": {}, "environment": {}}
    assert check_condition("['5', 4, True]", context)


def test_nested_lists():
    context = {"subject": {}, "object": {}, "environment": {}}
    assert check_condition("['5', 4, True, [True,False]]",
                           context) == ['5', 4, True, [True, False]]


def tests_broken_conditions():
    context = {"subject": {}, "object": {}, "environment": {}}
    with pytest.raises(BadRuleSyntax):
        check_condition("true", context)
    with pytest.raises(BadRuleSyntax):
        check_condition("[1,2,3", context)
    with pytest.raises(BadRuleSyntax):
        check_condition("[1,2,3,]", context)
