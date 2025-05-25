from unittest.mock import patch, MagicMock
from utils.api import DbtCloudApi, JobMonitor


def test_dbt_cloud_api_initialization():
    """Test that DbtCloudApi initializes correctly."""
    api = DbtCloudApi()
    assert api is not None


@patch("utils.api.dbt_cloud_api.requests.get")
def test_get_job_run_info(mock_get):
    """Test getting job run info from the API."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": {
            "id": 12345,
            "status": "Success",
            "status_humanized": "Success",
            "duration_humanized": "4 minutes, 20 seconds",
            "run_duration_humanized": "4 minutes, 20 seconds",
            "queued_duration_humanized": "0s",
            "finished_at": "11:11 AM",
            "is_success": True,
            "is_error": False,
            "in_progress": False,
            "job_id": 67890,
        }
    }

    # Instead of hitting requests.get, we're returning the mock_get response
    mock_get.return_value = mock_response

    api = DbtCloudApi()
    result = api.get_job_run_info("12345")

    assert result is not None
    assert result["status"] == "Success"
    assert result["duration"] == "4 minutes, 20 seconds"


def test_job_monitor_initialization(mock_dbt_api):
    """Test that JobMonitor initializes correctly."""
    monitor = JobMonitor(mock_dbt_api)
    assert monitor is not None


@patch("time.sleep")
def test_monitor_job(mock_sleep, mock_dbt_api, sample_job_run_data):
    """Test job monitoring functionality."""
    # Setup mock API responses
    mock_dbt_api.get_job_run_info.side_effect = [
        {"status": "running", "in_progress": True},
        {"status": "running", "in_progress": True},
        sample_job_run_data,
    ]

    monitor = JobMonitor(mock_dbt_api)
    result = monitor.monitor_job("12345", poll_interval=1)

    assert result == sample_job_run_data
    assert mock_dbt_api.get_job_run_info.call_count == 3
    assert (
        mock_sleep.call_count == 1
    )  # Should sleep once between two in-progress checks
