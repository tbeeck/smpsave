
import logging
import os
from logging.handlers import RotatingFileHandler

_COLORS = {
    "reset": "\x1b[0m",
    "grey": "\x1b[30;1m",
    "blackbg": "\x1b[40;1m",
    "magenta": "\x1b[35m",
    "redbg": "\x1b[41m",
    "lightblue": "\x1b[34;1m",
    "lightyellow": "\x1b[33;1m",
    "red": "\x1b[31m",
}


def file_handler() -> RotatingFileHandler:
    log_directory = "logs"
    os.makedirs(log_directory, exist_ok=True)

    handler = RotatingFileHandler(os.path.join(
        log_directory, "smps.log"), maxBytes=10000, backupCount=10)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(module)s %(message)s"))
    return handler


def configure_logging(level: int = logging.INFO,
                      use_file_handler: bool = False):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(Formatter())
    root_logger.addHandler(stream_handler)

    if use_file_handler:
        root_logger.addHandler(file_handler())


class Formatter(logging.Formatter):
    """ Acknowledement: Derived from discord.py's logging formatter """

    LEVELS = [
        (logging.DEBUG, _COLORS['blackbg']),
        (logging.INFO, _COLORS['grey']),
        (logging.WARNING, _COLORS['lightyellow']),
        (logging.ERROR, _COLORS['red']),
        (logging.CRITICAL, _COLORS['redbg']),
    ]

    FORMATS = {
        level: logging.Formatter(
            fmt=f"{_COLORS['grey']}%(asctime)s{_COLORS['reset']} {level_color}%(levelname)s{_COLORS['reset']} {_COLORS['magenta']}%(module)s{_COLORS['reset']}  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        for level, level_color in LEVELS
    }

    def format(self, record: logging.LogRecord):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f"{_COLORS['red']}{text}{_COLORS['reset']}"

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output
