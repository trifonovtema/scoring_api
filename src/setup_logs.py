import logging
import sys
import logging.config


from src.settings import LogSettings


def setup_logging():
    if LogSettings.LOG_FILE_PATH is not None:
        handlers = {
            "file": {
                "class": "logging.FileHandler",
                "formatter": "default",
                "level": "INFO",
                "filename": LogSettings.LOG_FILE_PATH,
            }
        }
    else:
        handlers = {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "INFO",
                "stream": sys.stdout,
            }
        }

    log_config = {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname).1s %(message)s",
                "datefmt": "%Y.%m.%d %H:%M:%S",
            }
        },
        "handlers": handlers,
        "root": {
            "level": "INFO",
            "handlers": list(handlers.keys()),
        },
        "disable_existing_loggers": False,
    }

    logging.config.dictConfig(log_config)
