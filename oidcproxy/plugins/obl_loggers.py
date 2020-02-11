from oidcproxy.plugins._lib import Obligation

from oidcproxy.ac.common import Effects

class LogFailed(Obligation):
    name = "obl_log_failed"
    def run(effect : Effects) -> bool:
        if effect == Effects.DENY:
            print("I am an obligation and running :)")
        return True

class LogSuccessful(Obligation):
    name = "obl_log_successful"
    def run(effect : Effects) -> bool:
        if effect == Effects.GRANT:
            print("I am an obligation and running :)")
        return True


