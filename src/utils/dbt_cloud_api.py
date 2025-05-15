import os
import time
import logging
import requests
from datetime import datetime
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
    Get the status of a dbt Cloud job run.
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
    logger.debug(f"Raw API Response: {data}")
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

def get_run_artifacts(job_run_id: str) -> dict:
    """
    Get the artifacts of a dbt Cloud job run.
    Args:
        job_run_id (str): The ID of the dbt Cloud job run
    Returns:
        dict: The run artifacts data from dbt Cloud API endpoint (/v2/runs/{run_id}/artifacts)
    """
    url = f"https://cloud.getdbt.com/api/v2/accounts/{DBT_CLOUD_ACCOUNT_ID}/runs/{job_run_id}/artifacts/"
    headers = {
        "Authorization": f"Token {DBT_CLOUD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    logger.debug(f"Making API request to get run artifacts: {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    logger.debug(f"Run artifacts API Response: {data}")
    return data

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
    
    # Format the completion time in local time
    finished_at = data.get('finished_at')
    if finished_at:
        try:
            # Parse the UTC time and convert to local time
            utc_time = datetime.fromisoformat(finished_at.replace('Z', '+00:00'))
            local_time = utc_time.astimezone()
            finished_at = local_time.strftime('%I:%M %p')
        except Exception as e:
            logger.error(f"Failed to format completion time: {e}")
            finished_at = 'Unknown'
    else:
        finished_at = 'Unknown'
    
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
    table.add_row("Completed", finished_at)
    
    if data.get('is_error'):
        error_msg = data.get('status_message', 'No error message available')
        table.add_row("Error", error_msg)
    
    # Print the table in a panel
    console.print(Panel(table, title="dbt Cloud Job Status", border_style="blue"))
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
    console.print(f"[bold green]Starting to poll job run {job_run_id}[/bold green]")
    
    # Print job info and execution steps at the start
    try:
        job_data = get_job_status(job_run_id)
        data = job_data.get('data', {})
        job_id = data.get('job_id')
        job_url = data.get('href')
        job_name = 'Unknown'
        
        if job_id:
            job_details = get_job_details(job_id)
            job_name = job_details.get('name', 'Unknown')
            
            # Print job info
            if job_url:
                console.print(f"\n[blue]Job Name: {job_name}[/blue]")
                console.print(f"[blue]Job URL: {job_url}[/blue]")
            
            # Print execution steps
            if job_details and 'execute_steps' in job_details:
                execution_steps = job_details['execute_steps']
                console.print("\n[bold cyan]Execution Steps:[/bold cyan]")
                for i, step in enumerate(execution_steps, 1):
                    console.print(f"[cyan]{i}. {step}[/cyan]")
                console.print("")  # Add a blank line for spacing
    except Exception as e:
        logger.error(f"Failed to fetch initial job details: {e}")
    
    while True:
        try:
            logger.debug("Fetching job status...")
            job_data = get_job_status(job_run_id)
            data = job_data.get('data', {})
            
            logger.debug(f"Full job data: {data}")
            
            status = data.get('status_humanized', 'Unknown')
            duration = data.get('duration_humanized', 'Unknown')
            in_progress = data.get('in_progress', False)
            
            # Get current step from run_steps in the main response
            run_steps = data.get('run_steps', [])
            current_step_index = None
            total_steps = len(run_steps)
            
            if run_steps:
                # Find the current step (status 1) or next queued step (status 0)
                for i, step in enumerate(run_steps):
                    if step.get('status') == 1:  # Running
                        current_step_index = i
                        logger.debug(f"Found running step at index {i}")
                        break
                    elif step.get('status') == 0:  # Queued
                        current_step_index = i
                        logger.debug(f"Found queued step at index {i}")
                        break
            
            # Print step progress if we have run steps
            if run_steps and current_step_index is not None:
                step_name = run_steps[current_step_index].get('name', 'Unknown step')
                step_status = "Running" if run_steps[current_step_index].get('status') == 1 else "Queued"
                console.print(f"[yellow]Step {current_step_index + 1} of {total_steps}: {step_status} - {step_name}[/yellow]")
            
            # Always print current status
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
                logger.debug("Job is no longer in progress")
                print_job_status(job_data)
                return job_data
            
            logger.debug(f"Job still in progress, waiting {poll_interval} seconds before next poll")
            time.sleep(poll_interval)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error polling job status: {e}", exc_info=True)
            console.print(f"[red]Error polling job status: {e}[/red]")
            time.sleep(poll_interval)