from __future__ import annotations

import configparser
import dataclasses
from pathlib import Path
from typing import List, Dict

from libs.subcleaner import config
import logging

logger = logging.getLogger("regex")

global_profiles: List[GlobalProfile] = []
purge_regex: Dict[str, List[str]] = {}
warning_regex: Dict[str, List[str]] = {}


def get_purge_regex(language: str):
    if language not in purge_regex:
        _create_language(language)
    return purge_regex[language]


def get_warning_regex(language: str):
    if language not in warning_regex:
        _create_language(language)
    return warning_regex[language]


@dataclasses.dataclass
class GlobalProfile:
    excluded_languages: List[str]
    purge_regex_lines: List[str]
    warning_regex_lines: List[str]

    def __init__(self, parser) -> None:
        self.purge_regex_lines = list(parser["PURGE_REGEX"].values())
        self.warning_regex_lines = list(parser["WARNING_REGEX"].values())

        self.excluded_languages = parser["META"].get("excluded_language_codes", "").replace(" ", "").split(",")
        for language in self.excluded_languages:
            if not language:
                self.excluded_languages.remove(language)

        for language in purge_regex:
            if any(language == excluded_language for excluded_language in self.excluded_languages):
                continue
            purge_regex[language] += self.purge_regex_lines
            warning_regex[language] += self.warning_regex_lines


def _load_profile(profile_file: Path) -> None:
    parser = configparser.ConfigParser()

    try:
        parser.read(profile_file)

        languages = parser["META"].get("language_codes", "").replace(" ", "")

        if "excluded_language_codes" in parser["META"].keys() or not languages:
            global_profiles.append(GlobalProfile(parser))
            return

        for language in languages.split(","):
            if language not in purge_regex:
                _create_language(language)
            purge_regex[language] += list(parser["PURGE_REGEX"].values())
            warning_regex[language] += list(parser["WARNING_REGEX"].values())

    except Exception:
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
                _load_profile(default_profile_file)
    for profile_file in config.regex_dir.iterdir():
        if profile_file.is_file() and not profile_file.name.startswith(".") and profile_file.suffix == ".conf":
            for default_profile_file in config.default_regex_dir.iterdir():

                if default_profile_file.name == profile_file.name:
                    break
            else:
                _load_profile(profile_file)


_load_regex()
