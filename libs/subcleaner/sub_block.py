import dataclasses
import datetime
import util
from libs.subcleaner.subtitle import ParsingException


@dataclasses.dataclass()
class SubBlock(object):
    original_index: int
    content: str
    start_time: datetime.timedelta
    end_time: datetime.timedelta
    regex_matches = 0

    def __init__(self, block_string: str):
        rows = block_string.split("\n")

        self.original_index = int(rows[0])
        if len(rows) == 1:
            raise ParsingException(self.original_index)

        times = rows[1].replace(" ", "").split("-->")
        self.start_time = util.time_string_to_timedelta(times[0])
        self.end_time = util.time_string_to_timedelta(times[1])

        if len(rows) > 2:
            self.content = "\n".join(rows[2:])

    def __str__(self) -> str:
        string = f"{util.timedelta_to_time_string(self.start_time)} --> {util.timedelta_to_time_string(self.end_time)}\n" \
                 f"{self.content}"
        return string
