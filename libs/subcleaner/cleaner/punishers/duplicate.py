import re
from typing import Dict, List

from libs.subcleaner.sub_block import SubBlock
from libs.subcleaner.subtitle import Subtitle


def punish_clone_blocks(subtitle: Subtitle) -> None:
    content_dict: Dict[str, List[SubBlock]] = {}

    for block in subtitle.blocks:
        content = re.sub("[\\s.,:_-]", "", block.content)
        if content not in content_dict:
            content_dict[content] = []
        content_dict[content].append(block)

    for duplicate_list in content_dict.values():
        if len(duplicate_list) <= 1:
            continue
        for block in duplicate_list:
            block.regex_matches += 1
            block.hints.append("similar_content")


def move_duplicated(subtitle: Subtitle) -> None:
    for ad_block in list(subtitle.ad_blocks):
        for block in subtitle.blocks:
            if block == ad_block:
                continue
            if block.equal_content(ad_block):
                subtitle.ad(block)

    for warning_block in list(subtitle.warning_blocks):
        for block in subtitle.blocks:
            if block == warning_block:
                continue
            if block.equal_content(warning_block):
                subtitle.warn(block)
