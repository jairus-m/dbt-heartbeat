import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the src directory to the Python path
src_path = str(Path(__file__).parent.parent / "src")
sys.path.insert(0, src_path)

from utils.api import DbtCloudApi, JobMonitor  # noqa: E402


@pytest.fixture
def mock_dbt_api():
    """Fixture that provides a mocked DbtCloudApi instance."""
    return MagicMock(spec=DbtCloudApi)


@pytest.fixture
def mock_job_monitor(mock_dbt_api):
    """Fixture that provides a mocked JobMonitor instance."""
    return MagicMock(spec=JobMonitor)


@pytest.fixture
def mock_platform():
    """Fixture to mock platform as macOS."""
    with patch("sys.platform", "darwin"):
        yield


@pytest.fixture
def sample_job_run_data():
    """Fixture providing a basic job run data structure."""
    return {
        "id": 12345,
        "job_id": 67890,
        "name": "Test Job",
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
    }


@pytest.fixture
def mock_job_run_info(sample_job_run_data):
    """Fixture providing mock job run info for API responses."""
    return {
        "id": sample_job_run_data["id"],
        "job_id": sample_job_run_data["job_id"],
        "name": sample_job_run_data["name"],
        "status": sample_job_run_data["status"],
        "started_at": "2024-03-20T10:00:00Z",
        "finished_at": sample_job_run_data["finished_at"],
        "duration": sample_job_run_data["duration"],
        "duration_humanized": sample_job_run_data["duration_humanized"],
        "run_duration_humanized": sample_job_run_data["run_duration_humanized"],
        "queued_duration_humanized": sample_job_run_data["queued_duration_humanized"],
        "project_id": 1,
        "environment_id": 1,
        "is_success": sample_job_run_data["is_success"],
        "is_error": sample_job_run_data["is_error"],
        "in_progress": sample_job_run_data["in_progress"],
    }


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to set up environment variables for testing."""
    monkeypatch.setenv("DBT_CLOUD_API_KEY", "test_key")
    monkeypatch.setenv("DBT_CLOUD_ACCOUNT_ID", "test_account")
    return {"DBT_CLOUD_API_KEY": "test_key", "DBT_CLOUD_ACCOUNT_ID": "test_account"}


@pytest.fixture
def job_states():
    """Fixture providing different job states for testing."""
    return {
        "success": {
            "status": "Success",
            "status_humanized": "Success",
            "is_success": True,
            "is_error": False,
        },
        "error": {
            "status": "Error",
            "status_humanized": "Error",
            "is_success": False,
            "is_error": True,
            "error_message": "Test error",
        },
        "cancelled": {
            "status": "Cancelled",
            "status_humanized": "Cancelled",
            "is_success": False,
            "is_error": False,
        },
    }


@pytest.fixture
def mock_sys_argv():
    """Fixture to mock sys.argv for command-line argument testing."""

    def _mock_argv(*args):
        return patch.object(sys, "argv", ["script.py"] + list(args))

    return _mock_argv


def assert_notification_content(
    message, job_name, status, duration="4 minutes, 20 seconds", error_msg=None
):
    """Helper function to assert notification message content."""
    assert job_name in message
    assert status in message
    assert duration in message
    assert "11:11 AM" in message
    if error_msg:
        assert error_msg in message
