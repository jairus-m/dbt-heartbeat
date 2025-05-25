import logging
import sys

logger = logging.getLogger(__name__)

# Only import pync on macOS
if sys.platform == "darwin":
    from pync import Notifier
else:
    Notifier = None


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
    Send a notification using pync.
    Args:
        job_details (dict): The job details including name, status, duration, etc.
    """
    if not job_details:
        logger.error("No job details received for notification")
        return

    if sys.platform != "darwin":
        logger.debug("System notifications are only supported on macOS")
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
        Notifier.notify(
            message,
            title=title,
            sound="default",
            timeout=10,
        )
        logger.debug("System notification sent successfully")
    except Exception as e:
        logger.error(f"Failed to send system notification: {e}")
