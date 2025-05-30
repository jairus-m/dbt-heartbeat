from unittest.mock import patch, MagicMock
from utils.notifications import send_system_notification
from tests.conftest import assert_notification_content


@patch("utils.notifications.os_notifs.sys")
@patch("utils.notifications.os_notifs.Notifier")
def test_notification_cancelled_mock(
    mock_notifier, mock_sys, sample_job_run_data, job_states
):
    """Test that notifications are sent correctly when a job is cancelled."""
    # Setup the mocks
    mock_sys.platform = "darwin"

    job_data = {**sample_job_run_data, **job_states["cancelled"]}
    send_system_notification(job_data)
    mock_notifier.notify.assert_called_once()
    message = mock_notifier.notify.call_args[0][0]
    assert_notification_content(message, "Test Job", "Cancelled")


@patch("utils.notifications.os_notifs.sys")
@patch("utils.notifications.os_notifs.Notifier")
def test_notification_error_mock(
    mock_notifier, mock_sys, sample_job_run_data, job_states
):
    """Test that notifications are sent correctly when a job fails."""
    # Setup the mocks
    mock_sys.platform = "darwin"

    job_data = {**sample_job_run_data, **job_states["error"]}
    send_system_notification(job_data)
    mock_notifier.notify.assert_called_once()
    message = mock_notifier.notify.call_args[0][0]
    assert_notification_content(message, "Test Job", "Error", error_msg="Test error")


@patch("utils.notifications.os_notifs.sys")
@patch("utils.notifications.os_notifs.win10toast", create=True)
def test_windows_notification_cancelled_mock(
    mock_win10toast, mock_sys, sample_job_run_data, job_states
):
    """Test that Windows notifications are sent correctly when a job is cancelled."""
    # Setup the mocks
    mock_sys.platform = "win32"
    mock_toaster = MagicMock()
    mock_win10toast.ToastNotifier.return_value = mock_toaster

    # Create the toaster instance in the module
    with patch("utils.notifications.os_notifs.toaster", mock_toaster, create=True):
        job_data = {**sample_job_run_data, **job_states["cancelled"]}
        send_system_notification(job_data)
        mock_toaster.show_toast.assert_called_once()

        # Get the arguments passed to show_toast
        call_args = mock_toaster.show_toast.call_args[0]
        title = call_args[0]
        message = call_args[1]

        # Assert the notification content
        assert "dbt Job Status Update" in title
        assert_notification_content(message, "Test Job", "Cancelled")


@patch("utils.notifications.os_notifs.sys")
@patch("utils.notifications.os_notifs.win10toast", create=True)
def test_windows_notification_error_mock(
    mock_win10toast, mock_sys, sample_job_run_data, job_states
):
    """Test that Windows notifications are sent correctly when a job fails."""
    # Setup the mocks
    mock_sys.platform = "win32"
    mock_toaster = MagicMock()
    mock_win10toast.ToastNotifier.return_value = mock_toaster

    # Create the toaster instance in the module
    with patch("utils.notifications.os_notifs.toaster", mock_toaster, create=True):
        job_data = {**sample_job_run_data, **job_states["error"]}
        send_system_notification(job_data)
        mock_toaster.show_toast.assert_called_once()

        # Get the arguments passed to show_toast
        call_args = mock_toaster.show_toast.call_args[0]
        title = call_args[0]
        message = call_args[1]

        # Assert the notification content
        assert "dbt Job Status Update" in title
        assert_notification_content(
            message, "Test Job", "Error", error_msg="Test error"
        )


@patch("utils.notifications.os_notifs.sys")
@patch("utils.notifications.os_notifs.win10toast", create=True)
def test_windows_notification_success_mock(
    mock_win10toast, mock_sys, sample_job_run_data, job_states
):
    """Test that Windows notifications are sent correctly when a job succeeds."""
    # Setup the mocks
    mock_sys.platform = "win32"
    mock_toaster = MagicMock()
    mock_win10toast.ToastNotifier.return_value = mock_toaster

    # Create the toaster instance in the module
    with patch("utils.notifications.os_notifs.toaster", mock_toaster, create=True):
        job_data = {**sample_job_run_data, **job_states["success"]}
        send_system_notification(job_data)
        mock_toaster.show_toast.assert_called_once()

        # Get the arguments passed to show_toast
        call_args = mock_toaster.show_toast.call_args[0]
        title = call_args[0]
        message = call_args[1]

        # Assert the notification content
        assert "dbt Job Status Update" in title
        assert_notification_content(message, "Test Job", "Success")


@patch("utils.notifications.os_notifs.sys")
@patch("utils.notifications.os_notifs.win10toast", create=True)
def test_windows_notification_parameters(
    mock_win10toast, mock_sys, sample_job_run_data, job_states
):
    """Test that Windows notifications are sent with correct parameters."""
    # Setup the mocks
    mock_sys.platform = "win32"
    mock_toaster = MagicMock()
    mock_win10toast.ToastNotifier.return_value = mock_toaster

    # Create the toaster instance in the module
    with patch("utils.notifications.os_notifs.toaster", mock_toaster, create=True):
        job_data = {**sample_job_run_data, **job_states["success"]}
        send_system_notification(job_data)

        # Get the keyword arguments passed to show_toast
        call_kwargs = mock_toaster.show_toast.call_args[1]

        # Assert the notification parameters
        assert call_kwargs["duration"] == 10
        assert call_kwargs["threaded"] is True
