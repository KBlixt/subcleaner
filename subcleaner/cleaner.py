from .subtitle import Subtitle
from .sub_block import SubBlock
from re import findall, IGNORECASE
from datetime import timedelta


def clean(subtitle: Subtitle, regex_list) -> list:
    delete_blocks: list = list()

    _run_regex(subtitle, regex_list)

    delete_blocks += _remove_ads_start(subtitle)
    delete_blocks += _remove_ads_end(subtitle)

    clean_delete_blocks: list = list()
    for block in delete_blocks:
        if block not in clean_delete_blocks:
            clean_delete_blocks.append(block)

    for block in clean_delete_blocks:
        subtitle.remove_block(block)

    _fix_overlap(subtitle)

    return clean_delete_blocks


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

    if best_match_index == 0:
        return []

    considered_blocks = list(blocks[max(0, best_match_index - 6): min(len(blocks), best_match_index + 6)])
    for block in considered_blocks:
        if block.regex_matches > 0:
            delete_blocks.append(block)
    return delete_blocks


def _remove_ads_end(subtitle: Subtitle) -> list:
    delete_blocks: list = list()
    blocks: list = subtitle.blocks
    min_index: int = max(0, len(blocks) - 30)
    best_match_index: int = 0
    highest_score: int = 0

    for block in blocks[min_index:]:
        if block.regex_matches > highest_score:
            best_match_index = block.orig_index
            highest_score = block.regex_matches

    if best_match_index == 0:
        return []

    considered_blocks = list(blocks[max(0, best_match_index - 6): min(len(blocks), best_match_index + 6)])
    for block in considered_blocks:
        if block.regex_matches > 0:
            delete_blocks.append(block)
    return delete_blocks


def _fix_overlap(subtitle: Subtitle) -> None:
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
