from datetime import timedelta

from libs.subcleaner.subtitle import Subtitle
from libs.subcleaner.sub_block import SubBlock
from libs.subcleaner.settings import args

from . import detectors, punishers


def find_ads(subtitle: Subtitle) -> None:

    punishers.punish_quick_first_block(subtitle)
    punishers.punish_short_duration(subtitle)
    punishers.punish_regex_matches(subtitle)

    for block in subtitle.blocks:
        if block.regex_matches == 0:
            block.regex_matches = -1

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


def remove_ads(subtitle: Subtitle):
    if args.sensitive and len(subtitle.blocks) > 1:
        subtitle.warn(subtitle.blocks[0])
        subtitle.warn(subtitle.blocks[-1])

        for i in range(1, len(subtitle.blocks)-1):
            prev_block = subtitle.blocks[i - 1]
            block = subtitle.blocks[i]
            next_block = subtitle.blocks[i + 1]
            if prev_block in subtitle.ad_blocks or next_block in subtitle.ad_blocks:
                subtitle.warn(block)
    for block in subtitle.ad_blocks:
        subtitle.blocks.remove(block)
    subtitle.reindex()


def fix_overlap(subtitle: Subtitle) -> None:
    if len(subtitle.blocks) < 2:
        return

    margin: timedelta = timedelta(seconds=0.0417)
    previous_block: SubBlock = subtitle.blocks[0]
    for block in subtitle.blocks[1:]:
        block: SubBlock
        stop_time: timedelta = previous_block.end_time + margin
        start_time: timedelta = block.start_time - margin
        overlap: timedelta = stop_time - start_time
        if overlap.days >= 0 and overlap.microseconds > 3000:
            content_ratio = len(block.content) / (len(block.content) + len(previous_block.content))
            block.start_time += content_ratio * overlap
            previous_block.end_time += (content_ratio - 1) * overlap
        previous_block = block
    return
