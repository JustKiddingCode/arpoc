from lark import Transformer

class CombinedTransformer(Transformer):
    def __init__(self, *transformers):
        self.transformers = transformers

    def __getattr__(self, key):
        for transformer in reversed(self.transformers):
            try:
                return getattr(transformer, key)
            except AttributeError:
                pass
        raise AttributeError()

    def __add__(self, other):
        return CombinedTransformer(*self.transformers, other)

class MyTransformer(Transformer):
    def __add__(self, other):
        return CombinedTransformer(self, other)
