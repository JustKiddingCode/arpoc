
from oidcproxy.plugins._lib import Obligation

class OblDummy(Obligation):
    name = "obl_dummy"

    @staticmethod
    def run(effect, context, cfg):
        return True
