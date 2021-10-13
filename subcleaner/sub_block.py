from datetime import timedelta
from math import floor


class SubBlock(object):
    orig_index: int
    content: str
    start_time: timedelta
    stop_time: timedelta
    regex_matches: int
    keep: bool

    def __init__(self, orig_index):
        self.orig_index = orig_index
        self.keep = True
        self.regex_matches = 0
        self.content = ""
        self.stop_time = timedelta()
        self.start_time = timedelta()

    def set_start_time(self, time: str) -> None:
        self.start_time = self._convert_to_timedelta(time)

    def set_stop_time(self, time):
        self.stop_time = self._convert_to_timedelta(time)

    @staticmethod
    def _convert_to_timedelta(time) -> timedelta:
        time = time.replace(".", ",")
        split = time.split(":")

        return timedelta(hours=float(split[0]),
                         minutes=float(split[1]),
                         seconds=float(split[2].split(",")[0]),
                         milliseconds=float(split[2].split(",")[1]))

    @staticmethod
    def _convert_from_timedelta(time: timedelta) -> str:
        time_left = time.total_seconds()

        hours = floor(time_left / (60 * 60))
        time_left = time_left - hours * (60 * 60)

        minutes = floor(time_left / 60)
        time_left = time_left - minutes * 60

        seconds = floor(time_left)
        time_left = time_left - seconds

        mill = floor(time_left * 1000)

        hours_str = str(hours)
        minutes_str = str(minutes)
        seconds_str = str(seconds)
        mill_str = str(mill)

        hours_str = "0" * (2 - len(hours_str)) + hours_str
        minutes_str = "0" * (2 - len(minutes_str)) + minutes_str
        seconds_str = "0" * (2 - len(seconds_str)) + seconds_str
        mill_str = mill_str + "0" * (3 - len(mill_str))

        return hours_str + ":" + minutes_str + ":" + seconds_str + "," + mill_str

    def __repr__(self) -> str:

        string = (self._convert_from_timedelta(self.start_time) +
                  " --> " +
                  self._convert_from_timedelta(self.stop_time) +
                  "\n")
        string += self.content
        return string

