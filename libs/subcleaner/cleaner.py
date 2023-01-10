import re
from typing import List, Dict

from .subtitle import Subtitle
from .sub_block import SubBlock
from re import findall, IGNORECASE, UNICODE
from datetime import timedelta
from . import regex_lists, args


def run_regex(subtitle: Subtitle) -> None:

    for block in subtitle.blocks:
        if len(block.content.strip()) < 1:
            block.regex_matches = 3
            continue

        _run_regex_on_block(block, regex_lists.get_purge_regex(subtitle.language), 3)
        _run_regex_on_block(block, regex_lists.get_warning_regex(subtitle.language), 1)

        if block.regex_matches == 0:
            block.regex_matches = -1

    for index in range(0, len(subtitle.blocks)):
        if index < 3 or index > len(subtitle.blocks) - 4:
            subtitle.blocks[index].regex_matches += 1
            continue
        for block in subtitle.blocks[max(0, index - 1): min(index + 2, len(subtitle.blocks))]:
            if block.regex_matches >= 2 and block != subtitle.blocks[index]:
                subtitle.blocks[index].regex_matches += 1
                break

    if len(subtitle.blocks) >= 50:
        for index in range(0, len(subtitle.blocks)):
            for block in subtitle.blocks[max(0, index - 15): min(index + 16, len(subtitle.blocks))]:
                if block.regex_matches >= 3:
                    subtitle.blocks[index].regex_matches += 1
                    break

    if subtitle.blocks[0].start_time < timedelta(seconds=1):
        subtitle.blocks[0].regex_matches += 1

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


def _run_regex_on_block(block: SubBlock, regex_list: List[str], punishment: int) -> None:
    clean_content = " ".join(block.content.replace("-\n", "-").split())
    for regex in regex_list:
        result = findall(regex, clean_content, flags=IGNORECASE | UNICODE)
        if result:
            block.regex_matches += punishment * len(result)


def find_ads(subtitle: Subtitle) -> None:
    for index in range(0, len(subtitle.blocks)):
        block: SubBlock = subtitle.blocks[index]

        if block.regex_matches >= 3:
            subtitle.ad_blocks.append(block)
            continue
        elif block.regex_matches == 2:
            subtitle.warning_blocks.append(block)

        pre_block: SubBlock = subtitle.blocks[max(index - 1, 0)]
        post_block: SubBlock = subtitle.blocks[min(index + 1, len(subtitle.blocks) - 1)]

        if index == 0:
            if post_block.regex_matches >= 3:
                if (post_block.start_time - block.end_time) < timedelta(seconds=1):
                    if block in subtitle.warning_blocks:
                        subtitle.ad_blocks.append(block)
                        subtitle.warning_blocks.remove(block)
                    else:
                        subtitle.warning_blocks.append(block)
                else:
                    subtitle.warning_blocks.append(block)
            continue

        if index == len(subtitle.blocks) - 1:
            if pre_block.regex_matches >= 3:
                if (block.start_time - pre_block.end_time) < timedelta(seconds=1):
                    if block in subtitle.warning_blocks:
                        subtitle.ad_blocks.append(block)
                        subtitle.warning_blocks.remove(block)
                    else:
                        subtitle.warning_blocks.append(block)
                else:
                    subtitle.warning_blocks.append(block)
            continue

        if pre_block.regex_matches >= 3 and post_block.regex_matches >= 3:
            if (post_block.start_time - block.end_time) < timedelta(seconds=1) and \
                    (block.start_time - pre_block.end_time) < timedelta(seconds=1):
                subtitle.ad_blocks.append(block)
                continue
            if block.regex_matches == 2:
                subtitle.ad_blocks.append(block)
                continue
            else:
                subtitle.warning_blocks.append(block)
                continue

    for ad_block in subtitle.ad_blocks:
        for block in subtitle.blocks:
            if block == ad_block:
                continue
            if block in subtitle.ad_blocks:
                continue
            if not block.equal_content(ad_block):
                continue
            if block in subtitle.warning_blocks:
                subtitle.warning_blocks.remove(block)
            subtitle.ad_blocks.append(block)

    for warning_block in subtitle.warning_blocks:
        for block in subtitle.blocks:
            if block == warning_block:
                continue
            if block in subtitle.warning_blocks:
                continue
            if not block.equal_content(warning_block):
                continue
            subtitle.warning_blocks.append(block)

    cascade_memory: List[SubBlock] = []
    for i in range(0, len(subtitle.blocks)):
        block = subtitle.blocks[i]

        cascade: bool = False
        if i < len(subtitle.blocks)-1:
            post_block = subtitle.blocks[i + 1]
            if compare(post_block.content, block.content):
                cascade = True
        if i > 0:
            pre_block = subtitle.blocks[i - 1]
            if compare(pre_block.content, block.content):
                cascade = True

        if not cascade:
            cascade_memory.clear()
            continue

        if block not in subtitle.ad_blocks:
            cascade_memory.append(block)
            continue

        for casc_block in cascade_memory:
            if casc_block in subtitle.warning_blocks:
                subtitle.warning_blocks.remove(casc_block)
            subtitle.ad_blocks.append(casc_block)
        cascade_memory.clear()

    subtitle.dedupe_warning_blocks()


def compare(s1: str, s2: str) -> bool:
    if len(s1) + 1 == len(s2):
        if s2.startswith(s1) or s2.endswith(s1):
            return True
    elif len(s1) == 1 + len(s2):
        if s1.startswith(s2) or s1.endswith(s2):
            return True
    return False


def remove_ads(subtitle: Subtitle):
    if args.sensitive and len(subtitle.blocks) > 1:
        if subtitle.blocks[0] not in subtitle.warning_blocks and subtitle.blocks[0] not in subtitle.ad_blocks:
            subtitle.warning_blocks.append(subtitle.blocks[0])
        if subtitle.blocks[-1] not in subtitle.warning_blocks and subtitle.blocks[-1] not in subtitle.ad_blocks:
            subtitle.warning_blocks.append(subtitle.blocks[-1])
        for i in range(1, len(subtitle.blocks)-1):
            prev_block = subtitle.blocks[i - 1]
            block = subtitle.blocks[i]
            next_block = subtitle.blocks[i + 1]
            if prev_block in subtitle.ad_blocks or next_block in subtitle.ad_blocks:
                if block not in subtitle.warning_blocks and block not in subtitle.ad_blocks:
                    subtitle.warning_blocks.append(block)
    for block in subtitle.ad_blocks:
        subtitle.blocks.remove(block)

    subtitle.ad_blocks.sort(key=lambda b: b.original_index)
    subtitle.warning_blocks.sort(key=lambda b: b.original_index)


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
