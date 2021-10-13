from .subtitle import Subtitle
from .sub_block import SubBlock
from re import findall, IGNORECASE


def clean(subtitle: Subtitle, regex_list) -> list:
    delete_blocks: list = list()

    _run_regex(subtitle, regex_list)

    delete_blocks += _remove_ads_start(subtitle)
    delete_blocks += _remove_ads_end(subtitle)
    for block in delete_blocks:
        subtitle.remove_block(block)

    return delete_blocks


def _run_regex(subtitle: Subtitle, regex_list):
    blocks = subtitle.blocks
    for block in blocks:
        for regex in regex_list:
            result = findall(regex, block.content.replace("\n", " "), flags=IGNORECASE)
            if result is not None:
                block.regex_matches += len(result)


def _remove_ads_start(subtitle: Subtitle) -> list:
    delete_blocks: list = list()
    blocks = subtitle.blocks
    max_index = len(blocks)
    for block in blocks:
        block: SubBlock
        if block.start_time.seconds < 900:
            max_index = block.orig_index

    best_match_index: int = 0
    highest_score: int = 0
    for block in blocks[:max_index]:
        if block.regex_matches > highest_score:
            best_match_index = block.orig_index
            highest_score = block.regex_matches

    considered_blocks = list(blocks[max(0, best_match_index - 2): min(len(blocks), best_match_index + 2)])
    for block in considered_blocks:
        if block.regex_matches > 0:
            delete_blocks.append(block)
    return delete_blocks


def _remove_ads_end(subtitle: Subtitle) -> list:
    delete_blocks: list = list()
    blocks: list = subtitle.blocks
    min_index: int = max(0, len(blocks) - 10)
    best_match_index: int = 0
    highest_score: int = 0

    for block in blocks[min_index:]:
        if block.regex_matches > highest_score:
            best_match_index = block.orig_index
            highest_score = block.regex_matches

    considered_blocks = list(blocks[max(0, best_match_index - 2): min(len(blocks), best_match_index + 2)])
    for block in considered_blocks:
        if block.regex_matches > 0:
            delete_blocks.append(block)
    return delete_blocks


