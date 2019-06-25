from enum import Enum
import logging


class LogLevel(Enum):

    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG

    @classmethod
    def get_levels(cls):
        return list(cls.__members__.keys())
