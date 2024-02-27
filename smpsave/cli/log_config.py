
import logging
import os
from logging.handlers import RotatingFileHandler


def stream_handler() -> logging.StreamHandler:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    return handler


def file_handler() -> RotatingFileHandler:
    log_directory = "logs"
    os.makedirs(log_directory, exist_ok=True)

    handler = RotatingFileHandler(os.path.join(log_directory, "smps.log"))
    handler.setLevel(logging.DEBUG)
    return handler
