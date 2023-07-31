import pytest 
from unittest.mock import Mock
from src import controller

@pytest.mark.parametrize(
    "test_config_file, expected", [
        # Test when all options are provided correctly 
        ({
            'browser': 'edge', 
            'mode': 'real-time', 
            'schedule_window': '1m', 
            'logdir': '../history', 
            'logmode': 'csv', 
            'rotation': '1m', 
            'deletion': '1w'
        },
        {
            'browser': 'edge',
            'mode': 'real-time',
            'schedule_window': '1m',
            'logdir': '../history',
            'logmode': 'csv',
            'rotation': '1m',
            'deletion': '1w'
        }),
        # Test when all options are provided correctly except browser
        ({
            'browser': None,
            'mode': 'real-time',
            'schedule_window': '1m',
            'logdir': '../history',
            'logmode': 'csv',
            'rotation': '1m',
            'deletion': '1w'

        },
        {
            'browser': 'all', # default value
            'mode': 'real-time',
            'schedule_window': '1m',
            'logdir': '../history',
            'logmode': 'csv',
            'rotation': '1m',
            'deletion': '1w'
        }),
        # Test when schedule_window, rotation, and deletion have invalid values
        ({
            'browser': 'firefox',
            'mode': 'real-time',
            'schedule_window': 'abc',
            'logdir': '../logs',
            'logmode': 'json',
            'rotation': 'xyz',
            'deletion': 'qwe'
        },
        {
            'browser': 'firefox',
            'mode': 'real-time',
            'schedule_window': '1m',   # default value
            'logdir': '../logs',
            'logmode': 'json',
            'rotation': '1m',          # default value
            'deletion': '1w'           # default value
        }),

        # Test when logdir is empty
        ({
            'browser': 'firefox',
            'mode': 'real-time',
            'schedule_window': '1m',
            'logdir': '',
            'logmode': 'json',
            'rotation': '1d',
            'deletion': '1w'
        },
        {
            'browser': 'firefox',
            'mode': 'real-time',
            'schedule_window': '1m',
            'logdir': '/opt/browsermon/history',  # default value
            'logmode': 'json',
            'rotation': '1d',
            'deletion': '1w'
        }),

        # Test when logmode is invalid
        ({
            'browser': 'firefox',
            'mode': 'real-time',
            'schedule_window': '1m',
            'logdir': '../logs',
            'logmode': 'txt',
            'rotation': '1d',
            'deletion': '1w'
        },
        {
            'browser': 'firefox',
            'mode': 'real-time',
            'schedule_window': '1m',
            'logdir': '../logs',
            'logmode': 'csv',          # default value
            'rotation': '1d',
            'deletion': '1w'
        }),

        # Test missing values for all options (defaults will be used)
        ({},
        {
            'browser': 'all',
            'mode': 'scheduled',
            'schedule_window': '1m',
            'logdir': '/opt/browsermon/history',
            'logmode': 'csv',
            'rotation': '1m',
            'deletion': '1w'
        }),
    ], indirect=["test_config_file"]
)
def test_config_reader(test_config_file, expected):
    logger = Mock()
    config = controller.config_reader(logger, test_config_file)
    assert config == expected
