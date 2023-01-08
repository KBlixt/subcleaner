from typing import Optional

from libs.subcleaner import config, args
from libs.subcleaner.subtitle import Subtitle

_report_base = "          | "
_report: str


def generate_report(subtitle: Subtitle) -> str:
    _reset()
    _add(f"{len(subtitle.ad_blocks)} deleted blocks and {len(subtitle.warning_blocks)} warnings remaining.")

    if subtitle.ad_blocks:
        _add("")
        _add(_deleted_card(subtitle), " " * 4)
    if subtitle.warning_blocks and not args.errors_only:
        try:
            sub_file = subtitle.file.relative_to(config.relative_base)
        except ValueError:
            sub_file = subtitle.file
        _add("")
        _add(_warning_card(subtitle), " " * 40)
        _add("")
        _add("To delete all remaining warnings run:")
        _add(f"python3 '{config.script_file}' '{sub_file}' -d {' '.join(subtitle.get_warning_indexes())}")

    return _report[1:]


def _add(lines: str, spacer: str = "") -> None:
    lines = "\n" + lines

    global _report
    _report += lines.replace("\n", f"\n{_report_base}{spacer}")


def _reset() -> None:
    global _report
    _report = ""


def _deleted_card(subtitle: Subtitle) -> str:
    card = "[---------Removed Blocks----------]\n"
    for block in subtitle.ad_blocks:
        card += f"{block.original_index}\n"
        card += f"{block}\n\n"
    card = card[:-1] + "[---------------------------------]"
    return card


def _warning_card(subtitle: Subtitle) -> str:
    card = "[---------Warning Blocks----------]\n"
    for block in subtitle.warning_blocks:
        card += f"{subtitle.index_of(block)}\n"
        card += f"{block}\n\n"
    card = card[:-1] + "[---------------------------------]"
    return card
