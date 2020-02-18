import importlib.resources
import logging
import os
import re
import warnings
from abc import abstractmethod
from functools import reduce
from typing import Any, Dict, List, TypeVar, Union

from collections.abc import Mapping
import lark.exceptions
from lark import Lark, Transformer, Tree, tree

from oidcproxy.exceptions import *

with importlib.resources.path(
        'oidcproxy.resources',
        'grammar.lark') as grammar_path, open(grammar_path) as fp:
    grammar = fp.read()
lark_condition = Lark(grammar, start="condition")
lark_target = Lark(grammar, start="target")

LOGGER = logging.getLogger(__name__)

TNum = TypeVar('TNum', int, float)


class BinaryOperator:
    @classmethod
    @abstractmethod
    def eval(cls, op1: Any, op2: Any) -> Any:
        pass


class BinarySameTypeOperator(BinaryOperator):
    @classmethod
    @abstractmethod
    def eval(cls, op1: Any, op2: Any) -> bool:
        if type(op1) != type(op2):
            raise BadSemantics(
                "op1 '{}' and op2 '{}' need to have the same type, found {}, {}"
                .format(op1, op2, type(op1), type(op2)))
        return False


class BinaryStringOperator(BinaryOperator):
    @classmethod
    def eval(cls, op1: str, op2: str) -> bool:
        if not isinstance(op1, str):
            raise BadSemantics("op1 '{}' is not a string".format(op1))
        if not isinstance(op2, str):
            raise BadSemantics("op2 '{}' is not a string".format(op2))
        return False


class BinaryNumeralOperator(BinaryOperator):
    @classmethod
    def eval(cls, op1: TNum, op2: TNum) -> bool:
        NumberTypes = (int, float)
        if not isinstance(op1, NumberTypes):
            raise BadSemantics("op1 '{}' is not a number".format(op1))
        if not isinstance(op2, NumberTypes):
            raise BadSemantics("op1 '{}' is not a number".format(op2))
        return False


class BinaryOperatorIn(BinaryOperator):
    @classmethod
    def eval(cls, op1: Any, op2: Union[list, dict]) -> bool:
        if not isinstance(op2, list):
            if isinstance(op2, dict):
                return op1 in op2.keys()
            raise BadSemantics("op2 '{}' is not a list".format(op2))
        return op1 in op2


class Lesser(BinarySameTypeOperator):
    @classmethod
    def eval(cls, op1: Any, op2: Any) -> bool:
        super().eval(op1, op2)
        return op1 < op2


class Greater(BinarySameTypeOperator):
    @classmethod
    def eval(cls, op1: Any, op2: Any) -> bool:
        super().eval(op1, op2)
        return op1 > op2


class Equal(BinaryOperator):
    @classmethod
    def eval(cls, op1: Any, op2: Any) -> bool:
        return op1 == op2


class NotEqual(BinaryOperator):
    @classmethod
    def eval(cls, op1: Any, op2: Any) -> bool:
        return op1 != op2


class startswith(BinaryStringOperator):
    @classmethod
    def eval(cls, op1: str, op2: str) -> bool:
        super().eval(op1, op2)
        return op1.startswith(op2)


class matches(BinaryStringOperator):
    @classmethod
    def eval(cls, op1: str, op2: str) -> bool:
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


class UOP:
    @staticmethod
    def exists(elem: Any) -> bool:
        return elem != None


class TransformAttr(Transformer):
    def __init__(self, data: Dict):
        super().__init__(self)
        self.data = data

    def subject_attr(self, args: List) -> Any:
        LOGGER.debug("data is %s", self.data['subject'])
        LOGGER.debug("args are %s", str(args[0]))
        attr_str = str(args[0])
        attr = reduce(
            lambda d, key: d.get(key, None)
            if isinstance(d, Mapping) else None, attr_str.split("."),
            self.data["subject"])
        if attr == None:
            raise SubjectAttributeMissing("No subject_attr %s" % str(args[0]),
                                          args[0])
        return attr

    def access_attr(self, args: List) -> Any:
        attr = reduce(
            lambda d, key: d.get(key, None)
            if isinstance(d, Mapping) else None, args[0].split("."),
            self.data["access"])

        #        attr = self.data["access"].get(str(args[0]), None)
        return attr

    def object_attr(self, args: List) -> Any:
        LOGGER.debug("data is %s", self.data['object'])
        LOGGER.debug("args are %s", args)
        attr_str = str(args[0])
        attr = reduce(
            lambda d, key: d.get(key, None)
            if isinstance(d, Mapping) else None, attr_str.split("."),
            self.data["object"])
        if attr == None:
            raise ObjectAttributeMissing("No object attr %s" % attr_str,
                                         args[0])


#            warnings.warn("No object_attr %s" % str(args[0]),
#                          ObjectAttributeMissingWarning)

        return attr

    def environment_attr(self, args: List) -> Any:
        attr = reduce(
            lambda d, key: d.get(key, None)
            if isinstance(d, Mapping) else None, args[0].split("."),
            self.data["environment"])
        if attr == None:
            raise EnvironmentAttributeMissing(
                "No object attr %s" % str(args[0]), args[0])
            #           warnings.warn("No environment_attr %s" % str(args[0]),
            #              EnvironmentAttributeMissingWarning)

        return attr

    def list_inner(self, args: List) -> Any:
        # either we have two children (one list, one literal) or one child (literal)
        if len(args) == 1:
            return [args[0]]
        return [args[0]] + args[1]

    def lit(self, args: List) -> Union[Dict, List, str, int, float]:
        if isinstance(args[0], (list, )):
            return args[0]
        if args[0].type == "SINGLE_QUOTED_STRING":
            return str(args[0][1:-1])
        if args[0].type == "DOUBLE_QUOTED_STRING":
            return str(args[0][1:-1])
        if args[0].type == "BOOL":
            return args[0] == "True"
        return int(args[0])


class ExistsTransformer(Transformer):
    def __init__(self, attr_transformer: TransformAttr):
        super().__init__(self)
        self.attr_transformer = attr_transformer

    """ The exists Transformer must run before the normal transformers in order to catch exceptions """
    def _exists(self, args: List) -> bool:
        try:
            getattr(self.attr_transformer, args[0].data)(args[0].children)
            return True
        except AttributeMissing:
            return False

    def single(self, args: List) -> Any:
        if args[0] == "exists":
            return self._exists(args[1:])
        return Tree("single", args)

    def uop(self, args: List) -> Any:
        if (args[0] == "exists"):
            return "exists"
        return Tree("uop", args)
        #return getattr(UOP, str(args[0]))


class EvalComplete(Transformer):
    def condition(self, args: List) -> Any:
        if len(args) == 1:
            return args[0]
        raise ValueError
        #return Tree("condition", args)

    def target(self, args: List) -> Any:
        if len(args) == 1:
            return args[0]
        raise ValueError


class EvalTree(Transformer):
    def cbop(self, args: List) -> str:
        return str(args[0])

    def lbop(self, args: List) -> str:
        return str(args[0])

    def statement(self, args: List) -> Any:
        if len(args) == 1:
            return args[0]
        raise ValueError
#        return Tree("statement", args)

    def comparison(self, args: List) -> bool:
        # xor check for none attributes
        if bool(args[0] == None) ^ bool(args[2] == None):
            return False
        op = binary_operators.get(args[1], None)
        if op is None:
            raise NotImplementedError()
#        assert op is not None  # for mypy
        LOGGER.debug("{} {} {}".format(args[0], args[1], args[2]))
        return op.eval(args[0], args[2])

    def linked(self, args: List) -> bool:
        allowed_types = (bool, dict, list, str, float, int)
        if args[0] is None:
            args[0] = False
        if args[1] is None:
            args[1] = False
        if isinstance(args[0], allowed_types) and isinstance(
                args[2], allowed_types):
            if args[1] == "and":
                return bool(args[0] and args[2])
            elif args[1] == "or":
                return bool(args[0] or args[2])
            else:
                raise NotImplementedError
        LOGGER.debug("Types are %s and %s", type(args[0]), type(args[2]))
        raise ValueError


#        return Tree("linked", args)

    def uop(self, args: List) -> Any:
        return getattr(UOP, str(args[0]))

    def single(self, args: List) -> Any:
        if len(args) == 2:
            return args[0](args[1])
        if len(args) == 1:
            return args[0]
        raise ValueError


def parse_and_transform(lark_handle: Lark, rule: str, data: Dict) -> bool:
    try:
        ast = lark_handle.parse(rule)
    except (lark.exceptions.UnexpectedCharacters,
            lark.exceptions.UnexpectedEOF):
        raise BadRuleSyntax('Rule has a bad syntax %s' % rule)
    # Eval exists
    attr_transformer = TransformAttr(data)
    new_ast = ExistsTransformer(attr_transformer).transform(ast)
    T = attr_transformer * EvalTree() * EvalComplete()
    return T.transform(new_ast)


def check_condition(condition: str, data: Dict) -> bool:
    global lark_condition
    LOGGER.debug("Check condition %s with data %s", condition, data)
    ret_value = parse_and_transform(lark_condition, condition, data)
    LOGGER.debug("Condition %s evaluated to %s", condition, ret_value)
    return ret_value


def check_target(rule: str, data: Dict) -> bool:
    global lark_target
    LOGGER.debug("Check target rule %s with data %s", rule, data)
    try:
        ret_value = parse_and_transform(lark_target, rule, data)
    except Exception as e:
        LOGGER.debug(e)
        raise
    LOGGER.debug("Target Rule %s evaluated to %s", rule, ret_value)
    return ret_value


if __name__ == "__main__":
    #
    l = Lark(grammar, start="condition")
    data = {"subject": {"email": "hello"}}
    attr_transformer = TransformAttr(data)
    ast = l.parse("exists subject.email")
    new_ast = ExistsTransformer(attr_transformer).transform(ast)
    print(new_ast)
    T = attr_transformer * EvalTree() * EvalComplete()
    print(T.transform(new_ast))
    ast = l.parse("exists subject.notexisting")
    new_ast = ExistsTransformer(attr_transformer).transform(ast)
    print(new_ast)
    T = attr_transformer * EvalTree() * EvalComplete()
    print(T.transform(new_ast))
    print(ast)
    new_ast = ExistsTransformer(attr_transformer).transform(ast)
    print(new_ast)
    #print(new_ast)
#
#    ast = l.parse("[5, '4', True]")
#    print(ast)
#    #data = {}
#    ast = TransformAttr(data).transform(ast)
#    tree.pydot__tree_to_png(ast, "graph.png")
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
