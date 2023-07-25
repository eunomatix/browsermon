import sys
import os 
import pytest
import src.controller as controller

def test_get_installed_browsers():
    browsers = controller.get_installed_browsers()

    browser_set = {'chrome', 'firefox', 'edge'}
    assert browsers == browser_set

@pytest.mark.parametrize(
    "options, expected", [
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
        ({
            'browser': 'chrome',
            'mode': 'real-time',
            'schedule_window': '1m',
            'logdir': '../history',
            'logmode': 'csv',
            'rotation': '1m',
            'deletion': '1w'

        },
        {
            'browser': 'chrome',
            'mode': 'real-time',
            'schedule_window': '1m',
            'logdir': '../history',
            'logmode': 'csv',
            'rotation': '1m',
            'deletion': '1w'
        })
    ], indirect=["options"]
)
def test_config_reader_with_options(options, expected):
    config = controller.config_reader(options)
    assert config == expected