from abc import ABC


class EnvironmentAttribute(ABC):
    target = ""

    @staticmethod
    def run():
        return None


class ObjectSetter(ABC):
    name = ""

    def __init__(self, cfg):
        pass

    def run(self, data):
        return None
