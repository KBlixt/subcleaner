import datetime
from datetime import timedelta

from libs.subcleaner.subtitle import Subtitle


def punish_quick_first_block(subtitle: Subtitle) -> None:
    if subtitle.blocks[0].start_time < timedelta(seconds=1):
        subtitle.blocks[0].regex_matches += 1


def punish_short_duration(subtitle: Subtitle) -> None:
    for block in subtitle.blocks:
        if block.end_time - block.start_time < datetime.timedelta(milliseconds=250):
            block.regex_matches += 1

        if block.end_time - block.start_time < datetime.timedelta(milliseconds=100):
            block.regex_matches += 1