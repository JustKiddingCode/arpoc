import pytest

from ac.conflict_resolution import *
from ac.common import Effects


def test_any_of_any_0_rules():
    cr = AnyOfAny()
    assert cr.check_break() == False
    assert cr.get_effect() == None


def test_any_of_any():
    cr = AnyOfAny()
    cr.update("this_rule", Effects.GRANT)

    assert cr.check_break()
    assert cr.get_effect() == Effects.GRANT


def test_any_of_any_none():
    cr = AnyOfAny()
    cr.update("this_rule", None)
    assert not cr.check_break()
    assert cr.get_effect() == None


def test_any_of_any_2_rules():
    cr = AnyOfAny()
    cr.update("this_rule01", Effects.DENY)
    assert not cr.check_break()
    cr.update("this_rule02", Effects.GRANT)

    assert cr.check_break()
    assert cr.get_effect() == Effects.GRANT


def test_And_0_rules():
    cr = And()
    assert cr.check_break() == False
    assert cr.get_effect() == None


def test_And():
    cr = And()
    cr.update("this_rule01", Effects.GRANT)
    assert not cr.check_break()
    assert cr.get_effect() == Effects.GRANT
    cr = And()
    cr.update("this_rule01", Effects.DENY)
    assert cr.check_break()
    assert cr.get_effect() == Effects.DENY
