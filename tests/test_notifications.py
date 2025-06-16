from unittest.mock import patch, MagicMock
from utils.notifications import send_system_notification, send_slack_notification
from tests.conftest import assert_notification_content


@patch("utils.notifications.run_notifs.sys")
@patch("utils.notifications.run_notifs.Notifier")
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


@patch("utils.notifications.run_notifs.sys")
@patch("utils.notifications.run_notifs.Notifier")
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


@patch("utils.notifications.run_notifs.sys")
@patch("utils.notifications.run_notifs.win10toast", create=True)
def test_windows_notification_cancelled_mock(
    mock_win10toast, mock_sys, sample_job_run_data, job_states
):
    """Test that Windows notifications are sent correctly when a job is cancelled."""
    # Setup the mocks
    mock_sys.platform = "win32"
    mock_toaster = MagicMock()
    mock_win10toast.ToastNotifier.return_value = mock_toaster

    # Create the toaster instance in the module
    with patch("utils.notifications.run_notifs.toaster", mock_toaster, create=True):
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


@patch("utils.notifications.run_notifs.sys")
@patch("utils.notifications.run_notifs.win10toast", create=True)
def test_windows_notification_error_mock(
    mock_win10toast, mock_sys, sample_job_run_data, job_states
):
    """Test that Windows notifications are sent correctly when a job fails."""
    # Setup the mocks
    mock_sys.platform = "win32"
    mock_toaster = MagicMock()
    mock_win10toast.ToastNotifier.return_value = mock_toaster

    # Create the toaster instance in the module
    with patch("utils.notifications.run_notifs.toaster", mock_toaster, create=True):
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


@patch("utils.notifications.run_notifs.sys")
@patch("utils.notifications.run_notifs.win10toast", create=True)
def test_windows_notification_success_mock(
    mock_win10toast, mock_sys, sample_job_run_data, job_states
):
    """Test that Windows notifications are sent correctly when a job succeeds."""
    # Setup the mocks
    mock_sys.platform = "win32"
    mock_toaster = MagicMock()
    mock_win10toast.ToastNotifier.return_value = mock_toaster

    # Create the toaster instance in the module
    with patch("utils.notifications.run_notifs.toaster", mock_toaster, create=True):
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


@patch("utils.notifications.run_notifs.sys")
@patch("utils.notifications.run_notifs.win10toast", create=True)
def test_windows_notification_parameters(
    mock_win10toast, mock_sys, sample_job_run_data, job_states
):
    """Test that Windows notifications are sent with correct parameters."""
    # Setup the mocks
    mock_sys.platform = "win32"
    mock_toaster = MagicMock()
    mock_win10toast.ToastNotifier.return_value = mock_toaster

    # Create the toaster instance in the module
    with patch("utils.notifications.run_notifs.toaster", mock_toaster, create=True):
        job_data = {**sample_job_run_data, **job_states["success"]}
        send_system_notification(job_data)

        # Get the keyword arguments passed to show_toast
        call_kwargs = mock_toaster.show_toast.call_args[1]

        # Assert the notification parameters
        assert call_kwargs["duration"] == 10
        assert call_kwargs["threaded"] is True


@patch("utils.notifications.run_notifs.requests.post")
@patch("utils.notifications.run_notifs.os.getenv")
def test_notification_success_slack_mock(
    mock_getenv, mock_post, sample_job_run_data, job_states
):
    """Test that Slack notifications are sent correctly when a job succeeds."""
    # Setup the mocks
    mock_getenv.return_value = "https://hooks.slack.com/services/test/webhook/url"
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    job_data = {**sample_job_run_data, **job_states["success"]}
    send_slack_notification(job_data)

    # Verify the webhook was called
    mock_post.assert_called_once()

    # Get the JSON payload that was sent
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://hooks.slack.com/services/test/webhook/url"

    blocks = call_args[1]["json"]["blocks"]

    # Verify the blocks structure
    assert blocks[0]["text"]["text"] == "✅ dbt Job Status Update"
    assert any("Test Job" in field["text"] for field in blocks[1]["fields"])
    assert any("Success" in field["text"] for field in blocks[1]["fields"])


@patch("utils.notifications.run_notifs.requests.post")
@patch("utils.notifications.run_notifs.os.getenv")
def test_notification_error_slack_mock(
    mock_getenv, mock_post, sample_job_run_data, job_states
):
    """Test that Slack notifications are sent correctly when a job fails."""
    # Setup the mocks
    mock_getenv.return_value = "https://hooks.slack.com/services/test/webhook/url"
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    job_data = {**sample_job_run_data, **job_states["error"]}
    send_slack_notification(job_data)

    # Verify the webhook was called
    mock_post.assert_called_once()

    # Get the JSON payload that was sent
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://hooks.slack.com/services/test/webhook/url"

    blocks = call_args[1]["json"]["blocks"]

    # Verify the blocks structure
    assert blocks[0]["text"]["text"] == "❌ dbt Job Status Update"
    assert any("Test Job" in field["text"] for field in blocks[1]["fields"])
    assert any("Error" in field["text"] for field in blocks[1]["fields"])
    # Find the error message block and verify its content
    error_block = next(
        (
            block
            for block in blocks
            if block.get("type") == "section"
            and "Error:" in block.get("text", {}).get("text", "")
        ),
        None,
    )
    assert error_block is not None
    assert "Test error" in error_block["text"]["text"]


@patch("utils.notifications.run_notifs.requests.post")
@patch("utils.notifications.run_notifs.os.getenv")
def test_notification_cancelled_slack_mock(
    mock_getenv, mock_post, sample_job_run_data, job_states
):
    """Test that Slack notifications are sent correctly when a job is cancelled."""
    # Setup the mocks
    mock_getenv.return_value = "https://hooks.slack.com/services/test/webhook/url"
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    job_data = {**sample_job_run_data, **job_states["cancelled"]}
    send_slack_notification(job_data)

    # Verify the webhook was called
    mock_post.assert_called_once()

    # Get the JSON payload that was sent
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://hooks.slack.com/services/test/webhook/url"

    blocks = call_args[1]["json"]["blocks"]

    # Verify the blocks structure
    assert blocks[0]["text"]["text"] == "⚠️ dbt Job Status Update"
    assert any("Test Job" in field["text"] for field in blocks[1]["fields"])
    assert any("Cancelled" in field["text"] for field in blocks[1]["fields"])
