from oidcproxy.plugins._lib import Obligation, Optional

from oidcproxy.ac.common import Effects

from typing import Dict

class LogFailed(Obligation):
    name = "obl_log_failed"
    
    @staticmethod
    def run(effect : Optional[Effects], context: Dict, cfg: Dict) -> bool:
        if effect == Effects.DENY:
            print("I am an obligation and running :)")
        return True

class LogSuccessful(Obligation):
    name = "obl_log_successful"
    @staticmethod
    def run(effect : Optional[Effects], context: Dict, cfg: Dict) -> bool:
        if effect == Effects.GRANT:
            print("I am an obligation and running :)")
        return True


