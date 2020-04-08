import importlib.resources
import arpoc.ac
from arpoc.ac.parser import check_condition

import pytest

test_acls = 'arpoc.tests.resources.acl'


# Benchmark complete evaluation
@pytest.fixture
def Container():
    Container = arpoc.ac.AC_Container()
    for f in importlib.resources.contents(test_acls):
        if f.endswith(".json"):
            with importlib.resources.path(test_acls, f) as path_p:
                Container.load_file(path_p)
    return Container


def test_hierarchy_evaluation(benchmark, Container):
    context = {"subject": {}, "object": {}, "environment": {}}
    benchmark(Container.evaluate_by_entity_id, "com.example.policysets.alwaysGrant", context)


# Benchmark True evaluation
def test_true(benchmark):
    benchmark(check_condition, "True", {} )

def test_true_attribute(benchmark):
    subject = {"attr1" : True}
    context = {"subject" : subject }
    benchmark(check_condition, "subject.attr1", context )


# Integer Comparison
def test_integer_comparison_small_true(benchmark):
    subject = {"attr1" : 1, "attr2" : 5}
    context = {"subject" : subject }
    rule = "subject.attr1 < subject.attr2"
    benchmark(check_condition, rule, context)

def test_integer_comparison_small_false(benchmark):
    subject = {"attr1" : 1, "attr2" : 5}
    context = {"subject" : subject }
    rule = "subject.attr1 > subject.attr2"
    benchmark(check_condition, rule, context)

def test_integer_comparison_big_true(benchmark):
    subject = {"attr1" : 1000000, "attr2" : 5000000}
    context = {"subject" : subject }
    rule = "subject.attr1 < subject.attr2"
    benchmark(check_condition, rule, context)

def test_integer_comparison_big_false(benchmark):
    subject = {"attr1" : 1000000, "attr2" : 5000000}
    context = {"subject" : subject }
    rule = "subject.attr1 > subject.attr2"
    benchmark(check_condition, rule, context)

# String Equality

def test_string_equality_small_true(benchmark):
    subject = {"attr1" : "abcdefghijklmnopqrstuvxxyz", "attr2" : "abcdefghijklmnopqrstuvxxyz"}
    context = {"subject" : subject }
    rule = "subject.attr1 == subject.attr2"
    benchmark(check_condition, rule, context)

def test_string_equality_small_false(benchmark):
    subject = {"attr1" : "abcdefghijklmnopqrstuvxxyz", "attr2" : "abcdefghijklmnopqrstuvxxyZ"}
    context = {"subject" : subject }
    rule = "subject.attr1 == subject.attr2"
    benchmark(check_condition, rule, context)

def test_string_equality_big_true(benchmark):
    import string
    import random
    import copy
    big_string = ''.join(random.choices(string.ascii_lowercase, k=1000))
    big_string2 = copy.copy(big_string)
    subject = {"attr1" : big_string, "attr2" : big_string2}
    context = {"subject" : subject }
    rule = "subject.attr1 == subject.attr2"
    benchmark(check_condition, rule, context)

def test_string_equality_big_false(benchmark):
    import string
    import random
    import copy
    big_string = ''.join(random.choices(string.ascii_lowercase, k=1000))
    big_string2 = big_string[:-1] + "Z"
    subject = {"attr1" : big_string, "attr2" : big_string2}
    context = {"subject" : subject }
    rule = "subject.attr1 == subject.attr2"
    benchmark(check_condition, rule, context)

# Integer Equality

def test_integer_equality_big_true(benchmark):
    subject = {"attr1" : 1000000, "attr2" : 1000000}
    context = {"subject" : subject }
    rule = "subject.attr1 == subject.attr2"
    benchmark(check_condition, rule, context)

def test_integer_equality_big_false(benchmark):
    subject = {"attr1" : 1000000, "attr2" : 5000000}
    context = {"subject" : subject }
    rule = "subject.attr1 == subject.attr2"
    benchmark(check_condition, rule, context)

# String Startswith
def test_string_startswith_true(benchmark):
    subject = {"attr1" : "abcdefghijklmnopqrstuvwxyz", "attr2" : "abcdefghij"}
    context = {"subject" : subject }
    rule = "subject.attr1 startswith subject.attr2"
    benchmark(check_condition, rule, context)

def test_string_startswith_false(benchmark):
    subject = {"attr1" : "abcdefghijklmnopqrstuvwxyz", "attr2" : "abcdefghiK"}
    context = {"subject" : subject }
    rule = "subject.attr1 startswith subject.attr2"
    benchmark(check_condition, rule, context)

# Regex
def test_string_regex_true(benchmark):
    subject = {"attr1" : "test@example.com"}
    context = {"subject" : subject }
    rule = "subject.attr1 matches r'^[A-Z0-9._%+-]+@(?:[A-Z0-9-]+\.)+[A-Z]{2,}$'"
    benchmark(check_condition, rule, context)

def test_string_regex_false(benchmark):
    subject = {"attr1" : "test example.com"}
    context = {"subject" : subject }
    rule = "subject.attr1 matches r'^[A-Z0-9._%+-]+@(?:[A-Z0-9-]+\.)+[A-Z]{2,}$'"
    benchmark(check_condition, rule, context)

# in
def test_in_true(benchmark):
    subject = {"attr1" : "z", "attr2": ["a","b","c","d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]}
    context = {"subject" : subject }
    rule = "subject.attr1 in subject.attr2"
    benchmark(check_condition, rule, context)

def test_in_false(benchmark):
    subject = {"attr1" : "z", "attr2": ["a","b","c","d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y"]}
    context = {"subject" : subject }
    rule = "subject.attr1 in subject.attr2"
    benchmark(check_condition, rule, context)


def test_exists_true(benchmark):
    subject = {"attr1": True}
    context = {"subject" : subject }
    rule = "exists subject.attr1"
    benchmark(check_condition, rule, context)

def test_exists_false(benchmark):
    subject = {}
    context = {"subject" : subject }
    rule = "exists subject.attr1"
    benchmark(check_condition, rule, context)

def test_directory_access(benchmark):
    subject = {"attr1" : { "a" : { "b" : { "c" : { "d" : { "e" : { "f" : { "g" : { "h" : { "i" : True } } } } } } } } } }
    context = {"subject" : subject }
    rule = "subject.attr1.a.b.c.d.e.f.g.h.i"
    benchmark(check_condition, rule, context)

def test_and(benchmark):
    rule = "True and True"
    benchmark(check_condition, rule, {})

def test_or(benchmark):
    rule = "True and True"
    benchmark(check_condition, rule, {})
