import dataclasses
import logging
from typing import Optional

from . import util, args, config, languages
from .sub_block import SubBlock, ParsingException
from libs import langdetect
from pathlib import Path

logger = logging.getLogger("subtitle")


@dataclasses.dataclass()
class Subtitle(object):
    blocks: list[SubBlock]
    ad_blocks: list[SubBlock]
    warning_blocks: list[SubBlock]
    language: Optional[str]
    file: Path

    def __init__(self, subtitle_file: Path) -> None:
        self.file = subtitle_file
        self.blocks = []
        self.ad_blocks = []
        self.warning_blocks = []

        try:
            self.file = self.file.relative_to(config.relative_base)
        except ValueError:
            pass

        file_content = util.read_file(subtitle_file)
        try:
            self._parse_file_content(file_content)
        except ParsingException as e:
            e.subtitle_file = subtitle_file
            raise e

        if not self:
            raise SubtitleContentException(subtitle_file)

        self.language = args.language
        if not self.language:
            self.determine_language()
        if not self.language_is_correct():
            logger.warning(f"the language within the file does not match the file label: '{self.language}'")

        if args.destroy_list:
            self.mark_blocks_for_deletion(args.destroy_list)

    def _parse_file_content(self, file_content: str) -> None:
        raw_blocks = file_content.split("\n\n")

        for raw_block in raw_blocks:
            if raw_block:
                self.blocks.append(SubBlock(raw_block))

    def mark_blocks_for_deletion(self, purge_list: list[int]) -> None:
        for index in purge_list:
            if index-1 >= len(self.blocks):
                continue
            self.blocks[index-1].regex_matches = 3

    def language_is_correct(self) -> bool:
        if self.language == "und":
            return True  # unknown language.
        language_code_2 = languages.get_2letter_code(self.language)

        if not language_code_2:
            return True  # unknown language.

        sub_content: str = ""
        for block in self.blocks:
            sub_content += block.content

        if len(sub_content) < 200:
            return True  # not enough content to estimate language.
        detected_language = langdetect.detect_langs(sub_content)[0]

        return detected_language.lang == language_code_2 and detected_language.prob > 0.8

    def determine_language(self) -> None:
        if config.default_language:
            self.language = config.default_language
            return

        self.language = "und"

        for suffix in self.file.suffixes[-3:-1]:
            parsed_lang = suffix.replace(":", "-").replace("_", "-").split("-")[0]
            if languages.is_language(parsed_lang):
                self.language = parsed_lang
                return

        sub_content: str = ""
        for block in self.blocks:
            sub_content += block.content
        if len(sub_content) < 200:
            return
        detected_language = langdetect.detect_langs(sub_content)[0]
        if detected_language.prob > 0.9:
            self.language = detected_language.lang

    def to_content(self) -> str:
        content = ""
        index = 1
        for block in self.blocks:
            content += f"{index}\n" \
                       f"{block}\n" \
                       f"\n"
            index += 1
        return content[:-1]

    def get_warning_indexes(self) -> list[str]:
        l: list[str] = []
        for block in self.warning_blocks:
            l.append(str(self.index_of(block)))
        return l

    def index_of(self, block: SubBlock) -> int:
        return self.blocks.index(block) + 1

    def dedupe_warning_blocks(self) -> None:
        self.warning_blocks[:] = [block for block in self.warning_blocks if block not in self.ad_blocks]

    def __str__(self) -> str:
        return str(self.file)

    def __len__(self) -> int:
        return len(self.blocks)

    def __bool__(self) -> bool:
        for block in self.blocks:
            if block.content:
                return True
        return False


class SubtitleContentException(Exception):
    subtitle_file: str

    def __init__(self, subtitle_file):
        self.subtitle_file = subtitle_file

    def __str__(self) -> str:
        return f"File {self.subtitle_file} is empty."
