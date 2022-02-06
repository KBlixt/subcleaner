from configparser import ConfigParser
from pathlib import Path

from .subtitle import Subtitle
from .sub_block import SubBlock
from re import findall, IGNORECASE, UNICODE
from datetime import timedelta


class Cleaner(object):

    purge_regex: dict
    warning_regex: dict
    exclusive_configs: list

    def __init__(self, regex_dir: Path, use_default_regex: bool):
        self.exclusive_configs = list()
        self._build_regex(regex_dir, use_default_regex)
        print("hello")

    def run_regex(self, subtitle: Subtitle) -> None:
        blocks = subtitle.blocks

        for block in blocks:
            if len(block.content.strip(" -_.")) <= 1:
                block.regex_matches = 3
                continue

            if subtitle.language not in self.purge_regex:
                self._add_language(subtitle.language)

            self._block_regex(block, self.purge_regex[subtitle.language], 3)
            self._block_regex(block, self.warning_regex[subtitle.language], 1)

            if block.regex_matches == 0:
                block.regex_matches = -1

        if len(blocks) >= 10:
            for index in range(0, len(subtitle.blocks)):
                if index < 3 or index > len(subtitle.blocks)-4:
                    subtitle.blocks[index].regex_matches += 1
                    continue
                for block in subtitle.blocks[max(0, index-1): min(index+2, len(subtitle.blocks))]:
                    if block.regex_matches >= 2 and index != block.index - 1:
                        subtitle.blocks[index].regex_matches += 1
                        break

        if len(blocks) >= 100:
            for index in range(0, len(subtitle.blocks)):
                for block in subtitle.blocks[max(0, index-15): min(index+16, len(subtitle.blocks))]:
                    if block.regex_matches >= 3:
                        subtitle.blocks[index].regex_matches += 1
                        break

    @staticmethod
    def _block_regex(block: SubBlock, regex_list: list, punishment: int) -> None:
        clean_content: str = block.content.replace("\n", " ").strip()
        for regex in regex_list:
            result = findall(regex, clean_content, flags=IGNORECASE | UNICODE)
            if result is not None and len(result) > 0:
                block.regex_matches += punishment
                return

    @staticmethod
    def remove_ads(subtitle: Subtitle):
        for block in subtitle.ad_blocks:
            subtitle.remove_block(block)
        for index in range(len(subtitle.blocks)):
            block: SubBlock = subtitle.blocks[index]
            block.index = index+1

    @staticmethod
    def find_ads(subtitle: Subtitle) -> None:

        for index in range(0, len(subtitle.blocks)):
            block: SubBlock = subtitle.blocks[index]

            if block.regex_matches >= 3:
                subtitle.ad_blocks.append(block)
                continue
            elif block.regex_matches == 2:
                subtitle.warning_blocks.append(block)
                continue

            # todo: improve this:
            if index == 0 or index == len(subtitle.blocks)-1:
                continue
            pre_block: SubBlock = subtitle.blocks[index - 1]
            post_block: SubBlock = subtitle.blocks[index + 1]
            if (pre_block.regex_matches >= 3 or index == 0) and \
                    (post_block.regex_matches >= 3 or index == len(subtitle.blocks) - 1):
                if timedelta(seconds=-10) < (block.start_time - pre_block.stop_time) < timedelta(seconds=2.5):
                    subtitle.ad_blocks.append(block)
                    continue
                else:
                    subtitle.warning_blocks.append(block)
                    continue

    @staticmethod
    def fix_overlap(subtitle: Subtitle) -> None:
        if len(subtitle.blocks) < 2:
            return

        margin: timedelta = timedelta(seconds=0.0417)
        previous_block: SubBlock = subtitle.blocks[0]
        for block in subtitle.blocks[1:]:
            block: SubBlock
            stop_time: timedelta = previous_block.stop_time + margin
            start_time: timedelta = block.start_time - margin
            overlap: timedelta = stop_time - start_time
            if overlap.days >= 0 and overlap.microseconds > 3000:
                content_ratio = len(block.content) / (len(block.content) + len(previous_block.content))
                block.start_time += content_ratio * overlap
                previous_block.stop_time += (content_ratio-1) * overlap
            previous_block = block
        return

    def _build_regex(self, regex_dir: Path, use_default_regex: bool) -> None:
        self.purge_regex = dict()
        self.warning_regex = dict()
        if not regex_dir.is_dir():
            return
        if not regex_dir.joinpath("default").is_dir():
            use_default_regex = False

        if use_default_regex:
            for default in regex_dir.joinpath("default").iterdir():
                if default.match("*/[!.]*.conf"):
                    if not any(default.name.lower() == custom.name.lower() for custom in regex_dir.iterdir()):
                        self._add_config(default)

        for custom in regex_dir.iterdir():
            if custom.match("*/[!.]*.conf"):
                self._add_config(custom)

        self._add_exclusive_configs()

    def _add_config(self, regex_config: Path) -> None:
        parser: ConfigParser = ConfigParser()
        parser.read(regex_config, encoding="utf-8")

        if not parser.has_section("META"):
            return

        if parser.has_option("META", "language_codes") and len(parser["META"]["language_codes"]) > 0:
            self._add_inclusive_config(parser)
            return
        self.exclusive_configs.append(parser)

    def _add_inclusive_config(self, parser: ConfigParser) -> None:
        for language in parser["META"].get("language_codes", "").replace(" ", "").split(","):
            if language == "": continue
            self.purge_regex.update({language: []})
            self.warning_regex.update({language: []})

            if parser.has_section("PURGE_REGEX"):
                for key, value in parser.items("PURGE_REGEX"):
                    self.purge_regex[language].append(value)

            if parser.has_section("WARNING_REGEX"):
                for key, value in parser.items("WARNING_REGEX"):
                    self.warning_regex[language].append(value)

    def _add_exclusive_configs(self) -> None:
        for parser in self.exclusive_configs:
            excluded_languages = parser["META"].get("excluded_language_codes").replace(" ", "").split(",")
            if len(excluded_languages) == 1 and excluded_languages[0] == "":
                excluded_languages = []

            for language in self.purge_regex:
                if not any(language == excluded_language for excluded_language in excluded_languages):

                    if parser.has_section("PURGE_REGEX"):
                        for key, value in parser.items("PURGE_REGEX"):
                            self.purge_regex[language].append(value)

                    if parser.has_section("WARNING_REGEX"):
                        for key, value in parser.items("WARNING_REGEX"):
                            self.warning_regex[language].append(value)

    def _add_language(self, language: str) -> None:
        self.purge_regex.update({language: []})
        self.warning_regex.update({language: []})

        for parser in self.exclusive_configs:
            if parser.has_section("PURGE_REGEX"):
                for key, value in parser.items("PURGE_REGEX"):
                    self.purge_regex[language].append(value)

            if parser.has_section("WARNING_REGEX"):
                for key, value in parser.items("WARNING_REGEX"):
                    self.warning_regex[language].append(value)
