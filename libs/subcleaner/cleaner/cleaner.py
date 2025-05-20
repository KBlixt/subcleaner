import logging
from datetime import timedelta
from pathlib import Path
from typing import *
from libs.subcleaner.subtitle import Subtitle
from libs.subcleaner.settings import args

from . import detectors, punishers
from ..sub_block import SubBlock

ad_blocks: Dict[SubBlock, Set[Path]] = {}
warning_blocks: Dict[SubBlock, Set[Path]] = {}

logger = logging.getLogger(__name__)


def find_ads(subtitle: Subtitle) -> None:
    punishers.punish_regex_matches(subtitle)

    for block in subtitle.blocks:
        if block.regex_matches == 0:
            block.regex_matches = -1

    punishers.punish_quick_first_block(subtitle)
    punishers.punish_ad_adjacency(subtitle)
    punishers.punish_clone_blocks(subtitle)

    for block in subtitle.blocks:
        if block.regex_matches >= 3:
            subtitle.ad(block)
        elif block.regex_matches == 2:
            subtitle.warn(block)

    detectors.detect_wedged(subtitle)
    punishers.move_duplicated(subtitle)
    detectors.detect_chain(subtitle)


def reset():
    punishers.reset_duplicate()


def remove_ads(subtitle: Subtitle):
    if args.sensitive and len(subtitle.blocks) > 1:
        subtitle.warn(subtitle.blocks[0])
        subtitle.warn(subtitle.blocks[-1])

        for i in range(1, len(subtitle.blocks) - 1):
            prev_block = subtitle.blocks[i - 1]
            block = subtitle.blocks[i]
            next_block = subtitle.blocks[i + 1]
            if prev_block in subtitle.ad_blocks or next_block in subtitle.ad_blocks:
                subtitle.warn(block)

    for block in subtitle.ad_blocks:
        try:
            subtitle.blocks.remove(block)
            if "-->" in block.content:
                logger.warning(f"potential malformed subtitle blocks in removed block {block.original_index}.")
        except ValueError:
            pass
        for e_block in ad_blocks:
            if e_block.clean_content == block.clean_content:
                ad_blocks[e_block].add(subtitle.short_path)
                break
        else:
            ad_blocks[block] = {subtitle.short_path}

    for block in subtitle.warning_blocks:
        for e_block in warning_blocks:
            if e_block.clean_content == block.clean_content:
                warning_blocks[e_block].add(subtitle.short_path)
                break
        else:
            warning_blocks[block] = {subtitle.short_path}

    subtitle.reindex()


def fix_overlap(subtitle: Subtitle):
    if len(subtitle.blocks) < 2:
        return False
    changes = False
    previous_block = subtitle.blocks[0]
    for block in subtitle.blocks[1:]:
        if not (previous_block.start_time < block.start_time and previous_block.end_time < block.end_time):
            previous_block = block
            continue

        overlap = previous_block.end_time - block.start_time + timedelta(seconds=3 / 30)
        if timedelta(milliseconds=3) < overlap and (len(block.content) + len(previous_block.content)) > 0:
            content_ratio = block.duration_seconds / (block.duration_seconds + previous_block.duration_seconds)
            block.start_time += content_ratio * overlap
            previous_block.end_time += (content_ratio - 1) * overlap
            changes = True
        
        previous_block = block
    return changes


def unscramble(subtitle: Subtitle):
    subtitle.blocks.sort(key=lambda x: x.start_time)
    for block in subtitle.blocks.copy():
        if block.duration_seconds <= 0:
            subtitle.ad(block)
            block.hints.append("negative_duration")
            subtitle.blocks.remove(block)
    subtitle.reindex()
