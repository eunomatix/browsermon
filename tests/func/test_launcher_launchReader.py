import pytest
from unittest.mock import Mock, patch
@pytest.mark.parametrize("setup_launcher, return_value", [
    ({
        'browser': 'edge',
        'mode': 'real-time',
        'schedule_window': '1m',
        'logdir': '../history',
        'logmode': 'csv',
        'rotation': '1m',
        'deletion': '1w'
    }, {'stderr': "error", 'returncode': 1}),
    ({
        'browser': 'chrome',
        'mode': 'real-time',
        'schedule_window': '1m',
        'logdir': '../history',
        'logmode': 'csv',
        'rotation': '1m',
        'deletion': '1w'
    },{'stderr': "error", 'returncode': 2}),
    ({
        'browser': 'firefox',
        'mode': 'real-time',
        'schedule_window': '1m',
        'logdir': '../history',
        'logmode': 'csv',
        'rotation': '1m',
        'deletion': '1w'
    },{'stderr': "No error", 'returncode': 0})
], indirect=['setup_launcher'])

def test_launch_reader(setup_launcher, return_value):
    with patch('subprocess.Popen') as mocked_popen, patch('threading.Thread') as mocked_thread:
        mocked_popen.return_value = Mock(**return_value)
        browser = setup_launcher.options['browser']
        setup_launcher.launch_reader(browser)
        setup_launcher.logger.info.assert_any_call(f'Invoking {browser}_reader.py')
        setup_launcher.logger.info.assert_any_call(f'Invoked {browser}_reader.py')
        assert mocked_popen.called
        assert mocked_thread.called

    