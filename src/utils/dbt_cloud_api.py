import os
import time
import logging
import requests
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from dotenv import load_dotenv


logger = logging.getLogger(__name__)
console = Console()

# Load environment variables
load_dotenv()

# Configuration
DBT_CLOUD_API_KEY = os.getenv('DBT_CLOUD_API_KEY')
DBT_CLOUD_ACCOUNT_ID = os.getenv('DBT_CLOUD_ACCOUNT_ID')

def get_job_status(job_run_id: str) -> dict:
    """
    Get the status of a DBT Cloud job run.
    Args:
        job_run_id (str): The ID of the dbt Cloud job run
    Returns:
        dict: The job data from dbt Cloud API endpoint (/v2/jobs/run/{run_id})
    """
    url = f"https://cloud.getdbt.com/api/v2/accounts/{DBT_CLOUD_ACCOUNT_ID}/runs/{job_run_id}/"
    headers = {
        "Authorization": f"Token {DBT_CLOUD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    logger.debug(f"Making API request to: {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    logger.debug(f"API Response: {data}")
    return data

def get_job_details(job_id: dict) -> dict:
    """
    Get the details of a dbt Cloud job.
    Args:
        job_id (str): The ID of the dbt Cloud job
    Returns:
        dict: The job data from dbt Cloud API endpoint (/v2/jobs/{job_id})
    """
    url = f"https://cloud.getdbt.com/api/v2/accounts/{DBT_CLOUD_ACCOUNT_ID}/jobs/{job_id}/"
    headers = {
        "Authorization": f"Token {DBT_CLOUD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    logger.debug(f"Making API request to get job details: {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    logger.debug(f"Job details API Response: {data}")
    return data.get('data', {})

def print_job_status(job_data: dict):
    """
    Print job status details to the terminal.
    Args:
        job_data (dict): The job data from dbt Cloud API endpoint (/v2/jobs/run/{run_id})
    Returns:
        None
    """
    logger.debug("Preparing to print job status")
    
    if not job_data:
        logger.error("No job data received")
        console.print("[red]Error: No job data received[/red]")
        return
        
    data = job_data.get('data', {})
    if not data:
        logger.error("No data field in job response")
        console.print("[red]Error: Invalid job data format[/red]")
        return
    
    # Get job details if we have a job_id
    job_id = data.get('job_id')
    job_name = 'Unknown'
    if job_id:
        try:
            job_details = get_job_details(job_id)
            job_name = job_details.get('name', 'Unknown')
        except Exception as e:
            logger.error(f"Failed to fetch job details: {e}")
    
    run_id = data.get('id', 'Unknown')
    
    logger.debug(f"Job details - Name: {job_name}, Run ID: {run_id}")
    
    # Create a table for the job details
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Job Name", job_name)
    table.add_row("Run ID", str(run_id))
    table.add_row("Status", data.get('status_humanized', 'Unknown'))
    table.add_row("Duration", data.get('duration_humanized', 'Unknown'))
    table.add_row("Run Duration", data.get('run_duration_humanized', 'Unknown'))
    table.add_row("Queued Duration", data.get('queued_duration_humanized', 'Unknown'))
    
    if data.get('is_error'):
        error_msg = data.get('status_message', 'No error message available')
        table.add_row("Error", error_msg)
    
    # Print the table in a panel
    console.print(Panel(table, title="DBT Cloud Job Status", border_style="blue"))
    logger.debug("Job status table printed")

def poll_job(job_run_id: str, poll_interval=30): 
    """
    Poll the dbt Cloud API until the job is completed 
    and prints the job status to the terminal.
    Args:
        job_run_id (str): The ID of the dbt Cloud job run
        poll_interval (int): Time in seconds between polls
    Returns:
        None
    """
    logger.info(f"Starting to poll job run {job_run_id} with interval {poll_interval}s")
    console.print(f"[bold blue]Starting to poll job run {job_run_id}[/bold blue]")
    
    while True:
        try:
            logger.debug("Fetching job status...")
            job_data = get_job_status(job_run_id)
            data = job_data.get('data', {})
            
            status = data.get('status_humanized', 'Unknown')
            duration = data.get('duration_humanized', 'Unknown')
            in_progress = data.get('in_progress', False)
            
            logger.debug(f"Current status: {status}, Duration: {duration}, In Progress: {in_progress}")
            
            # Print current status with color based on state
            if data.get('is_success'):
                logger.debug("Job is successful")
                console.print(f"[green]Current status: {status} (Duration: {duration})[/green]")
            elif data.get('is_error'):
                logger.debug("Job has error")
                console.print(f"[red]Current status: {status} (Duration: {duration})[/red]")
            elif in_progress:
                logger.debug("Job is in progress")
                console.print(f"[yellow]Current status: {status} (Duration: {duration})[/yellow]")
            else:
                logger.debug("Job status unknown")
                console.print(f"Current status: {status} (Duration: {duration})")
            
            # Check if job is complete
            if not in_progress:
                logger.info("Job is no longer in progress")
                print_job_status(job_data)
                return job_data
            
            logger.debug(f"Job still in progress, waiting {poll_interval} seconds before next poll")
            time.sleep(poll_interval)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error polling job status: {e}", exc_info=True)
            console.print(f"[red]Error polling job status: {e}[/red]")
            time.sleep(poll_interval)