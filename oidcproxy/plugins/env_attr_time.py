from . import _lib

class EnvAttrTime(_lib.EnvironmentAttribute):
    target = "time"
    
    @staticmethod
    def run():
        return "16:05"

class EnvAttrTimeHour(_lib.EnvironmentAttribute):
    target = "time_hour"
    
    @staticmethod
    def run():
        return "16"
