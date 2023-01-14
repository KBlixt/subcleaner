import json
from pathlib import Path
from typing import Optional, List, Dict

languages_json_file = Path(__file__).parent.joinpath("languages.json")

_languages: List[Dict[str, str]]
_language_names: List[str] = []
_language_codes_2: List[str] = []
_language_codes_3: List[str] = []


def load_language_data() -> None:
    with open(languages_json_file, encoding="UTF-8") as json_file:
        global _languages
        _languages = json.load(json_file)
        for language in _languages:
            _language_names.append(language["name"])
            language["name"] = language["name"].lower().replace(" ", "_")
            if "alpha_2" in language:
                _language_codes_2.append(language["alpha_2"])
            if "alpha_3" in language:
                _language_codes_3.append(language["alpha_3"])


def is_language(lang: str) -> bool:
    if len(lang) == 2:
        return lang in _language_codes_2
    if len(lang) == 3:
        return lang in _language_codes_3
    return lang in _language_names


def get_2letter_code(lang: str) -> Optional[str]:
    if len(lang) == 2:
        if is_language(lang):
            return lang
        return None

    if len(lang) == 3:
        code_type = "alpha_3"
    else:
        code_type = "name"

    lang = lang.lower().replace(" ", "_")
    for language in _languages:
        if language[code_type] == lang:
            if "alpha_2" in language:
                return language["alpha_2"]
            return None


load_language_data()
