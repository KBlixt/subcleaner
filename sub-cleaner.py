#!/usr/bin/python3

from pathlib import Path
import argparse
import os
from sys import argv, exit
from configparser import ConfigParser
from re import findall, IGNORECASE
from datetime import timedelta
from math import floor
import langdetect
try:
    import six
except ImportError:
    print("package \"six\" must be installed.")
    exit()


def main():
    config_file: Path = Path(argv[0]).parent.joinpath("regex.config")
    subtitle_file: Path = Path(argv[1])
    subtitle_lang: str = argv[2].split(":")[0]

    log_file = Path(subtitle_file.parent, "log")
    log = log_file.open(mode="w")
    log.write(str(argv) + "\n")
    log.write("subtitle_file: " + str(subtitle_file) + "\n")

    if subtitle_file.name[-3:] != "srt":
        print("subtitle must be an srt file.")
        log.close()
        exit()
    regex_list = get_regex_list(config_file)

    log.write("regex loaded\n")

    log.write("regex loaded\n")
    blocks = parse_sub(subtitle_file)
    log.write("blocks loaded\n")
    check_regex(blocks, regex_list)
    log.write("checked regex\n")
    detect_adds_start(blocks)
    log.write("detected adds\n")
    detect_adds_end(blocks)
    log.write("detected adds\n")

    publish_sub(subtitle_file, blocks)
    log.write("wrote data\n")

    report(blocks, subtitle_file, subtitle_lang)
    log.write("wrote report\n")
    log.close()


def get_regex_list(config_file: Path) -> list:
    cfg = ConfigParser()
    cfg.read(str(config_file))
    regex_list = list(cfg.items("REGEX"))
    new_list = list()
    for regex in regex_list:
        if len(regex[1]) != 0:
            new_list.append(regex[1])
    return new_list


def parse_sub(subtitle_file: Path) -> list:
    with subtitle_file.open(mode="r") as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]

    current_index = 1
    block = SubBlock(1)
    blocks = []
    for line in lines:
        line = line.replace("\n", "")
        if len(line) == 0:
            if len(block.content) > 0:
                blocks.append(block)
                current_index += 1
            block = SubBlock(current_index)
            continue

        if "-->" in line and block.stop_time.seconds == 0:
            start = line.split("-->")[0].strip()
            stop = line.split("-->")[1].strip().replace("\n", "")
            block.start_time = convert_to_timedelta(start)
            block.stop_time = convert_to_timedelta(stop)
            continue

        if line.isnumeric() and block.stop_time.seconds == 0:
            continue

        block.content = block.content + line + "\n"

    return blocks


def convert_to_timedelta(time_string: str) -> timedelta:
    time_string = time_string.replace(".", ",")
    split = time_string.split(":")

    return timedelta(hours=float(split[0]),
                     minutes=float(split[1]),
                     seconds=float(split[2].split(",")[0]),
                     milliseconds=float(split[2].split(",")[1]))


def convert_from_timedelta(td: timedelta) -> str:
    hours = floor(td.seconds / 60 / 60)
    minutes = floor(td.seconds / 60)
    seconds = floor(td.seconds)
    mill = floor(td.microseconds / 1000)

    hours_str = str(hours)
    minutes_str = str(minutes % (60 * 60))
    seconds_str = str(seconds % 60)
    mill_str = str(mill % 1000)

    hours_str = "0" * (2 - len(hours_str)) + hours_str
    minutes_str = "0" * (2 - len(minutes_str)) + minutes_str
    seconds_str = "0" * (2 - len(seconds_str)) + seconds_str
    mill_str = mill_str + "0" * (3 - len(mill_str))

    return hours_str + ":" + minutes_str + ":" + seconds_str + "," + mill_str


def publish_sub(subtitle_file, blocks):
    file = subtitle_file.open(mode="w")
    i = 1
    for block in blocks:
        block: SubBlock
        if not block.keep:
            continue

        file.write(str(i) + "\n")
        file.write(convert_from_timedelta(block.start_time) +
                   " --> " +
                   convert_from_timedelta(block.stop_time) +
                   "\n")
        file.write(block.content + "\n")
        i += 1


def check_lang(blocks, subtitle_lang) -> bool:
    content = ""
    for block in blocks:
        if block.keep:
            content = content + block.content
    return langdetect.detect(content) == subtitle_lang


def check_regex(blocks, regex_list):
    for block in blocks:
        matches = 0
        for regex in regex_list:
            result = findall(regex, block.content.replace("\n", " "), flags=IGNORECASE)
            if result is not None:
                matches += len(result)
        block.regex_matches = matches


def detect_adds_start(blocks):
    max_index = len(blocks)
    for block in blocks:
        block: SubBlock
        if block.start_time.seconds < 900:
            max_index = block.index

    best_match_index = None
    highest_score = 0
    for block in blocks[:max_index]:
        if block.regex_matches > highest_score:
            best_match_index = block.index
            highest_score = block.regex_matches

    if best_match_index is None:
        return

    for block in blocks[max(0, best_match_index - 2): min(len(blocks), best_match_index + 2)]:
        if block.regex_matches > 0:
            block.keep = False


def detect_adds_end(blocks):
    min_index = max(0, len(blocks) - 10)

    best_match_index = None
    highest_score = 0
    for block in blocks[min_index:]:
        if block.regex_matches > highest_score:
            best_match_index = block.index
            highest_score = block.regex_matches

    if best_match_index is None:
        return

    for block in blocks[max(0, best_match_index - 2): min(len(blocks), best_match_index + 2)]:
        if block.regex_matches > 0:
            block.keep = False


def report(blocks: list, subtitle_file: Path, subtitle_lang):
    write_report = False

    report_path = Path(subtitle_file.parent, "sub-cleaner." + subtitle_lang + ".report")
    warn_path = Path(subtitle_file.parent, "lang-warning." + subtitle_lang + ".report")

    if not check_lang(blocks, subtitle_lang):
        with warn_path.open(mode='w') as file:
            file.write(str(subtitle_file) + " is not the correct language, Please verify.")
    else:
        try:
            warn_path.unlink()
        except FileNotFoundError:
            pass

    delete_report: str = "[--Removed Blocks--]\n\n"
    for block in blocks:
        block: SubBlock
        if not block.keep:
            write_report = True
            delete_report += str(block.index) + "\n"
            delete_report += convert_from_timedelta(block.start_time) + " --> " + convert_from_timedelta(
                block.stop_time) + "\n"
            delete_report += block.content + "\n"

    if not write_report:
        return

    delete_report += "[--/Removed Blocks--]"

    with report_path.open(mode='w') as file:
        file.write(delete_report)
    return


class SubBlock:
    index: int
    content: str
    start_time: timedelta
    stop_time: timedelta
    regex_matches: int
    keep: bool

    def __init__(self, index):
        self.index = index
        self.keep = True
        self.regex_matches = 0
        self.content = ""
        self.stop_time = timedelta()
        self.start_time = timedelta()


if __name__ == '__main__':
    main()
