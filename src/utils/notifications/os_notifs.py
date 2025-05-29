import logging
import sys

logger = logging.getLogger(__name__)

# Import platform-specific notification modules
if sys.platform == "darwin":
    from pync import Notifier
elif sys.platform == "win32":
    from win10toast import ToastNotifier

    toaster = ToastNotifier()
else:
    Notifier = None
    toaster = None


def get_status_emoji(job_details: dict) -> str:
    """
    Determine the appropriate emoji based on job status.
    Args:
        job_details (dict): Job details including success/error status
    Returns:
        str: Emoji representing the job status
    """
    if job_details.get("is_success"):
        return "✅"
    elif job_details.get("is_error"):
        return "❌"
    return "⚠️"


def send_system_notification(job_details: dict):
    """
    Send a notification using platform-specific notification system.
    Args:
        job_details (dict): The job details including name, status, duration, etc.
    """
    if not job_details:
        logger.error("No job details received for notification")
        return

    emoji = get_status_emoji(job_details)

    # Create notification title and message
    title = f"{emoji} dbt Job Status Update"
    message = f"Job: {job_details.get('name', 'Unknown')}\nStatus: {job_details.get('status', 'Unknown')}\nDuration: {job_details.get('duration', 'Unknown')}\nCompleted: {job_details.get('finished_at', 'Unknown')}"

    # Add error message if job failed
    if job_details.get("is_error"):
        message += (
            f"\nError: {job_details.get('error_message', 'No error message available')}"
        )

    try:
        if sys.platform == "darwin":
            Notifier.notify(
                message,
                title=title,
                sound="default",
                timeout=10,
            )
        elif sys.platform == "win32":
            toaster.show_toast(
                title,
                message,
                duration=10,
                threaded=True,
            )
        else:
            logger.debug("System notifications are not supported on this platform")
            return

        logger.debug("System notification sent successfully")
    except Exception as e:
        logger.error(f"Failed to send system notification: {e}")
