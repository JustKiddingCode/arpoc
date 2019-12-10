import pkg_resources
import os

import logging
import warnings

import re

from lark import Lark, tree, Transformer, Tree
import lark.exceptions

grammar_path = pkg_resources.resource_filename(
    "__main__", os.path.join(os.pardir, 'resources', 'grammar.lark'))
with open(grammar_path) as fp:
    grammar = fp.read()

LOGGER = logging.getLogger(__name__)


class BadSemantics(Exception):
    pass


class BinaryOperator:
    @classmethod
    def eval(cls, op1, op2):
        pass


class BinaryStringOperator(BinaryOperator):
    @classmethod
    def eval(cls, op1, op2):
        if not isinstance(op1, str):
            raise BadSemantics("op1 '{}' is not a string".format(op1))
        if not isinstance(op2, str):
            raise BadSemantics("op2 '{}' is not a string".format(op2))


class BinaryNumeralOperator(BinaryOperator):
    @classmethod
    def eval(cls, op1, op2):
        NumberTypes = (int, float)
        if not isinstance(op1, NumberTypes):
            raise BadSemantics("op1 '{}' is not a number".format(op1))
        if not isinstance(op2, NumberTypes):
            raise BadSemantics("op1 '{}' is not a number".format(op2))


class BinaryOperatorIn(BinaryOperator):
    @classmethod
    def eval(cls, op1, op2):
        if not isinstance(op2, list):
            raise BadSemantics("op1 '{}' is not a string".format(op2))
        return op1 in op2


class Lesser(BinaryNumeralOperator):
    @classmethod
    def eval(cls, op1, op2):
        super().eval(op1, op2)
        return op1 < op2


class Greater(BinaryNumeralOperator):
    @classmethod
    def eval(cls, op1, op2):
        super().eval(op1, op2)
        return op1 > op2


class Equal(BinaryOperator):
    @classmethod
    def eval(cls, op1, op2):
        return op1 == op2


class NotEqual(BinaryOperator):
    @classmethod
    def eval(cls, op1, op2):
        return op1 != op2


class startswith(BinaryStringOperator):
    @classmethod
    def eval(cls, op1, op2):
        super().eval(op1, op2)
        return op1.startswith(op2)


class matches(BinaryStringOperator):
    @classmethod
    def eval(cls, op1, op2):
        super().eval(op1, op2)
        return re.fullmatch(op2, op1) != None


binary_operators = {
    "startswith": startswith,
    "matches": matches,
    "in": BinaryOperatorIn,
    "<": Lesser,
    ">": Greater,
    "==": Equal,
    "!=": NotEqual
}


class AttributeMissingWarning(Warning):
    pass


class SubjectAttributeMissingWarning(AttributeMissingWarning):
    pass


class ObjectAttributeMissingWarning(AttributeMissingWarning):
    pass


class EnvironmentAttributeMissingWarning(AttributeMissingWarning):
    pass


class BadRuleSyntax(Exception):
    pass


class UOP:
    def exists(elem):
        return elem != None


class TransformAttr(Transformer):
    def __init__(self, data):
        super().__init__(self)
        self.data = data

    def subject_attr(self, args):
        attr = self.data["subject"].get(str(args[0]), None)
        if attr == None:
            warnings.warn("No subject_attr %s" % str(args[0]),
                          SubjectAttributeMissingWarning)
        return attr

    def object_attr(self, args):
        attr = self.data["object"].get(str(args[0]), None)
        if attr == None:
            warnings.warn("No object_attr %s" % str(args[0]),
                          ObjectAttributeMissingWarning)

        return attr

    def environment_attr(self, args):
        attr = self.data["environment"].get(str(args[0]), None)
        if attr == None:
            warnings.warn("No environment_attr %s" % str(args[0]),
                          EnvironmentAttributeMissingWarning)

        return attr

    def list_inner(self, args):
        # either we have two children (one list, one literal) or one child (literal)
        if len(args) == 1:
            return [args[0]]
        else:
            return [args[0]] + args[1]

    def lit(self, args):
        if isinstance(args[0], (list, )):
            return args[0]
        if args[0].type == "SINGLE_QUOTED_STRING":
            return str(args[0][1:-1])
        elif args[0].type == "DOUBLE_QUOTED_STRING":
            return str(args[0][1:-1])
        elif args[0].type == "BOOL":
            return args[0] == "True"
        else:
            return int(args[0])


class EvalComplete(Transformer):
    def condition(self, args):
        if len(args) == 1:
            return args[0]
        else:
            return Tree("condition", args)

    def target(self, args):
        if len(args) == 1:
            return args[0]
        else:
            return Tree("target", args)


class EvalTree(Transformer):
    def cbop(self, args):
        return str(args[0])

    def lbop(self, args):
        return str(args[0])

    def statement(self, args):
        if len(args) == 1:
            return args[0]
        else:
            return Tree("statement", args)

    def comparison(self, args):
        # xor check for none attributes
        if bool(args[0] == None) ^ bool(args[2] == None):
            return False
        op = binary_operators.get(args[1], None)
        if op == None:
            raise NotImplementedError()
        LOGGER.debug("{} {} {}".format(args[0], args[1], args[2]))
        return op.eval(args[0], args[2])

    def linked(self, args):
        if isinstance(args[0], bool) and isinstance(args[2], bool):
            print("{} {} {}".format(args[0], args[1], args[2]))
            return eval("{} {} {}".format(args[0], args[1], args[2]))
        else:
            return Tree("linked", args)

    def uop(self, args):
        return getattr(UOP, str(args[0]))

    def single(self, args):
        if len(args) == 2:
            return args[0](args[1])
        elif len(args) == 1:
            return args[0]
        assert False
        return None


def check_condition(condition, data):
    LOGGER.debug("Check condition %s with data %s", condition, data)
    l = Lark(grammar, start="condition")
    try:
        ast = l.parse(condition)
    except (lark.exceptions.UnexpectedCharacters,
            lark.exceptions.UnexpectedEOF):
        raise BadRuleSyntax('Rule has a bad syntax %s' % condition)
    T = TransformAttr(data) * EvalTree() * EvalComplete()
    ret_value = T.transform(ast)
    LOGGER.debug("Condition %s evaluated to %s", condition, ret_value)

    return ret_value


def check_target(rule, data):
    LOGGER.debug("Check target rule %s with data %s", rule, data)
    l = Lark(grammar, start="target")
    try:
        ast = l.parse(rule)
    except (lark.exceptions.UnexpectedCharacters,
            lark.exceptions.UnexpectedEOF):
        raise BadRuleSyntax('Rule has a bad syntax %s' % target)
    T = TransformAttr(data) * EvalTree() * EvalComplete()
    ret_value = T.transform(ast)
    LOGGER.debug("Target Rule %s evaluated to %s", rule, ret_value)
    return ret_value


if __name__ == "__main__":

    l = Lark(grammar, start="condition")

    ast = l.parse("[5, '4', True]")
    print(ast)
    data = {}
    ast = TransformAttr(data).transform(ast)
    tree.pydot__tree_to_png(ast, "graph.png")
#    ast = l.parse("subject.email != object.email")
#    #print(ast)
#
#    data = {
#        "subject": {
#            "email": "blub"
#        },
#        "object": {
#            "email": "blab"
#        },
#        "environment": {
#            "time": 2
#        }
#    }
#    transformed = TransformAttr(data).transform(ast)
#    transformed = EvalTree().transform(transformed)
#    tree.pydot__tree_to_png(ast, "graph.png")
#    tree.pydot__tree_to_png(transformed, "graph02.png")
#    ast = l.parse("exists environment.time")
#    tree.pydot__tree_to_png(ast, "graph01.png")
#    T = TransformAttr(data) * EvalTree() * EvalComplete()
#    t1 = TransformAttr(data).transform(ast)
#    t2 = EvalTree().transform(t1)
#    t3 = EvalComplete().transform(t2)
#    print(T.transform(ast))
#    print(t3)
#    ast = l.parse("True")
#    tree.pydot__tree_to_png(ast, "graph04.png")
#    ast = l.parse("environment.time < 3")
#    tree.pydot__tree_to_png(ast, "graph03_orig.png")
#    ast = TransformAttr(data).transform(ast)
#    tree.pydot__tree_to_png(ast, "graph03_attr.png")
#    ast = EvalTree().transform(ast)
#    tree.pydot__tree_to_png(ast, "graph03.png")
