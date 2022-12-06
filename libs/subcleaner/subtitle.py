from .sub_block import SubBlock
from libs import langdetect
from pathlib import Path


class Subtitle(object):
    blocks: list
    ad_blocks: list
    warning_blocks: list
    language: str
    file: Path

    def __init__(self, subtitle_file: Path, language: str, destroy_list: list):
        self.blocks: list = list()
        self.ad_blocks = []
        self.warning_blocks = []
        self.language = language
        self.file = subtitle_file

        try:
            with subtitle_file.open("r", encoding="utf-8") as file:
                self._parse_file(file.read())
        except UnicodeDecodeError:
            with subtitle_file.open("r", encoding="cp1252") as file:
                self._parse_file(file.read())
        
        for block in self.blocks:
            if block.content:
                break
        else:
            raise ParsingException(f"srt file does not contain anything")

        if destroy_list is not None:
            for index in destroy_list:
                if index-1 < len(self.blocks):
                    self.blocks[index-1].regex_matches = 3

    def add_block(self, block: SubBlock) -> None:
        self.blocks.append(block)

    def remove_block(self, block: SubBlock) -> None:
        if block is not None:
            try:
                self.blocks.remove(block)
            except ValueError:
                pass

    def check_language(self) -> bool:
        sub_content: str = ""
        for block in self.blocks:
            sub_content += block.content
        if len(sub_content) < 100:
            return True
        detected_language = langdetect.detect_langs(sub_content)[0]
        return detected_language.lang == self.language and detected_language.prob > 0.8

    def _parse_file(self, file_content: str) -> None:
        current_index = 1
        block = SubBlock(current_index)
        try:
            for line in file_content.split("\n"):
                if len(line) == 0:
                    if block.stop_time is not None:
                        self.blocks.append(block)
                        current_index += 1
                        block = SubBlock(current_index)
                    continue

                if " --> " in line and block.stop_time is None:
                    start_string = line.split(" --> ")[0].rstrip()[:12]
                    block.set_start_time(start_string)

                    stop_string = line.split(" --> ")[1].rstrip()[:12]
                    block.set_stop_time(stop_string)
                    continue

                if block.stop_time is not None:
                    block.content = block.content + line + "\n"''
            if block.stop_time is not None:
                self.blocks.append(block)
        except Exception as e:
            raise ParsingException(f"srt file not correctly formatted at index {current_index}", current_index)

    def __repr__(self):
        sub_file_content = ""
        for i in range(len(self.blocks)):
            sub_file_content += (str(i+1) + "\n")
            sub_file_content += (str(self.blocks[i]))
            sub_file_content += "\n"
        return sub_file_content[:-1]

    def determine_language(self):
        if len(self.file.name.split(".")) > 2:
            self.language = self.file.name.split(".")[1]
        else:
            sub_content: str = ""
            for block in self.blocks:
                sub_content += block.content
            if len(sub_content) < 100:
                self.language = "unknown"
                return
            detected_language = langdetect.detect_langs(sub_content)[0]
            if detected_language.prob > 0.8:
                self.language = detected_language.lang
            else:
                self.language = "unknown"


class ParsingException(Exception):
    block_index: int
    subtitle_file: str
    message:str

    def __init__(self, message, block_index):
        self.message = message
        self.block_index = block_index

    def __str__(self) -> str:
        return f"Parsing error at block {self.block_index} in file {self.subtitle_file}."
