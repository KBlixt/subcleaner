import configparser
import re
from pathlib import Path
from typing import List, Dict, Tuple, Pattern

from libs.subcleaner.settings import config
import logging

logger = logging.getLogger(__name__)

global_profiles: List["GlobalProfile"] = []
purge_regex: Dict[str, List[Tuple[str, Pattern]]] = {}
warning_regex: Dict[str, List[Tuple[str, Pattern]]] = {}


def language_has_profile(language: str):
    return language in purge_regex


def get_purge_regex(language: str) -> List[Tuple[str, Pattern]]:
    if language in purge_regex:
        return purge_regex[language]
    return purge_regex["no_profile"]


def get_warning_regex(language: str) -> List[Tuple[str, Pattern]]:
    if language in warning_regex:
        return warning_regex[language]
    return warning_regex["no_profile"]


class GlobalProfile:
    excluded_languages: List[str]
    purge_regex_lines: List[Tuple[str, Pattern]]
    warning_regex_lines: List[Tuple[str, Pattern]]

    def __init__(self, parser, default: bool) -> None:
        self.purge_regex_lines = []
        self.warning_regex_lines = []

        for key, value in list(parser["PURGE_REGEX"].items()):
            if not default:
                key = key + "*"
            value = f"({value})"
            compiled_regex = re.compile(value, flags=re.IGNORECASE | re.UNICODE)
            self.purge_regex_lines.append((key, compiled_regex))
        for key, value in list(parser["WARNING_REGEX"].items()):
            if not default:
                key = key + "*"
            value = f"({value})"
            compiled_regex = re.compile(value, flags=re.IGNORECASE | re.UNICODE)
            self.warning_regex_lines.append((key, compiled_regex))

        self.excluded_languages = parser["META"].get("excluded_language_codes", "").replace(" ", "").split(",")
        for language in self.excluded_languages:
            if not language:
                self.excluded_languages.remove(language)

        for language in purge_regex:
            if any(language == excluded_language for excluded_language in self.excluded_languages):
                continue
            purge_regex[language] += self.purge_regex_lines
            warning_regex[language] += self.warning_regex_lines


def _load_profile(profile_file: Path, default: bool = True) -> None:
    parser = configparser.ConfigParser()

    try:
        parser.read(profile_file, encoding="utf-8")

        languages = parser["META"].get("language_codes", "").replace(" ", "")

        if "excluded_language_codes" in parser["META"].keys() or not languages:
            global_profiles.append(GlobalProfile(parser, default))
            return
        if config.use_english_on_all and default and profile_file.name == "english.conf":
            global_profiles.append(GlobalProfile(parser, default))
            for language in languages.split(","):
                if language not in purge_regex:
                    _create_language(language)
            return

        for language in languages.split(","):
            if language not in purge_regex:
                _create_language(language)
            for key, value in list(parser["PURGE_REGEX"].items()):
                if not default:
                    key = key + "*"
                value = f"({value})"
                compiled_regex = re.compile(value, flags=re.IGNORECASE | re.UNICODE)
                purge_regex[language].append((key, compiled_regex))
            for key, value in list(parser["WARNING_REGEX"].items()):
                if not default:
                    key = key + "*"
                value = f"({value})"
                compiled_regex = re.compile(value, flags=re.IGNORECASE | re.UNICODE)
                warning_regex[language].append((key, compiled_regex))

    except Exception as e:
        logger.error(f"Incorrectly configured regex language profile: {profile_file.name}")
        exit(1)


def _create_language(language: str) -> None:
    purge_regex[language] = []
    warning_regex[language] = []

    for global_profile in global_profiles:
        if any(language == excluded_language for excluded_language in global_profile.excluded_languages):
            continue
        purge_regex[language] += global_profile.purge_regex_lines
        warning_regex[language] += global_profile.warning_regex_lines


def _load_regex():
    for default_profile_file in config.default_regex_dir.iterdir():
        if default_profile_file.is_file() and not default_profile_file.name.startswith(".") and default_profile_file.suffix == ".conf":
            for profile_file in config.regex_dir.iterdir():

                if default_profile_file.name == profile_file.name:
                    _load_profile(profile_file)
                    break
            else:
                _load_profile(default_profile_file, default=True)
    for profile_file in config.regex_dir.iterdir():
        if profile_file.is_file() and not profile_file.name.startswith(".") and profile_file.suffix == ".conf":
            for default_profile_file in config.default_regex_dir.iterdir():

                if default_profile_file.name == profile_file.name:
                    break
            else:
                _load_profile(profile_file)


_load_regex()
