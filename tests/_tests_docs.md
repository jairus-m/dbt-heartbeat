# Test Documentation

This document provides detailed information about the test suite for dbt-heartbeat.

__Note:__ To run the unit/integration tests locally, you need to have string values instantiated for the `DBT_CLOUD_API_KEY` and `DBT_CLOUD_ACCOUNT_ID` environment vars.

## Test Structure

### 1. Main Tests

- `test_main_with_valid_job_id`: Verifies basic job monitoring functionality
- `test_custom_poll_interval`: Tests custom polling interval configuration
- `test_log_level_changes`: Verifies different log level settings
- `test_main_with_invalid_job_id`: Tests error handling for invalid job IDs
- `test_main_with_missing_env_vars`: Verifies environment variable validation

### 2. Integration Tests

- `test_end_to_end_flow`: Verifies complete job monitoring workflow
- `test_mock_api_integration`: Tests API and JobMonitor interaction
- `test_empty_api_response`: Tests handling of empty API responses
- `test_api_error_handling`: Tests API error scenarios
- `test_malformed_api_response`: Tests handling of malformed API responses

### 3. Notification Tests

#### macOS Notifications
- `test_notification_cancelled_mock`: Tests cancelled job notifications
- `test_notification_error_mock`: Tests error job notifications

#### Windows Notifications
- `test_windows_notification_cancelled_mock`: Tests Windows cancelled job notifications
- `test_windows_notification_error_mock`: Tests Windows error job notifications
- `test_windows_notification_success_mock`: Tests Windows success job notifications
- `test_windows_notification_parameters`: Tests Windows notification parameters (duration, threading)

### 4. Environment Validation Tests
- `test_partial_environment_variables`: Tests behavior when only one of the required environment variables is set
- `test_invalid_environment_variables`: Tests handling of invalid environment variables (empty strings, invalid IDs)

## Test Fixtures (`conftest.py`)

The `conftest.py` file contains reusable test fixtures that are available to all test files.

### Key Fixtures

- `mock_dbt_api()`: Mocks `DbtCloudApi` class
- `mock_job_monitor()`: Mocks `JobMonitor` class
- `mock_platform()`: Mocks platform-specific behavior (macOS/Windows)
- `sample_job_run_data()`: Consistent sample data as returned by `DbtCloudApi`
- `job_states()`: Provides different scenarios for tests (success, error, cancelled)
- `mock_env_vars()`: Sets up environment variables for testing
- `mock_sys_argv()`: Provides a way to mock command-line arguments

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
   # macOS notifications
   @patch('utils.notifications.os_notifs.Notifier.notify')
   
   # Windows notifications
   @patch('utils.notifications.os_notifs.win10toast')
   ```

3. **Environment Variables**
   ```python
   @patch.dict(os.environ, {
       'DBT_CLOUD_API_KEY': 'test_key',
       'DBT_CLOUD_ACCOUNT_ID': 'test_account'
   })
   ```

4. **Platform Detection**
   ```python
   @patch('utils.notifications.os_notifs.sys')
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
pytest tests/test_environment.py

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

