import datetime
from pathlib import Path


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


def read_file(file: Path) -> str:
    file_content: str

    try:
        with file.open("r", encoding="utf-8") as opened_file:
            file_content = opened_file.read()
    except UnicodeDecodeError:
        with file.open("r", encoding="cp1252") as opened_file:
            file_content = opened_file.read()

    return file_content


def is_language_code(language_code: str) -> bool:
    return 2 <= len(language_code) <= 3

