import pytest
import sys
from unittest.mock import patch, MagicMock
import requests
from utils.api import DbtCloudApi, JobMonitor
from dbt_heartbeat.main import main

skip_if_not_macos = pytest.mark.skipif(
    sys.platform != "darwin", reason="Notification tests require macOS (pync)"
)


@skip_if_not_macos
def test_end_to_end_flow(capsys):
    """Test the entire flow from command-line input to job completion and notification."""
    with patch("dbt_heartbeat.main.job_monitor") as mock_monitor, patch(
        "dbt_heartbeat.main.dbt_api"
    ) as mock_api, patch(
        "utils.notifications.run_notifs.Notifier.notify"
    ) as mock_notify:
        # Setup mock responses
        mock_monitor.monitor_job.return_value = {
            "name": "Test Integration Job # 1",
            "status": "Success",
            "status_humanized": "Success",
            "duration": "4 minutes, 20 seconds",
            "duration_humanized": "4 minutes, 20 seconds",
            "run_duration_humanized": "4 minutes, 20 seconds",
            "queued_duration_humanized": "0s",
            "finished_at": "11:11 AM",
            "is_success": True,
            "is_error": False,
            "in_progress": False,
            "job_id": 12345,
            "run_id": 67890,
        }
        mock_api.get_job_run_info.return_value = {
            "name": "Test Integration Job # 1",
            "status": "Success",
            "status_humanized": "Success",
            "duration": "4 minutes, 20 seconds",
            "duration_humanized": "4 minutes, 50 seconds",
            "run_duration_humanized": "4 minutes, 50 seconds",
            "queued_duration_humanized": "0s",
            "finished_at": "11:11 AM",
            "is_success": True,
            "is_error": False,
            "in_progress": False,
            "job_id": 12345,
            "run_id": 67890,
        }

        # Run the main function
        with patch("sys.argv", ["script.py", "12345"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        # Verify the flow
        mock_monitor.monitor_job.assert_called_once_with("12345", 30)
        mock_api.get_job_run_info.assert_called_once_with("12345")
        mock_notify.assert_called_once()


@skip_if_not_macos
def test_end_to_end_flow_with_slack(capsys):
    """Test the entire flow from command-line input to job completion with Slack notification."""
    with patch("dbt_heartbeat.main.job_monitor") as mock_monitor, patch(
        "dbt_heartbeat.main.dbt_api"
    ) as mock_api, patch(
        "utils.notifications.run_notifs.requests.post"
    ) as mock_slack_post, patch(
        "utils.notifications.run_notifs.os.getenv"
    ) as mock_getenv:
        # Setup mock responses
        mock_monitor.monitor_job.return_value = {
            "name": "Test Integration Job # 1",
            "status": "Success",
            "status_humanized": "Success",
            "duration": "4 minutes, 20 seconds",
            "duration_humanized": "4 minutes, 20 seconds",
            "run_duration_humanized": "4 minutes, 20 seconds",
            "queued_duration_humanized": "0s",
            "finished_at": "11:11 AM",
            "is_success": True,
            "is_error": False,
            "in_progress": False,
            "job_id": 12345,
            "run_id": 67890,
        }
        mock_api.get_job_run_info.return_value = {
            "name": "Test Integration Job # 1",
            "status": "Success",
            "status_humanized": "Success",
            "duration": "4 minutes, 20 seconds",
            "duration_humanized": "4 minutes, 50 seconds",
            "run_duration_humanized": "4 minutes, 50 seconds",
            "queued_duration_humanized": "0s",
            "finished_at": "11:11 AM",
            "is_success": True,
            "is_error": False,
            "in_progress": False,
            "job_id": 12345,
            "run_id": 67890,
        }
        mock_getenv.return_value = "https://hooks.slack.com/services/test/webhook/url"
        mock_slack_response = MagicMock()
        mock_slack_response.raise_for_status.return_value = None
        mock_slack_post.return_value = mock_slack_response

        # Run the main function with --slack flag
        with patch("sys.argv", ["script.py", "12345", "--slack"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        # Verify the flow
        mock_monitor.monitor_job.assert_called_once_with("12345", 30)
        mock_api.get_job_run_info.assert_called_once_with("12345")
        mock_slack_post.assert_called_once()

        # Verify Slack message content
        call_args = mock_slack_post.call_args
        assert call_args[0][0] == "https://hooks.slack.com/services/test/webhook/url"
        blocks = call_args[1]["json"]["blocks"]
        assert blocks[0]["text"]["text"] == "✅ dbt Job Status Update"
        assert any(
            "Test Integration Job # 1" in field["text"] for field in blocks[1]["fields"]
        )
        assert any("Success" in field["text"] for field in blocks[1]["fields"])


def test_mock_api_integration():
    """Test the interaction between DbtCloudApi and JobMonitor with a fully mocked API."""
    mock_api = MagicMock(spec=DbtCloudApi)
    monitor = JobMonitor(mock_api)

    # Setup mock responses
    mock_api.get_job_run_info.side_effect = [
        {
            "name": "Integration Test Job # 2",
            "status": "Running",
            "status_humanized": "Running",
            "duration": "1 minutes, 10 seconds",
            "duration_humanized": "1 minutes, 10 seconds",
            "run_duration_humanized": "1 minutes, 10 seconds",
            "queued_duration_humanized": "0s",
            "finished_at": None,
            "is_success": False,
            "is_error": False,
            "in_progress": True,
            "job_id": 12345,
            "run_id": 67890,
        },
        {
            "name": "Integration Test Job # 2",
            "status": "Running",
            "status_humanized": "Running",
            "duration": "1 minutes, 40 seconds",
            "duration_humanized": "1 minutes, 40 seconds",
            "run_duration_humanized": "1 minutes, 40 seconds",
            "queued_duration_humanized": "0s",
            "finished_at": None,
            "is_success": False,
            "is_error": False,
            "in_progress": True,
            "job_id": 12345,
            "run_id": 67890,
        },
        {
            "name": "Test Job # 3",
            "status": "Success",
            "status_humanized": "Success",
            "duration": "2 minutes, 10 seconds",
            "duration_humanized": "2 minutes, 10 seconds",
            "run_duration_humanized": "2 minutes, 10 seconds",
            "queued_duration_humanized": "0s",
            "finished_at": "11:11 AM",
            "is_success": True,
            "is_error": False,
            "in_progress": False,
            "job_id": 12345,
            "run_id": 67890,
        },
    ]

    result = monitor.monitor_job("12345", poll_interval=1)
    assert result["status"] == "Success"
    assert mock_api.get_job_run_info.call_count == 3


def test_empty_api_response():
    """Test handling of empty API responses."""
    with patch("utils.api.dbt_cloud_api.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {}}
        mock_get.return_value = mock_response

        api = DbtCloudApi()
        result = api.get_job_run_info("12345")
        assert result == {}


def test_api_error_handling():
    """Test handling of API errors."""
    with patch("utils.api.dbt_cloud_api.requests.get") as mock_get:
        # Test 404 error
        mock_get.side_effect = requests.exceptions.HTTPError("404 Client Error")
        api = DbtCloudApi()
        result = api.get_job_run_info("invalid_id")
        assert result == {}

        # Test network error
        mock_get.side_effect = requests.exceptions.ConnectionError()
        result = api.get_job_run_info("12345")
        assert result == {}


def test_malformed_api_response():
    """Test handling of malformed API responses."""
    with patch("utils.api.dbt_cloud_api.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        api = DbtCloudApi()
        result = api.get_job_run_info("12345")
        assert result == {}
