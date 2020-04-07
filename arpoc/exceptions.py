class OIDCProxyException(Exception):
    pass


class ACEntityMissing(OIDCProxyException):
    pass


class AttributeMissing(OIDCProxyException):
    pass


class SubjectAttributeMissing(AttributeMissing):
    def __init__(self, message: str, attr: str) -> None:
        super().__init__(self, message)
        self.attr = attr


class ObjectAttributeMissing(AttributeMissing):
    pass


class EnvironmentAttributeMissing(AttributeMissing):
    pass


class BadRuleSyntax(Exception):
    pass


class BadSemantics(Exception):
    pass


class DuplicateKeyError(OIDCProxyException):
    pass


class ConfigError(OIDCProxyException):
    pass
