import logging
import os

LOG_DIR = "logs"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

class LevelFilter(logging.Filter):
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

info_handler = logging.FileHandler(os.path.join(LOG_DIR, "info.log"))
info_handler.setLevel(logging.INFO)
info_handler.addFilter(LevelFilter(logging.INFO))
info_handler.setFormatter(formatter)

warning_handler = logging.FileHandler(os.path.join(LOG_DIR, "warning.log"))
warning_handler.setLevel(logging.WARNING)
warning_handler.addFilter(LevelFilter(logging.WARNING))
warning_handler.setFormatter(formatter)

error_handler = logging.FileHandler(os.path.join(LOG_DIR, "error.log"))
error_handler.setLevel(logging.ERROR)
error_handler.addFilter(LevelFilter(logging.ERROR))
error_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

logger.addHandler(info_handler)
logger.addHandler(warning_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)


def get_logger(name: str):
    return logging.getLogger(name)