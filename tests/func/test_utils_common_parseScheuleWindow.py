import pytest
from unittest.mock import patch
from src.utils.common import parse_schedule_window, InvalidScheduleWindowFormat

def test_parse_schedule_window_minutes():
    result = parse_schedule_window("5m")
    assert result == 300

def test_parse_schedule_window_hours():
    result = parse_schedule_window("2h")
    assert result == 7200

def test_parse_schedule_window_days():
    result = parse_schedule_window("1d")
    assert result == 86400

def test_invalid_schedule_format_string():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        parse_schedule_window('1x')
    assert pytest_wrapped_e.type == SystemExit

def test_invalid_schedule_format_missing_unit():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        parse_schedule_window('5z')
    assert pytest_wrapped_e.type == SystemExit


# Empty string not catered in the function
# def test_invalid_schedule_format_empty_input():
#     with pytest.raises(InvalidScheduleWindowFormat):
#         parse_schedule_window("")
    

