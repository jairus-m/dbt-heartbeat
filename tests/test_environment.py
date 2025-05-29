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
