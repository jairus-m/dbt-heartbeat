import pytest
import sys
from unittest.mock import patch
from utils.notifications import send_system_notification
from utils.config import validate_environment_vars
from tests.conftest import assert_notification_content

skip_if_not_macos = pytest.mark.skipif(
    sys.platform != "darwin", reason="Notification tests require macOS (pync)"
)


@skip_if_not_macos
@patch("utils.notifications.os_notifs.Notifier")
def test_notification_cancelled_mock(mock_notifier, sample_job_run_data, job_states):
    """Test that notifications are sent correctly when a job is cancelled."""
    job_data = {**sample_job_run_data, **job_states["cancelled"]}
    send_system_notification(job_data)
    mock_notifier.notify.assert_called_once()
    message = mock_notifier.notify.call_args[0][0]
    assert_notification_content(message, "Test Job", "Cancelled")


@skip_if_not_macos
@patch("utils.notifications.os_notifs.Notifier")
def test_notification_error_mock(mock_notifier, sample_job_run_data, job_states):
    """Test that notifications are sent correctly when a job fails."""
    job_data = {**sample_job_run_data, **job_states["error"]}
    send_system_notification(job_data)
    mock_notifier.notify.assert_called_once()
    message = mock_notifier.notify.call_args[0][0]
    assert_notification_content(message, "Test Job", "Error", error_msg="Test error")


def test_partial_environment_variables(monkeypatch):
    """Test behavior when only one of the required environment variables is set."""
    # Set only API key
    monkeypatch.setenv("DBT_CLOUD_API_KEY", "test_key")
    monkeypatch.delenv("DBT_CLOUD_ACCOUNT_ID", raising=False)

    missing_vars = validate_environment_vars(
        ["DBT_CLOUD_API_KEY", "DBT_CLOUD_ACCOUNT_ID"]
    )
    assert "DBT_CLOUD_ACCOUNT_ID" in missing_vars
    assert len(missing_vars) == 1


def test_invalid_environment_variables(monkeypatch):
    """Test handling of invalid environment variables."""
    # Set invalid API key (empty string)
    monkeypatch.setenv("DBT_CLOUD_API_KEY", "")
    monkeypatch.setenv("DBT_CLOUD_ACCOUNT_ID", "invalid_id")

    missing_vars = validate_environment_vars(
        ["DBT_CLOUD_API_KEY", "DBT_CLOUD_ACCOUNT_ID"]
    )
    assert "DBT_CLOUD_API_KEY" in missing_vars


### IF WANT TO GET NOTIFS IN REAL TIME DURING TESTS UNCOMMENT THIS

# @skip_if_not_macos
# def test_notification_success():
#     """Test that notifications are actually sent to macOS Notification Center."""
#     job_data = {
#         "name": "Test Job w/ Success Status",
#         "status": "Success",
#         "status_humanized": "Success",
#         "duration": "4 minutes, 20 seconds",
#         "duration_humanized": "4 minutes, 20 seconds",
#         "run_duration_humanized": "4 minutes, 20 seconds",
#         "queued_duration_humanized": "0s",
#         "finished_at": "11:11 AM" ,
#         "is_success": True,
#         "is_error": False,
#         "in_progress": False,
#         "job_id": 12345,
#         "run_id": 67890
#     }
#     # This will send a real notification to macOS Notification Center
#     send_system_notification(job_data)

# @skip_if_not_macos
# def test_notification_error():
#     """Test that notifications are actually sent to macOS Notification Center."""
#     job_data = {
#         "name": "Test Job w/ Error Status",
#         "status": "Error",
#         "status_humanized": "Error",
#         "duration": "4 minutes, 20 seconds",
#         "duration_humanized": "4 minutes, 20 seconds",
#         "run_duration_humanized": "4 minutes, 20 seconds",
#         "queued_duration_humanized": "0s",
#         "finished_at": "11:11 AM" ,
#         "is_success": False,
#         "is_error": True,
#         "in_progress": False,
#         "job_id": 12345,
#         "run_id": 67890
#     }
#     # This will send a real notification to macOS Notification Center
#     send_system_notification(job_data)

# @skip_if_not_macos
# def test_notification_cancelled():
#     """Test that notifications are actually sent to macOS Notification Center."""
#     job_data = {
#         "name": "Test Job w/ Cancelled Status",
#         "status": "Cancelled",
#         "status_humanized": "Cancelled",
#         "duration": "4 minutes, 20 seconds",
#         "duration_humanized": "4 minutes, 20 seconds",
#         "run_duration_humanized": "4 minutes, 20 seconds",
#         "queued_duration_humanized": "0s",
#         "finished_at": "11:11 AM" ,
#         "is_success": False,
#         "is_error": False,
#         "in_progress": False,
#         "job_id": 12345,
#         "run_id": 67890
#     }
#     # This will send a real notification to macOS Notification Center
#     send_system_notification(job_data)
