from oidcproxy.plugins.obl_loggers import *
from oidcproxy.ac.common import Effects

new_cfg = {
    "handlers": {
        "obligation_file": None
    },
    "loggers": {
        "obligation_logger": {
            "handlers": []
        }
    }
}


def test_replace_attr():
    context = {
        'subject': {
            'test': 'foo'
        },
        'object': {
            'test': 'bar'
        },
        'environment': {
            'test': 'bla'
        },
        'access': {
            'test': 'blub'
        }
    }
    logtext = "subject.test object.test environment.test access.test"
    assert Log.replace_attr(logtext, context) == "foo bar bla blub"


def test_log_run(caplog):
    context = {
        'subject': {
            'email': 'test@example.com'
        },
        'object': {
            'path': '/',
            'target_url': 'FQDN',
            'service': 'Service A'
        },
        'environment': {
            'test': 'bla'
        },
        'access': {
            'test': 'blub'
        }
    }
    Log.run(Effects.GRANT, context, new_cfg)
    assert "GRANT test@example.com accessed Service A [/] -- FQDN" in caplog.text

def test_logfailed(caplog):
    context = {
        'subject': {
            'email': 'test@example.com'
        },
        'object': {
            'path': '/',
            'target_url': 'FQDN',
            'service': 'Service A'
        },
        'environment': {
            'test': 'bla'
        },
        'access': {
            'test': 'blub'
        }
    }
    LogFailed.run(Effects.GRANT, context, new_cfg)
    assert "GRANT test@example.com accessed Service A [/] -- FQDN" not in caplog.text
    LogFailed.run(Effects.DENY, context, new_cfg)
    assert "DENY test@example.com accessed Service A [/] -- FQDN" in caplog.text

def test_logsuccessful(caplog):
    context = {
        'subject': {
            'email': 'test@example.com'
        },
        'object': {
            'path': '/',
            'target_url': 'FQDN',
            'service': 'Service A'
        },
        'environment': {
            'test': 'bla'
        },
        'access': {
            'test': 'blub'
        }
    }
    LogSuccessful.run(Effects.GRANT, context, new_cfg)
    assert "GRANT test@example.com accessed Service A [/] -- FQDN" in caplog.text
    LogSuccessful.run(Effects.DENY, context, new_cfg)
    assert "DENY test@example.com accessed Service A [/] -- FQDN" not in caplog.text
