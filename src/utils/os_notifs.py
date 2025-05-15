import logging
from datetime import datetime
from pync import Notifier
from .dbt_cloud_api import get_job_details

# Configure logging
logger = logging.getLogger(__name__)

def send_system_notification(job_data: dict):
    """
    Send a notification using pync.
    Args:
        job_data (dict): The job data from dbt Cloud API endpoint (/v2/jobs/run/{run_id})
    Returns:
        None
    """
    if not job_data:
        logger.error("No job data received for notification")
        return
        
    data = job_data.get('data', {})
    if not data:
        logger.error("No data field in job response for notification")
        return
    
    # Get job details if we have a job_id
    job_id = data.get('job_id')
    job_name = 'Unknown'
    if job_id:
        try:
            job_details = get_job_details(job_id)
            job_name = job_details.get('name', 'Unknown')
        except Exception as e:
            logger.error(f"Failed to fetch job details for notification: {e}")
    
    status = data.get('status_humanized', 'Unknown')
    duration = data.get('duration_humanized', 'Unknown')
    
    # Format the end time in local time
    finished_at = data.get('finished_at')
    if finished_at:
        try:
            # Parse the UTC time and convert to local time
            utc_time = datetime.fromisoformat(finished_at.replace('Z', '+00:00'))
            local_time = utc_time.astimezone()
            finished_at = local_time.strftime('%I:%M %p')
        except Exception as e:
            logger.error(f"Failed to format end time: {e}")
            finished_at = 'Unknown'
    else:
        finished_at = 'Unknown'
    
    # Determine emoji based on status xD cause it's cute
    if data.get('is_success'):
        emoji = "✅"
    elif data.get('is_error'):
        emoji = "❌"
    else:
        emoji = "⚠️"
    
    # Create notification title and message
    title = f"{emoji} dbt Job Status Update"
    message = f"Job: {job_name}\nStatus: {status}\nDuration: {duration}\nCompleted: {finished_at}"
    
    # Add error message if job failed
    if data.get('is_error'):
        error_msg = data.get('status_message', 'No error message available')
        message += f"\nError: {error_msg}"
    
    try:
        Notifier.notify(
            message,
            title=title,
            sound='default', 
            timeout=10  # Notification will stay for 10 seconds
        )
        logger.debug("System notification sent successfully")
    except Exception as e:
        logger.error(f"Failed to send system notification: {e}") 