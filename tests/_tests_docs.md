# Test Documentation

This document provides detailed information about the test suite for dbt-heartbeat.

## Test Structure

The test suite is organized into several categories, each focusing on different aspects of the application:

### 1. Main Tests (`tests/test_main.py`)

Tests the core functionality of the tool:
- Job monitoring
- API integration
- Command-line argument handling
- Log level configuration
- Custom polling intervals

Key test functions:
- `test_main_with_valid_job_id`: Verifies basic job monitoring functionality
- `test_custom_poll_interval`: Tests custom polling interval configuration
- `test_log_level_changes`: Verifies different log level settings
- `test_main_with_invalid_job_id`: Tests error handling for invalid job IDs
- `test_main_with_missing_env_vars`: Verifies environment variable validation

### 2. Integration Tests (`tests/test_integration.py`)

Tests the integration between different components:
- End-to-end job monitoring flow
- API response handling
- Error scenarios
- Empty and malformed response handling

Key test functions:
- `test_end_to_end_flow`: Verifies complete job monitoring workflow
- `test_mock_api_integration`: Tests API and JobMonitor interaction
- `test_empty_api_response`: Tests handling of empty API responses
- `test_api_error_handling`: Tests API error scenarios
- `test_malformed_api_response`: Tests handling of malformed API responses

### 3. Notification Tests (`tests/test_notifications.py`)

Tests the notification system:
- Mocked notification tests for different job statuses
- Notification content verification
- Platform-agnostic testing

Key test functions:
- `test_notification_cancelled_mock`: Tests cancelled job notifications
- `test_notification_error_mock`: Tests error job notifications
- `test_partial_environment_variables`: Tests environment variable validation
- `test_invalid_environment_variables`: Tests invalid environment variable handling

### 4. Configuration Tests

Tests for configuration and environment setup:
- Environment variable validation
- Configuration loading
- Error handling for missing/invalid configuration

## Test Fixtures (`conftest.py`)

The `conftest.py` file contains shared test fixtures that are automatically available to all test files. These fixtures provide reusable test components and mock data.

### Key Fixtures

1. **API and Monitor Mocks**
   ```python
   @pytest.fixture
   def mock_dbt_api():
       """Fixture that provides a mocked DbtCloudApi instance."""
       return MagicMock(spec=DbtCloudApi)

   @pytest.fixture
   def mock_job_monitor(mock_dbt_api):
       """Fixture that provides a mocked JobMonitor instance."""
       return MagicMock(spec=JobMonitor)
   ```
   - Provides mocked instances of the API and JobMonitor classes
   - Ensures consistent mocking across all tests
   - `mock_job_monitor` depends on `mock_dbt_api`

2. **Platform Mocking**
   ```python
   @pytest.fixture
   def mock_platform():
       """Fixture to mock platform as macOS."""
       with patch("sys.platform", "darwin"):
           yield
   ```
   - Mocks the system platform for platform-specific tests
   - Particularly useful for notification tests that require macOS

3. **Job Data Fixtures**
   ```python
   @pytest.fixture
   def sample_job_run_data():
       """Fixture providing a basic job run data structure."""
       return {
           "id": 12345,
           "job_id": 67890,
           "name": "Test Job",
           "status": "Success",
           # ... other fields ...
       }

   @pytest.fixture
   def job_states():
       """Fixture providing different job states for testing."""
       return {
           "success": {...},
           "error": {...},
           "cancelled": {...}
       }
   ```
   - Provides consistent test data across all tests
   - Includes different job states for various test scenarios

4. **Environment Variable Fixtures**
   ```python
   @pytest.fixture
   def mock_env_vars(monkeypatch):
       """Fixture to set up environment variables for testing."""
       monkeypatch.setenv("DBT_CLOUD_API_KEY", "test_key")
       monkeypatch.setenv("DBT_CLOUD_ACCOUNT_ID", "test_account")
   ```
   - Sets up environment variables for testing
   - Uses pytest's `monkeypatch` fixture for clean environment management

5. **Command-Line Argument Fixtures**
   ```python
   @pytest.fixture
   def mock_sys_argv():
       """Fixture to mock sys.argv for command-line argument testing."""
       def _mock_argv(*args):
           return patch.object(sys, "argv", ["script.py"] + list(args))
       return _mock_argv
   ```
   - Provides a way to mock command-line arguments
   - Returns a function that can be used to set different argument combinations

### Usage in Tests

Fixtures can be used in test functions by including them as parameters:
```python
def test_something(mock_dbt_api, sample_job_run_data, mock_env_vars):
    # Test code here
```

## Mock Data

The tests use mock data that matches the format returned by `DbtCloudApi.get_job_run_info`:

```python
job_data = {
    "name": "Test Job",
    "status": "Success",
    "status_humanized": "Success",
    "duration": "4 minutes, 20 seconds",
    "duration_humanized": "4 minutes, 20 seconds",
    "run_duration_humanized": "4 minutes, 20 seconds",
    "queued_duration_humanized": "0s",
    "finished_at": "11:11 AM" ,
    "is_success": True,
    "is_error": False,
    "in_progress": False,
    "job_id": 12345,
    "run_id": 67890
}
```

## Mocking Strategy

The tests use Python's `unittest.mock` to mock external dependencies:

1. **API Calls**
   ```python
   @patch('dbt_heartbeat.main.dbt_api')
   ```

2. **System Notifications**
   ```python
   @patch('utils.notifications.os_notifs.Notifier.notify')
   ```

3. **Environment Variables**
   ```python
   @patch.dict(os.environ, {
       'DBT_CLOUD_API_KEY': 'test_key',
       'DBT_CLOUD_ACCOUNT_ID': 'test_account'
   })
   ```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_main.py
pytest tests/test_integration.py
pytest tests/test_notifications.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src
```

### Test Selection

You can run specific test functions using:
```bash
pytest tests/test_main.py::test_main_with_valid_job_id
```

### Coverage Reports

Generate coverage reports with:
```bash
pytest --cov=src --cov-report=term-missing
```
