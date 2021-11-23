from .subtitle import Subtitle
from .sub_block import SubBlock
from re import findall, IGNORECASE, UNICODE
from datetime import timedelta


class Cleaner(object):

    purge_regex_list: list
    warning_regex_list: list

    def __init__(self):
        self.purge_regex_list = []
        self.warning_regex_list = []

    def run_regex(self, subtitle: Subtitle):
        blocks = subtitle.blocks
        for block in blocks:
            if len(block.content.strip(" -_.")) == 0:
                block.regex_matches = 3
                break

            for regex in self.purge_regex_list:
                result = findall(regex, block.content.replace("\n", " ").strip(), flags=IGNORECASE | UNICODE)
                if result is not None and len(result) > 0:
                    block.regex_matches = 3
                    break

            for regex in self.warning_regex_list:
                result = findall(regex, block.content.replace("\n", " ").strip(), flags=IGNORECASE | UNICODE)
                if result is not None and len(result) > 0:
                    block.regex_matches += len(result)
            if block.regex_matches == 0:
                block.regex_matches = -1

        if len(blocks) >= 10:
            for index in range(0, len(subtitle.blocks)):
                if index < 3 or index > len(subtitle.blocks)-4:
                    subtitle.blocks[index].regex_matches += 1
                    continue
                for block in subtitle.blocks[max(0, index-1): min(index+2, len(subtitle.blocks))]:
                    if block.regex_matches >= 2 and index != block.index - 1:
                        subtitle.blocks[index].regex_matches += 1
                        break

        if len(blocks) >= 100:
            for index in range(0, len(subtitle.blocks)):
                if index < 15 or index > len(subtitle.blocks)-16:
                    subtitle.blocks[index].regex_matches += 1
                    continue
                for block in subtitle.blocks[max(0, index-15): min(index+16, len(subtitle.blocks))]:
                    if block.regex_matches >= 3:
                        subtitle.blocks[index].regex_matches += 1
                        break

    @staticmethod
    def remove_ads(subtitle: Subtitle):
        for block in subtitle.ad_blocks:
            subtitle.remove_block(block)
        for index in range(len(subtitle.blocks)):
            block: SubBlock = subtitle.blocks[index]
            block.index = index+1

    @staticmethod
    def find_ads(subtitle: Subtitle):

        for index in range(0, len(subtitle.blocks)):
            block: SubBlock = subtitle.blocks[index]

            if block.regex_matches >= 3:
                subtitle.ad_blocks.append(block)
                continue
            elif block.regex_matches == 2:
                subtitle.warning_blocks.append(block)
                continue

            if index == 0 or index == len(subtitle.blocks)-1:
                continue

            pre_block: SubBlock = subtitle.blocks[index - 1]
            post_block: SubBlock = subtitle.blocks[index + 1]
            if pre_block.regex_matches >= 3 and post_block.regex_matches >= 3:
                if block.start_time - pre_block.stop_time < timedelta(seconds=2.5):
                    subtitle.ad_blocks.append(block)
                    continue
                else:
                    subtitle.warning_blocks.append(block)
                    continue

    @staticmethod
    def fix_overlap(subtitle: Subtitle) -> None:
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
