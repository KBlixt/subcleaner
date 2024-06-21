from datetime import timedelta
from typing import List

from libs.subcleaner.sub_block import SubBlock
from libs.subcleaner.subtitle import Subtitle


def detect_chain(subtitle: Subtitle) -> None:
    chain: List[SubBlock] = []
    identical_count = 0
    for i in range(1, len(subtitle.blocks)):
        block = subtitle.blocks[i]
        pre_block = subtitle.blocks[i - 1]

        link: bool = False

        if is_link(pre_block, block):
            if pre_block.equal_content(block):
                identical_count += 1
            link = True

        if link:
            if not chain:
                chain.append(pre_block)
            chain.append(block)
            continue

        if len(chain) > 2 + identical_count or any(block in subtitle.ad_blocks for block in chain):
            for chain_block in chain:
                subtitle.ad(chain_block)
                chain_block.hints.append("chain_block")

        chain.clear()
        identical_count = 0
    if len(chain) > 2 + identical_count or any(block in subtitle.ad_blocks for block in chain):
        for chain_block in chain:
            subtitle.ad(chain_block)
            chain_block.hints.append("chain_block")


def is_link(block: SubBlock, post_block: SubBlock) -> bool:
    if block.start_time > post_block.start_time:
        block, post_block = post_block, block
    if post_block.start_time - block.end_time > timedelta(milliseconds=500):
        return False

    if len(block.content) < len(post_block.content) <= len(block.content) + 2:
        if post_block.content.startswith(block.content) or post_block.content.endswith(block.content):
            return True
    elif len(post_block.content) < len(block.content) <= len(post_block.content) + 2:
        if block.content.startswith(post_block.content) or block.content.endswith(post_block.content):
            return True
    elif block.content.strip() == post_block.content.strip():
        return True

    return False
