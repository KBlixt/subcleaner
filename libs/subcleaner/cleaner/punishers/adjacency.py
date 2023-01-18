from typing import Set

from libs.subcleaner.sub_block import SubBlock
from libs.subcleaner.subtitle import Subtitle


def punish_ad_adjacency(subtitle: Subtitle) -> None:
    nearby_blocks: Set[SubBlock] = set()
    for index in range(0, len(subtitle.blocks)):
        block = subtitle.blocks[index]
        if index < 3:
            nearby_blocks.add(block)
            block.hints.append("close_to_start")
            continue
        if index > len(subtitle.blocks) - 4:
            nearby_blocks.add(block)
            block.hints.append("close_to_end")
            continue
        for compare_block in subtitle.blocks[max(0, index - 15): min(index + 16, len(subtitle.blocks))]:
            if compare_block.regex_matches >= 3 and compare_block != block:
                nearby_blocks.add(block)
                block.hints.append("nearby_ad")
                break

    adjacent_blocks: Set[SubBlock] = set()
    for index in range(0, len(subtitle.blocks)):
        block = subtitle.blocks[index]
        for compare_block in subtitle.blocks[max(0, index - 1): min(index + 2, len(subtitle.blocks))]:
            if compare_block.regex_matches >= 2 and compare_block != block:
                adjacent_blocks.add(block)
                break

    for block in nearby_blocks:
        block.regex_matches += 1

    for block in adjacent_blocks:
        block.regex_matches += 1
        block.hints.append("adjacent_ad")
