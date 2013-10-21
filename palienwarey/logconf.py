import logging

from .constants import LOG_FORMATTERS, STRING_LOG_LEVEL_MAP, MESSAGES_MAP


__all__ = ['STRING_LOG_LEVEL_MAP', 'LOG_FORMATTERS', 'handler', 'logger',
           'log_error_code']


formatter = logging.Formatter(LOG_FORMATTERS['simple'])

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

logger = logging.getLogger('palienwarey')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def set_log_level(log_level):
    """
    Sets logging level from user string.
    """
    logging_level = STRING_LOG_LEVEL_MAP.get(log_level, logging.INFO)
    logger.setLevel(logging_level)


def set_log_formatter(verbosity):
    """
    Sets log formatter from user string.
    """
    formatter = logging.Formatter(LOG_FORMATTERS.get(verbosity, 'simple'))
    handler.setFormatter(formatter)


def log_error_code(code):
    """
    Logs an error message for given code and returns it.
    """
    logger.error(MESSAGES_MAP.get(code, 'Unknown error'))
    return code
