import pytest
import os
from unittest.mock import Mock
from src import launcher



@pytest.fixture
def test_config_file(request):
    options = request.param
    
    # Manually construct the configuration content
    config_content = '[default]\n'  # Start with the section name
    for key, value in options.items():
        if value is None: 
            config_content += f'{key}=\n'  # Add each key-value pair
        else: 
            config_content += f'{key}={value}\n'  # Add each key-value pair

    config_file_path = "tests/browsermon.conf"
    with open(config_file_path, 'w') as configfile:
        configfile.write(config_content)
    
    yield config_file_path
    os.remove(config_file_path)




@pytest.fixture
def setup_launcher(request):
    installed_browsers = ['edge']
    logger = Mock()
    options = request.param
    return launcher.Launcher(installed_browsers, logger, options)


