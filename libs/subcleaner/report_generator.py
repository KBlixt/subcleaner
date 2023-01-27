from pathlib import Path
from typing import *

from libs.subcleaner.cleaner import cleaner
from libs.subcleaner.settings import args, config
from libs.subcleaner.sub_block import SubBlock
from libs.subcleaner.subtitle import Subtitle

_report_base = "          | "
_report: str


def generate_report(subtitle: Subtitle) -> str:
    _reset()
    _add(f"{len(subtitle.ad_blocks)} deleted blocks and {len(subtitle.warning_blocks)} warnings remaining.")

    if subtitle.ad_blocks:
        _add("")
        _add(_deleted_card(subtitle.ad_blocks), " " * 4)
    if subtitle.warning_blocks and not args.errors_only:
        _add("")
        _add(_warning_card(subtitle.warning_blocks), " " * 40)
        _add("")
        _add("To delete all remaining warnings run:")
        _add(f"python3 '{config.script_file}' '{subtitle.short_path}' -d {' '.join(subtitle.get_warning_indexes())}")

    return _report[1:]

def generate_end_report() -> str:
    _reset()
    _add("")
    _add(_end_deleted_card(cleaner.ad_blocks), " " * 4)
    _add("")
    _add(_end_warning_card(cleaner.warning_blocks), " " * 40)
    _add("")
    return _report[1:]



def _add(lines: str, spacer: str = "") -> None:
    lines = "\n" + lines

    global _report
    _report += lines.replace("\n", f"\n{_report_base}{spacer}")


def _reset() -> None:
    global _report
    _report = ""


def _deleted_card(ad_blocks: Set[SubBlock]) -> str:
    ad_blocks_list = list(ad_blocks)
    ad_blocks_list.sort(key=lambda b: b.original_index)
    card = "[---------Removed Blocks----------]\n"
    for block in ad_blocks_list:
        card += f"{block.original_index}\n"
        card += f"{block}\n"
        if args.explain:
            card += f"reasons: ({', '.join(block.hints)})\n"
        card += "\n"
    card = card[:-1] + "[---------------------------------]"
    return card


def _warning_card(warning_blocks: Set[SubBlock]) -> str:
    warning_blocks_list = list(warning_blocks)
    warning_blocks_list.sort(key=lambda b: b.original_index)
    card = "[---------Warning Blocks----------]\n"
    for block in warning_blocks_list:
        card += f"{block.current_index}\n"
        card += f"{block}\n"
        if args.explain:
            card += f"reasons: ({', '.join(block.hints)})\n"
        card += "\n"
    card = card[:-1] + "[---------------------------------]"
    return card


def _end_deleted_card(ad_blocks: Dict[SubBlock, Set[Path]]) -> str:

    ad_blocks_list = list((key, value) for key, value in ad_blocks.items())
    ad_blocks_list.sort(key=lambda b: len(b[1]))
    card = "[---------All Removed Blocks----------]\n"
    for block in ad_blocks_list:
        if len(block[1]) > 4:
            continue
        if 0 == block[0].regex_matches or block[0].regex_matches > 9:
            continue

        card += f"{block[0].original_index}\n"
        card += f"{block[0]}\n"
        if args.explain:
            card += f"reasons: ({', '.join(block[0].hints)})\n"
        card += "subtitles: \n" + "\n".join(map(str, block[1])) + "\n"
        card += "\n"
    card = card[:-1] + "[---------------------------------]"
    return card


def _end_warning_card(warning_blocks: Dict[SubBlock, Set[Path]]) -> str:
    ad_blocks_list = list((key, value) for key, value in warning_blocks.items())
    ad_blocks_list.sort(key=lambda b: len(b[1]), reverse=True)
    card = "[---------All Warning Blocks----------]\n"
    for block in ad_blocks_list:
        if len(block[1]) < 2:
            continue
        card += f"{block[0].original_index}\n"
        card += f"{block[0]}\n"
        if args.explain:
            card += f"reasons: ({', '.join(block[0].hints)})\n"
        card += "subtitles: \n" + "\n".join(map(str, block[1])) + "\n"
        card += "\n"
    card = card[:-1] + "[---------------------------------]"
    return card
