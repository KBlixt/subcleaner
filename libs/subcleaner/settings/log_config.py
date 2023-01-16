import logging.handlers
import sys
from . import args, config

# formatters
time_formatter = logging.Formatter("{asctime} - {levelname:>8}: {message}", style="{", datefmt='%Y-%m-%d_%H:%M:%S')
formatter = logging.Formatter("{levelname:>8}: {message}", style="{",)

base_logger = logging.getLogger()
base_logger.setLevel(logging.INFO)
base_logger.handlers.clear()

# file handler
if not args.no_log:
    file_handler = logging.handlers.RotatingFileHandler(config.log_file, maxBytes=10_000_000, backupCount=10, encoding='utf8')
    file_handler.setFormatter(time_formatter)
    file_handler.setLevel(logging.INFO)
    if args.errors_only:
        file_handler.setLevel(logging.ERROR)
    base_logger.addHandler(file_handler)

# stdout handler
stout_handler = logging.StreamHandler(sys.stdout)
stout_handler.setFormatter(formatter)
stout_handler.setLevel(logging.INFO)
if args.silent:
    stout_handler.setLevel(logging.WARNING)
if args.errors_only:
    stout_handler.setLevel(logging.ERROR)
base_logger.addHandler(stout_handler)
