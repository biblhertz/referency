import logging
from common.logger import log

# suppress logging when running tests
log.setLevel(logging.CRITICAL)