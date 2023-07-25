import pytest
import os 
import configparser

@pytest.fixture
def options(request):
    options = request.param
    config = configparser.ConfigParser()
    if 'default' not in config.sections():
        config.add_section('default')
    for key, value in options.items():
        config.set('default', key, value)

    config_file_path = "browsermon.conf"
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)
    return config_file_path




