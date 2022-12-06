import logging.handlers
import sys
from . import args
from . import config

# formatters
time_formatter = logging.Formatter("{asctime} - {levelname:>8}: {message}", style="{", datefmt='%Y-%m-%d_%H:%M:%S')
formatter = logging.Formatter("{levelname:>8}: {message}", style="{",)

# handlers
file_handler = logging.handlers.RotatingFileHandler(config.log_file, maxBytes=1_000_000, backupCount=10)
file_handler.setFormatter(time_formatter)
file_handler.setLevel(logging.INFO)
if args.no_log:
    file_handler.setLevel(logging.CRITICAL + 1)

stout_handler = logging.StreamHandler(sys.stdout)
stout_handler.setFormatter(formatter)
stout_handler.setLevel(logging.INFO)
if args.silent:
    stout_handler.setLevel(logging.CRITICAL + 1)

# loggers
base_logger = logging.getLogger()
base_logger.setLevel(logging.INFO)
base_logger.handlers.clear()

base_logger.addHandler(stout_handler)
base_logger.addHandler(file_handler)
