import pytest

from oidcproxy.ac.common import Effects
from oidcproxy.ac.conflict_resolution import *


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

def test_str():
    cr = AnyOfAny()
    cr.update("this_rule01", Effects.DENY)
    str_cr = str(cr)
    assert 'Results:DENY' in str_cr
    assert 'this_rule01' in str_cr
    assert 'Effects.DENY: False' in str_cr
    assert 'Break:False' in str_cr
    cr.update("this_rule02", Effects.GRANT)
    str_cr = str(cr)
    assert 'Results:GRANT' in str_cr
    assert 'this_rule01' in str_cr
    assert 'Effects.DENY: False' in str_cr
    assert 'Break:True' in str_cr


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
