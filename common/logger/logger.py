import logging
import os
import sys
import tqdm
from logging.handlers import RotatingFileHandler
from common.config import config

_LOG_FORMAT = '%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s'

if not os.path.exists(config.TEMP_FOLDER):
    os.makedirs(config.TEMP_FOLDER)

std_handler = logging.StreamHandler(sys.stdout)
std_handler.setFormatter(logging.Formatter(_LOG_FORMAT))

file_handler = RotatingFileHandler(config.LOG_FILE,
                                   maxBytes=10 * 1_000_000,  # 10MB
                                   backupCount=5,
                                   encoding="utf-8")

file_handler.setFormatter(logging.Formatter(_LOG_FORMAT))

class TqdmLoggingHandler(logging.Handler):
    """
    Logging handler that wraps tqdm so it can show a progress bar while other
    messages keep being logged.
    """

    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)

log = logging.getLogger(__name__)
log.setLevel(config.LOG_LEVEL.upper())
log.addHandler(TqdmLoggingHandler())

#log.addHandler(std_handler)
log.addHandler(file_handler)
