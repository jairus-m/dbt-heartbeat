import os
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class DbtCloudApi:
    """
    A class to interact with the dbt Cloud API.

    This class provides methods to fetch job statuses and run details from dbt Cloud.
    It requires DBT_CLOUD_API_KEY and DBT_CLOUD_ACCOUNT_ID environment variables to be set.

    Attributes:
        api_key (str): The dbt Cloud API key from environment variable DBT_CLOUD_API_KEY
        account_id (str): The dbt Cloud account ID from environment variable DBT_CLOUD_ACCOUNT_ID
        base_url (str): The base URL for the dbt Cloud API (https://cloud.getdbt.com/api/v2)
        headers (dict): Request headers containing authorization token and content type
    Methods:
        get_run_details(run_id: str) -> dict:
            Get details about a specific run from the dbt Cloud API
        get_job_details(job_id: str) -> dict:
            Get details about a specific job from the dbt Cloud API
        get_job_run_info(run_id: str) -> dict:
            Get formatted job run info with humanized duration fields
    """

    def __init__(self):
        self.api_key = os.getenv("DBT_CLOUD_API_KEY")
        self.account_id = os.getenv("DBT_CLOUD_ACCOUNT_ID")
        self.base_url = "https://cloud.getdbt.com/api/v2"
        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }

    def get_run_details(self, run_id: str) -> dict:
        """
        Get details about a specific run from the dbt Cloud API.
        Args:
            run_id (str): The ID of the run
        Returns:
            dict: Raw run data from the API
        """
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/runs/{run_id}/"
            logger.debug(f"Making API request to: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            try:
                json_data = response.json()
                if not json_data:
                    logger.error("Empty response from API")
                    return {}

                data = json_data.get("data", {})
                if not data:
                    logger.error("No data field in run response")
                    return {}

                return data
            except ValueError as e:
                logger.error(f"Invalid JSON response: {e}")
                return {}

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {}

    def get_job_details(self, job_id: str) -> dict:
        """
        Get details about a specific job from the dbt Cloud API.
        Args:
            job_id (str): The ID of the job
        Returns:
            dict: Raw job data from the API
        """
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/jobs/{job_id}/"
            logger.debug(f"Making API request to: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            try:
                json_data = response.json()
                if not json_data:
                    logger.error("Empty response from API")
                    return {}

                data = json_data.get("data", {})
                if not data:
                    logger.error("No data field in job response")
                    return {}

                return data
            except ValueError as e:
                logger.error(f"Invalid JSON response: {e}")
                return {}

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {}

    def get_job_run_info(self, run_id: str) -> dict:
        """
        Get comprehensive information about a dbt Cloud job run by combining run and job details.
        Args:
            run_id (str): The ID of the run
        Returns:
            dict: Formatted job information including name, status, duration, and completion time
        """
        try:
            # Get run details
            run_data = self.get_run_details(run_id)
            if not run_data:
                logger.error("No run data found")
                return {}

            logger.debug(f"Run data received: {run_data}")
            logger.debug(f"Run steps from run data: {run_data.get('run_steps', [])}")

            # Get job details if we have a job_id
            job_data = {}
            job_id = run_data.get("job_id")  # Get job_id directly from run data
            if job_id:
                job_data = self.get_job_details(job_id)
                if not job_data:
                    logger.debug(f"Could not fetch job details for job_id: {job_id}")
                else:
                    logger.debug(f"Job data received: {job_data}")
                    logger.debug(
                        f"Execute steps from job data: {job_data.get('execute_steps', [])}"
                    )
            else:
                logger.debug("No job ID found in run data, using run data only")

            # Format the end time in local time
            finished_at = run_data.get("finished_at")
            if finished_at:
                try:
                    utc_time = datetime.fromisoformat(
                        finished_at.replace("Z", "+00:00")
                    )
                    local_time = utc_time.astimezone()
                    finished_at = local_time.strftime("%I:%M %p")
                except Exception as e:
                    logger.error(f"Failed to format end time: {e}")
                    finished_at = "Unknown"
            else:
                finished_at = "Unknown"

            # Get run duration and queued duration
            run_duration = run_data.get("run_duration_humanized", "Unknown")
            queued_duration = run_data.get("queued_duration_humanized", "Unknown")

            # Build the response dictionary with safe gets
            response = {
                "name": job_data.get(
                    "name", "Unknown"
                ),  # We'll get the name from job details if available
                "status": run_data.get("status_humanized", "Unknown"),
                "duration": run_data.get("duration_humanized", "Unknown"),
                "run_duration": run_duration,
                "queued_duration": queued_duration,
                "finished_at": finished_at,
                "is_success": run_data.get("is_success", False),
                "is_error": run_data.get("is_error", False),
                "error_message": run_data.get(
                    "status_message", "No error message available"
                ),
                "run_id": run_data.get("id"),
                "job_id": job_id,
                "href": run_data.get("href"),
                "run_steps": job_data.get(
                    "execute_steps", []
                ),  # Use execute_steps from job data
                "in_progress": run_data.get("in_progress", False),
            }

            logger.debug(f"Formatted response: {response}")
            logger.debug(f"Run steps in response: {response.get('run_steps', [])}")
            return response

        except Exception as e:
            logger.error(f"Error getting job run info: {str(e)}", exc_info=True)
            return {}
