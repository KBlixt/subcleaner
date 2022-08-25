import dataclasses
from typing import Optional

from . import util
from .sub_block import SubBlock
from libs import langdetect
from pathlib import Path


@dataclasses.dataclass()
class Subtitle(object):
    blocks: list[SubBlock]
    ad_blocks: list[SubBlock]
    warning_blocks: list[SubBlock]
    language: Optional[str]
    file: Path

    def __init__(self, subtitle_file: Path, purge_list: Optional[list[int]] = None, language: Optional[str] = None) -> None:
        self.file = subtitle_file
        self.language = language

        self.blocks = []
        self.ad_blocks = []
        self.warning_blocks = []

        file_content = util.read_file(subtitle_file)
        try:
            self._parse_file_content(file_content)
        except ParsingException as e:
            e.subtitle_file = subtitle_file
            raise e

        if purge_list:
            self.mark_blocks_for_deletion(purge_list)

    def _parse_file_content(self, file_content: str) -> None:
        raw_blocks = file_content.split("\n\n")

        for raw_block in raw_blocks:
            if raw_block:
                self.blocks.append(SubBlock(raw_block))

    def mark_blocks_for_deletion(self, purge_list: list[int]):
        for index in purge_list:
            if index-1 >= len(self.blocks):
                continue
            self.blocks[index-1].regex_matches = 3

    def language_is_correct(self) -> bool:
        if not self.language:
            raise ValueError(f"Missing language code for: {self}")
        if self.language != 2:
            raise ValueError(f"incorrect language code for: {self}")

        sub_content: str = ""
        for block in self.blocks:
            sub_content += block.content
        detected_language = langdetect.detect_langs(sub_content)[0]
        return detected_language.lang == self.language and detected_language.prob > 0.8

    def determine_language(self, use_detector: bool) -> None:
        if len(self.file.name.split(".")) > 2:
            if len(self.file.name.split(".")[-2]) == 2:
                self.language = self.file.name.split(".")[-2]
                return

        if not use_detector:
            return

        sub_content: str = ""
        for block in self.blocks:
            sub_content += block.content
        detected_language = langdetect.detect_langs(sub_content)[0]
        if detected_language.prob > 0.9:
            self.language = detected_language.lang

    def to_content(self) -> str:
        content = ""
        index = 1
        for block in self.blocks:
            content += f"{index}\n" \
                       f"{block}\n\n"
            index += 1
        return content[:-1]

    def __str__(self):
        return str(self.file)


class ParsingException(Exception):
    block_index: int
    subtitle_file: str

    def __init__(self, block_index):
        self.block_index = block_index

    def __str__(self) -> str:
        return f"Parsing error at block {self.block_index} in file {self.subtitle_file}."
