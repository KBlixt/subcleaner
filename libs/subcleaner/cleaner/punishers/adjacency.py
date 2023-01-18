from typing import Set

from libs.subcleaner.sub_block import SubBlock
from libs.subcleaner.subtitle import Subtitle


def punish_ad_adjacency(subtitle: Subtitle) -> None:
    blocks_to_punish: Set[SubBlock] = set()
    for index in range(0, len(subtitle.blocks)):
        block = subtitle.blocks[index]
        if index < 3:
            blocks_to_punish.add(block)
            block.hints.append("close_to_start")
            continue
        if index > len(subtitle.blocks) - 4:
            blocks_to_punish.add(block)
            block.hints.append("close_to_end")
            continue
        for compare_block in subtitle.blocks[max(0, index - 15): min(index + 16, len(subtitle.blocks))]:
            if compare_block.regex_matches >= 3 and compare_block != block:
                blocks_to_punish.add(block)
                block.hints.append("nearby_ad")
                break
    for block in blocks_to_punish:
        block.regex_matches += 1
    blocks_to_punish.clear()

    for index in range(0, len(subtitle.blocks)):
        block = subtitle.blocks[index]
        for compare_block in subtitle.blocks[max(0, index - 1): min(index + 2, len(subtitle.blocks))]:
            if compare_block.regex_matches >= 2 and compare_block != block:
                blocks_to_punish.add(block)
                break
    for block in blocks_to_punish:
        block.regex_matches += 1
        block.hints.append("adjacent_ad")
    blocks_to_punish.clear()
