import platform
import os
import pytest
from unittest.mock import patch, mock_open

# Assuming that the function to be tested is in a module called 'edge_reader'
from src.edge_reader import get_all_profiles


@patch("src.edge_reader.platform")
@patch("src.edge_reader.os")
@patch("src.edge_reader.get_profiles")
def test_get_all_profiles_linux(mock_get_profiles, mock_os, mock_platform, mock_write_logs):
    # Mock platform.system() to return "Linux"
    mock_platform.system.return_value = "Linux"
    mock_os.listdir.return_value = ["user1", "user2"]
    mock_os.path.exists.side_effect = [True, True]
    mock_get_profiles.side_effect = [
        {
            "Profile 1": {
                "profile_title": "Test Profile",
                "profile_username": "test_user",
                "profile_path": "/mocked/user/profile/dir/Profile 1",
                "username": "mock_username"
            }
        },
        {
            "Profile 2": {
                "profile_title": "Test Profile 2",
                "profile_username": "test_user_2",
                "profile_path": "/mocked/user/profile/dir/Profile 2",
                "username": "mock_username_2"
            }
        }
    ]

    expected_profiles = {
        "Profile 1": {
            "profile_title": "Test Profile",
            "profile_username": "test_user",
            "profile_path": "/mocked/user/profile/dir/Profile 1",
            "username": "mock_username"
        }, "Profile 2": {
            "profile_title": "Test Profile 2",
            "profile_username": "test_user_2",
            "profile_path": "/mocked/user/profile/dir/Profile 2",
            "username": "mock_username_2"
        }
    }

    profiles = get_all_profiles()
    assert profiles == expected_profiles


