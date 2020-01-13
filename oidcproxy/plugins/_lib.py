from abc import ABC


class EnvironmentAttribute(ABC):
    target = None

    def run():
        return None

class ObjectSetter(ABC):
    name = None

    def __init__(self,cfg):
        pass

    def run(self, data):
        return None
