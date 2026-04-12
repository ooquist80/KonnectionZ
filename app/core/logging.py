import logging
import sys
import json


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


class DevelopmentFormatter(logging.Formatter):
    """Human-readable format for development"""
    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def __init__(self):
        super().__init__(fmt=self.fmt, datefmt="%Y-%m-%d %H:%M:%S")


def setup_logging(production: bool = True):
    handler = logging.StreamHandler(sys.stdout)

    if production:
        handler.setFormatter(JsonFormatter())
        log_level = logging.INFO
    else:
        handler.setFormatter(DevelopmentFormatter())
        log_level = logging.DEBUG

    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers = [handler]
