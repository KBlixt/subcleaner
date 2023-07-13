import datetime
import logging
import re
from typing import List

logger = logging.getLogger(__name__)


class SubBlock:
    original_index: int
    current_index: int
    content: str
    clean_content: str
    start_time: datetime.timedelta
    end_time: datetime.timedelta
    regex_matches = 0
    hints: List[str]

    def __init__(self, block_content: str, original_index_actual: int):
        lines = block_content.strip().split("\n")

        if self.is_sub_block_header(lines[0]) and len(lines) > 1 and not self.is_sub_block_header(lines[1]):
            lines = [""] + lines

        if lines[0].isnumeric():
            self.original_index = int(lines[0])
        else:
            number = ""
            for character in lines[0]:
                if character.isnumeric():
                    number += character
                else:
                    break
            if number:
                self.original_index = int(number)
            else:
                self.original_index = original_index_actual

        if len(lines) < 2 or not self.is_sub_block_header(lines[1]):
            raise ParsingException(self.original_index, "incorrectly formatted subtitle block")

        times = lines[1].replace(" ", "").split("-->")
        try:
            self.start_time = time_string_to_timedelta(times[0])
            self.end_time = time_string_to_timedelta(times[1])
        except ValueError:
            raise ParsingException(self.original_index, "failed to parse timeframe.")
        except IndexError:
            raise ParsingException(self.original_index, "failed to parse timeframe.")

        if len(lines) > 2:
            self.content = "\n".join(lines[2:]).strip()
        else:
            self.content = ""
        self.content = self.content.replace("</br>", "\n")
        self.clean_content = re.sub("[\\s.,:_-]", "", self.content)
        self.hints = []

    def equal_content(self, block: "SubBlock") -> bool:
        t = re.sub("[\\s.,:_-]", "", self.content)
        o = re.sub("[\\s.,:_-]", "", block.content)
        return t == o

    def __str__(self) -> str:
        string = f"{timedelta_to_time_string(self.start_time)} --> {timedelta_to_time_string(self.end_time)}\n" \
                 f"{self.content}"
        return string

    @classmethod
    def is_sub_block_header(cls, line: str) -> bool:
        if "\n" in line:
            return False

        times = line.replace(" ", "").split("-->")
        if len(times) < 2:
            return False
        try:
            time_string_to_timedelta(times[0])
            time_string_to_timedelta(times[1])
        except ValueError:
            return False
        except IndexError:
            return False

        return True

    @property
    def duration_seconds(self) -> float:
        return (self.end_time - self.start_time).total_seconds()


class ParsingException(Exception):
    block_index: int
    subtitle_file: str
    file_line: int
    reason: str

    def __init__(self, block_index, reason):
        self.block_index = block_index
        self.reason = reason

    def __str__(self) -> str:
        return f"Parsing error at block {self.block_index} in file \"{self.subtitle_file}\" line {self.file_line}. reason: {self.reason}"


def time_string_to_timedelta(time_string: str) -> datetime.timedelta:
    time = time_string.replace(",", ".").replace(" ", "")
    split = time.split(":")

    hours = float(split[0])
    minutes = float(split[1])
    seconds = split[2][:6]

    seconds_clean = ""
    found_dot = False
    for ch in seconds:
        if ch.isnumeric():
            seconds_clean += ch
        if ch == ".":
            if not found_dot:
                found_dot = True
                seconds_clean += ch
    seconds = float(seconds_clean)
    if seconds >= 60:
        raise ValueError()
    if minutes >= 60:
        raise ValueError()

    return datetime.timedelta(hours=hours,
                              minutes=minutes,
                              seconds=seconds)


def timedelta_to_time_string(timedelta: datetime.timedelta) -> str:
    time_string = str(timedelta)
    if "." in time_string:
        time_string = time_string[: -3].replace(".", ",").zfill(12)
    else:
        time_string = f"{time_string},000".zfill(12)
    return time_string
