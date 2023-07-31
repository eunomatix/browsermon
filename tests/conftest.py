import pytest
import os
from unittest.mock import Mock, patch
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
def setup_launcher():
    # This fixture is now empty, as the parameterization will be handled directly in the test function.
    pass


@pytest.fixture
def mock_write_logs():
    with patch("src.edge_reader.write_logs") as mock_method:
        yield mock_method


