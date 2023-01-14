import datetime
import logging
import re

from . import util

logger = logging.getLogger("sub_block")


class SubBlock(object):
    original_index: int
    content: str
    start_time: datetime.timedelta
    end_time: datetime.timedelta
    regex_matches = 0
    styling_elements = []

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
            self.start_time = util.time_string_to_timedelta(times[0])
            self.end_time = util.time_string_to_timedelta(times[1])
        except ValueError:
            raise ParsingException(self.original_index)
        except IndexError:
            raise ParsingException(self.original_index)

        if len(rows) > 2:
            self.content = "\n".join(rows[2:]).strip()
        else:
            self.content = ""

    def equal_content(self, block: "SubBlock") -> bool:
        t = re.sub("[\\s.,:_-]", "", self.content)
        o = re.sub("[\\s.,:_-]", "", block.content)
        return t == o

    def __str__(self) -> str:
        string = f"{util.timedelta_to_time_string(self.start_time)} --> {util.timedelta_to_time_string(self.end_time)}\n" \
                 f"{self.content}"
        return string


class ParsingException(Exception):
    block_index: int
    subtitle_file: str

    def __init__(self, block_index):
        self.block_index = block_index

    def __str__(self) -> str:
        return f"Parsing error at block {self.block_index} in file {self.subtitle_file}."
