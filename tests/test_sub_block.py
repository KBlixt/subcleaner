import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "libs"))

import pytest  # noqa: E402

from subcleaner.sub_block import (  # noqa: E402
    ParsingException,
    SubBlock,
    time_string_to_timedelta,
)


@pytest.mark.parametrize(
    "timestamp",
    ["9999999999999999999:00:00,000", "1e400:00:00,000"],
)
def test_time_string_out_of_range_raises_valueerror(timestamp):
    # An absurd hours value overflows timedelta. It must raise ValueError (which
    # the callers already handle), not leak OverflowError.
    with pytest.raises(ValueError):
        time_string_to_timedelta(timestamp)


def test_sub_block_with_out_of_range_timestamp_reports_parsing_error():
    block = (
        "1\n"
        "9999999999999999999:00:00,000 --> 9999999999999999999:00:01,000\n"
        "hello"
    )
    with pytest.raises(ParsingException):
        SubBlock(block, 1)


def test_is_sub_block_header_rejects_out_of_range_timestamp():
    header = "9999999999999999999:00:00,000 --> 9999999999999999999:00:01,000"
    assert SubBlock.is_sub_block_header(header) is False
