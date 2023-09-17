import re
from typing import Dict, List

from libs.subcleaner.sub_block import SubBlock
from libs.subcleaner.subtitle import Subtitle


content_dict: Dict[str, List[SubBlock]] = {}
content_dict_reverse: [SubBlock, str] = {}


def punish_clone_blocks(subtitle: Subtitle) -> None:
    for block in subtitle.blocks:
        content = re.sub("[\\s.,:_-]", "", block.content)
        content_dict_reverse[block] = content
        if content not in content_dict:
            content_dict[content] = []
        content_dict[content].append(block)

    for duplicate_list in content_dict.values():
        if len(duplicate_list) <= 1:
            continue
        for block in duplicate_list:
            if "♪" in block.content:
                continue
            block.regex_matches += 1
            block.hints.append("similar_content")


def move_duplicated(subtitle: Subtitle) -> None:
    for ad_block in subtitle.ad_blocks.copy():
        if "similar_content" not in ad_block.hints:
            continue
        for block in content_dict[content_dict_reverse[ad_block]]:
            subtitle.ad(block)

    for warn_block in subtitle.warning_blocks.copy():
        if "similar_content" not in warn_block.hints:
            continue
        for block in content_dict[content_dict_reverse[warn_block]]:
            subtitle.warn(block)


def reset_duplicate():
    content_dict.clear()
    content_dict_reverse.clear()
