import pytest
from unittest.mock import Mock, patch

from src import controller


def test_get_installed_browsers():
    browsers = controller.get_installed_browsers()

    browser_set = {'chrome', 'firefox', 'edge'}
    assert browsers == browser_set

def test_monitor_subprocess(setup_launcher):
    process_mock = Mock(wait=Mock(side_effect=[None, None, None, None, None, None]), returncode=1)
    with patch('subprocess.Popen') as mocked_popen:
        mocked_popen.return_value = process_mock
        setup_launcher.monitor_subprocess(process_mock, 'edge')
        setup_launcher.logger.info.assert_any_call("Relaunched the reader that exited with error")
