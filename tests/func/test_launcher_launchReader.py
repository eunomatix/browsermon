import pytest
from unittest.mock import Mock, patch
from src import launcher

@pytest.mark.parametrize("options, return_value", [
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
])

def test_launch_reader(options, return_value):
    with patch('subprocess.Popen') as mocked_popen, patch('threading.Thread') as mocked_thread:
        mocked_popen.return_value = Mock(**return_value)
        installed_browsers = ['edge']
        logger = Mock()
        setup_launcher = launcher.Launcher(installed_browsers, logger, options)
        browser = options['browser']
        setup_launcher.launch_reader(browser)
        setup_launcher.logger.info.assert_any_call(f'Invoking {browser}_reader.py')
        setup_launcher.logger.info.assert_any_call(f'Invoked {browser}_reader.py')
        assert mocked_popen.called
        assert mocked_thread.called
