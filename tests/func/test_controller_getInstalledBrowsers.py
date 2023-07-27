from src import controller

def test_get_installed_browsers():
    browsers = controller.get_installed_browsers()

    browser_set = {'chrome', 'firefox', 'edge'}
    assert browsers == browser_set