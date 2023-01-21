import datetime
import logging
import re
from typing import List

logger = logging.getLogger(__name__)


class SubBlock:
    original_index: int
    current_index: int
    content: str
    start_time: datetime.timedelta
    end_time: datetime.timedelta
    regex_matches = 0
    hints: List[str]

    def __init__(self, block_content: str):
        rows = block_content.strip().split("\n")

        try:
            self.original_index = int(rows[0])
        except ValueError:
            raise ParsingException(rows[0])
        if len(rows) == 1:
            raise ParsingException(self.original_index)

        try:
            times = rows[1].replace(" ", "").split("-->")
            self.start_time = time_string_to_timedelta(times[0])
            self.end_time = time_string_to_timedelta(times[1])
        except ValueError:
            raise ParsingException(self.original_index)
        except IndexError:
            raise ParsingException(self.original_index)

        if len(rows) > 2:
            self.content = "\n".join(rows[2:]).strip()
        else:
            self.content = ""
        self.content = self.content.replace("</br>", "\n")
        self.current_index = self.original_index
        self.hints = []

    def equal_content(self, block: "SubBlock") -> bool:
        t = re.sub("[\\s.,:_-]", "", self.content)
        o = re.sub("[\\s.,:_-]", "", block.content)
        return t == o

    def __str__(self) -> str:
        string = f"{timedelta_to_time_string(self.start_time)} --> {timedelta_to_time_string(self.end_time)}\n" \
                 f"{self.content.replace('--', '—')}"
        return string


class ParsingException(Exception):
    block_index: int
    subtitle_file: str

    def __init__(self, block_index):
        self.block_index = block_index

    def __str__(self) -> str:
        return f"Parsing error at block {self.block_index} in file {self.subtitle_file}."


def time_string_to_timedelta(time_string: str) -> datetime.timedelta:
    time = time_string.replace(",", ".").replace(" ", "")
    split = time.split(":")

    return datetime.timedelta(hours=float(split[0]),
                              minutes=float(split[1]),
                              seconds=float(split[2]))


def timedelta_to_time_string(timedelta: datetime.timedelta) -> str:
    time_string = str(timedelta)
    if "." in time_string:
        time_string = time_string[: -3].replace(".", ",").zfill(12)
    else:
        time_string = f"{time_string},000".zfill(12)
    return time_string
