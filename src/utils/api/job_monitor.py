import time
import logging
import requests
from rich.console import Console

from utils.api import DbtCloudApi
from utils.display import (
    print_polling_start,
    print_initial_job_info,
    print_current_status,
    print_job_details,
)

logger = logging.getLogger(__name__)
console = Console()


class JobMonitor:
    """
    A class to monitor dbt Cloud job runs.

    This class handles the polling logic for monitoring job runs, including
    displaying initial job information, status updates, and final results.
    Attributes:
        api (DbtCloudApi): Instance of DbtCloudApi for making API calls
    Methods:
        monitor_job(job_run_id: str, poll_interval: int = 30) -> dict:
            Monitor a dbt Cloud job run until completion.
    """

    def __init__(self, api: DbtCloudApi = None):
        """
        Initialize the JobMonitor with an optional DbtCloudApi instance.
        Args:
            api (DbtCloudApi, optional): Instance of DbtCloudApi. If not provided,
                                        a new instance will be created.
        """
        self.api = api or DbtCloudApi()

    def monitor_job(self, job_run_id: str, poll_interval: int = 30) -> dict:
        """
        Monitor a dbt Cloud job run until completion.
        Args:
            job_run_id (str): The ID of the dbt Cloud job run
            poll_interval (int): Time in seconds between polls
        Returns:
            dict: The final job data
        Raises:
            requests.exceptions.RequestException: If there are API communication errors
        """
        print_polling_start(job_run_id, poll_interval)

        # Print job info and execution steps at the start
        try:
            job_data = self.api.get_job_run_info(job_run_id)
            print_initial_job_info(job_data)
        except Exception as e:
            logger.error(f"Failed to fetch initial job details: {e}")

        while True:
            try:
                logger.debug("Fetching job status...")
                job_data = self.api.get_job_run_info(job_run_id)

                # Print current status
                print_current_status(job_data)

                # Check if job is complete
                if not job_data.get("in_progress"):
                    logger.debug("Job is no longer in progress")
                    print_job_details(job_data)
                    return job_data

                logger.debug(
                    f"Job still in progress, waiting {poll_interval} seconds before next poll"
                )
                time.sleep(poll_interval)

            except requests.exceptions.RequestException as e:
                logger.error(f"Error polling job status: {e}", exc_info=True)
                console.print(f"[red]Error polling job status: {e}[/red]")
                time.sleep(poll_interval)
