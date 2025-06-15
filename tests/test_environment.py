from unittest.mock import patch
import pytest
from dbt_heartbeat.main import main
from utils.config import validate_environment_vars


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


@patch("dbt_heartbeat.main.job_monitor")
@patch("dbt_heartbeat.main.dbt_api")
@patch("utils.notifications.run_notifs.requests.post")
@patch("utils.notifications.run_notifs.os.getenv")
@patch("dbt_heartbeat.main.validate_environment_vars")
def test_slack_flag_missing_webhook_environment_var(
    mock_validate_env_vars,
    mock_getenv,
    mock_slack_post,
    mock_dbt_api,
    mock_job_monitor,
    sample_job_run_data,
    mock_job_run_info,
    mock_sys_argv,
    caplog,
):
    """Test that appropriate error is logged when Slack webhook URL is missing."""
    # Setup mocks
    mock_job_monitor.monitor_job.return_value = sample_job_run_data
    mock_dbt_api.get_job_run_info.return_value = mock_job_run_info
    mock_getenv.return_value = None  # Simulate missing webhook URL
    mock_validate_env_vars.return_value = []  # No missing required env vars

    with mock_sys_argv("12345", "--slack"):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0

    # Verify error was logged
    assert any(
        "SLACK_WEBHOOK_URL environment variable not set" in record.message
        for record in caplog.records
    )
    # Verify no Slack notification was sent
    mock_slack_post.assert_not_called()
