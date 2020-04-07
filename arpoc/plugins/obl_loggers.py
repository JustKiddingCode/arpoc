import re
from collections.abc import Mapping
from functools import reduce
from copy import deepcopy

from arpoc.plugins._lib import Obligation, Optional, deep_dict_update

from arpoc.ac.common import Effects

from typing import Dict


import logging
"""
Obligation Log Module.
The classes here will either
  - log every access (Log),
  - every granted access (LogSuccessful)
  - every denied access (LogFailed)

The log can be configured via a dict cfg:
    cfg['loggercfg'] -- the logger cfg of the python logging module
    cfg['formatstring'] -- A format string for the message generation
The log will be created with INFO level
"""

logger_cfg = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "obligation_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "obligation.log",
            "maxBytes": 1024,
            "backupCount": 3,
            "level": "INFO",
        }
    },
    "loggers": {
        "obligation_logger": {
            "level": "INFO",
            "handlers": ["obligation_file"]
        }
    }
}


class Log(Obligation):
    name = "obl_log"

    @staticmethod
    def replace_subjectattr(logtext, subject_info):
        regex = r"subject\.(?P<subject>[.\w]+)"
        func = lambda x: reduce(
            lambda d, key: d.get(key, None)
            if isinstance(d, Mapping) else None,
            x.group('subject').split("."), subject_info)
        return re.sub(regex, func, logtext)

    @staticmethod
    def replace_objectattr(logtext, object_info):
        regex = r"object\.(?P<object>[.\w]+)"
        func = lambda x: reduce(
            lambda d, key: d.get(key, None)
            if isinstance(d, Mapping) else None,
            x.group('object').split("."), object_info)
        return re.sub(regex, func, logtext)

    @staticmethod
    def replace_envattr(logtext, env_info):
        regex = r"environment\.(?P<env>[.\w]+)"
        func = lambda x: reduce(
            lambda d, key: d.get(key, None)
            if isinstance(d, Mapping) else None,
            x.group('env').split("."), env_info)
        return re.sub(regex, func, logtext)

    @staticmethod
    def replace_accessattr(logtext, access_info):
        regex = r"access\.(?P<access>[.\w]+)"
        func = lambda x: reduce(
            lambda d, key: d.get(key, None)
            if isinstance(d, Mapping) else None,
            x.group('access').split("."), access_info)
        return re.sub(regex, func, logtext)

    @staticmethod
    def replace_attr(logtext, context):
        logtext = Log.replace_subjectattr(logtext, context['subject'])
        logtext = Log.replace_objectattr(logtext, context['object'])
        logtext = Log.replace_envattr(logtext, context['environment'])
        logtext = Log.replace_accessattr(logtext, context['access'])

        return logtext

    @staticmethod
    def run(effect: Optional[Effects], context: Dict, cfg: Dict) -> bool:
        if 'logger_cfg' in cfg:
            copy_logger_cfg = deepcopy(logger_cfg)
            merged_cfg = deep_dict_update(copy_logger_cfg, cfg['logger_cfg'])
        else:
            merged_cfg = deepcopy(logger_cfg)
        logger = logging.getLogger("obligation_logger")
        logging.config.dictConfig(merged_cfg)

        if 'log_format' in cfg:
            log_format = cfg['log_format']
        else:
            log_format = "{} subject.email accessed object.service [object.path] -- object.target_url"

        log_format = log_format.format(str(effect))
        logger.info(Log.replace_attr(log_format, context))
        return True


class LogFailed(Obligation):
    name = "obl_log_failed"

    @staticmethod
    def run(effect: Optional[Effects], context: Dict, cfg: Dict) -> bool:
        if effect == Effects.DENY:
            Log.run(effect, context, cfg)
        return True


class LogSuccessful(Obligation):
    name = "obl_log_successful"

    @staticmethod
    def run(effect: Optional[Effects], context: Dict, cfg: Dict) -> bool:
        if effect == Effects.GRANT:
            Log.run(effect, context, cfg)
        return True
