import datetime
from datetime import timedelta

from libs.subcleaner.subtitle import Subtitle


def punish_quick_first_block(subtitle: Subtitle) -> None:
    if not subtitle.blocks:
        return 
    block = subtitle.blocks[0]
    if block.start_time < timedelta(seconds=1):
        block.regex_matches += 1
        block.hints.append("quick_start")


def punish_short_duration(subtitle: Subtitle) -> None:
    for block in subtitle.blocks:
        if block.end_time - block.start_time < datetime.timedelta(milliseconds=8/30*1000):
            block.regex_matches += 1
            block.hints.append("short duration")

        if block.end_time - block.start_time < datetime.timedelta(milliseconds=3/30*1000):
            block.regex_matches += 1
            block.hints.append("very short duration")
