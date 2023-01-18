import logging
from configparser import ConfigParser
from pathlib import Path
from typing import Optional

import libs
from libs.subcleaner import languages

logger = logging.getLogger(__name__)

home_dir = Path(libs.__file__).parent.parent
try:
    home_dir = home_dir.relative_to(Path.cwd())
except ValueError:
    pass

regex_dir = home_dir.joinpath("regex_profiles")
default_regex_dir = regex_dir.joinpath("default")
script_file = home_dir.joinpath('subcleaner.py')

log_file: Path
use_default_regex: bool
fix_overlaps: bool
relative_base: Path
default_language: Optional[str]
config_file = home_dir.joinpath("subcleaner.conf")

if not config_file.is_file():
    config_file.write_text(home_dir.joinpath("default_config", "subcleaner.conf").read_text())

cfg = ConfigParser()
cfg.read(str(config_file), encoding="UTF-8")

use_default_regex = cfg['SETTINGS'].getboolean("use_defaults", True)

sections = cfg.sections()

log_dir = Path(cfg["SETTINGS"].get("log_dir", "logs/"))
if not log_dir.is_absolute():
    log_dir = home_dir.joinpath(log_dir)
if not log_dir.exists():
    log_dir.mkdir()
if not log_dir.is_dir():
    raise ValueError(f"log directory: {log_dir} is not a directory")
log_file = log_dir.joinpath("subcleaner.log")

relative_base = Path(cfg['SETTINGS'].get("relative_path_base", "."))
if not relative_base.is_absolute():
    relative_base = Path.cwd().joinpath(relative_base)
relative_base = relative_base.resolve()

fix_overlaps = cfg['SETTINGS'].getboolean("fix_overlaps", True)

default_language = cfg['SETTINGS'].get("default_language", "")
if default_language in ["blank", "Blank", "", "empty", "Empty"]:
    default_language = None
if default_language:
    if not languages.is_language(default_language):
        logger.error("Config error: default language code must be a valid ISO:639 language. Exiting")
        exit(1)

use_english_on_all = cfg['SETTINGS'].getboolean("use_english_on_all", False)
require_language_profile = cfg['SETTINGS'].getboolean("require_language_profile", True)
