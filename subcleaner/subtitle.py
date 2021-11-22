from .sub_block import SubBlock
from libs.langdetect import detect_langs
from pathlib import Path


class Subtitle(object):
    blocks: list
    ad_blocks: list
    warning_blocks: list

    def __init__(self, subtitle_file: Path, destroy_list: list):
        self.blocks: list = list()
        self.ad_blocks = []
        self.warning_blocks = []

        with subtitle_file.open("r") as file:
            self._parse(file.read())

        if destroy_list is not None:
            for index in destroy_list:
                self.blocks[index-1].regex_matches = 3

    def add_block(self, block: SubBlock) -> None:
        self.blocks.append(block)

    def remove_block(self, block: SubBlock) -> None:
        if block is not None:
            try:
                self.blocks.remove(block)
            except ValueError:
                pass

    def check_language(self, language) -> bool:
        sub_content: str = ""
        for block in self.blocks:
            sub_content += block.content
        detected_language = detect_langs(sub_content)[0]
        return detected_language.lang == language and detected_language.prob > 0.8

    def _parse(self, file_content: str) -> None:
        current_index = 1
        block = SubBlock(current_index)
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

    def __repr__(self):
        sub_file_content = ""
        for i in range(len(self.blocks)):
            sub_file_content += (str(i+1) + "\n")
            sub_file_content += (str(self.blocks[i]))
            sub_file_content += "\n"
        return sub_file_content[:-1]
