import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

logger = logging.getLogger(__name__)
console = Console()


def print_job_status(status: str):
    """
    Print job status with appropriate color based on the status.
    Args:
        status (str): The job status to print
    """
    if status == "Success":
        console.print(f"[bold green]Job completed with status: {status}[/bold green]")
    elif status == "Error":
        console.print(f"[bold red]Job completed with status: {status}[/bold red]")
    elif status == "Cancelled":
        console.print(f"[bold yellow]Job completed with status: {status}[/bold yellow]")
    else:
        console.print(f"[bold white]Job completed with status: {status}[/bold white]")


def print_missing_env_vars(missing_vars: list):
    """
    Print instructions for missing environment variables.
    Args:
        missing_vars (list): List of missing environment variable names
    """
    console.print(
        f"[red]Missing required environment variables: {', '.join(missing_vars)}[/red]"
    )
    console.print(
        "\n[red]Export them directly in your terminal (or shell configuration file):[/red]"
    )
    for var in missing_vars:
        console.print(f"[red]export {var}=your_{var.lower()}[/red]")
    console.print("\n[red]Or add them to a .env file:[/red]")
    for var in missing_vars:
        console.print(f"[red]{var}=your_{var.lower()}[/red]")


def print_job_details(job_data: dict):
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

    # Create a table for the job details
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Job Name", job_data.get("name", "Unknown"))
    table.add_row("Run ID", str(job_data.get("run_id", "Unknown")))
    table.add_row("Status", job_data.get("status", "Unknown"))
    table.add_row("Duration", job_data.get("duration", "Unknown"))
    table.add_row("Run Duration", job_data.get("run_duration", "Unknown"))
    table.add_row("Queued Duration", job_data.get("queued_duration", "Unknown"))
    table.add_row("Completed", job_data.get("finished_at", "Unknown"))

    if job_data.get("is_error"):
        error_msg = job_data.get("error_message", "No error message available")
        table.add_row("Error", error_msg)

    # Print the table in a panel
    console.print(Panel(table, title="dbt Cloud Job Status", border_style="blue"))
    logger.debug("Job status table printed")


def print_polling_start(job_run_id: str, poll_interval: int):
    """
    Print initial polling information.
    Args:
        job_run_id (str): The ID of the job run
        poll_interval (int): Time in seconds between polls
    """
    logger.info(f"Starting to poll job run {job_run_id} with interval {poll_interval}s")
    console.print(f"[bold green]Starting to poll job run {job_run_id}[/bold green]")


def print_initial_job_info(job_data: dict):
    """
    Print initial job information and execution steps.
    Args:
        job_data (dict): The job data containing initial information
    """
    try:
        logger.debug("Starting to print initial job info")
        if job_data.get("href"):
            logger.debug("Found job href, printing job name and URL")
            console.print(f"\n[blue]Job Name: {job_data.get('name', 'Unknown')}[/blue]")
            console.print(f"[blue]Job URL: {job_data.get('href')}[/blue]")

            # Print execution steps
            run_steps = job_data.get("run_steps", [])
            logger.debug(f"Found {len(run_steps)} run steps")
            if run_steps:
                console.print("\n[bold cyan]Execution Steps:[/bold cyan]")
                for i, step in enumerate(run_steps, 1):
                    logger.debug(f"Printing step {i}: {step}")
                    console.print(f"[cyan]{i}. {step}[/cyan]")
                console.print("")  # Add a blank line for spacing
            else:
                logger.debug("No run steps found in job data")
        else:
            logger.debug("No job href found in job data")
    except Exception as e:
        logger.error(f"Failed to print initial job details: {e}", exc_info=True)


def print_step_progress(run_steps: list, current_step_index: int, total_steps: int):
    """
    Print the current step progress.
    Args:
        run_steps (list): List of run steps
        current_step_index (int): Index of the current step
        total_steps (int): Total number of steps
    """
    if run_steps and current_step_index is not None:
        step_name = run_steps[current_step_index].get("name", "Unknown step")
        step_status = (
            "Running" if run_steps[current_step_index].get("status") == 1 else "Queued"
        )
        console.print(
            f"[yellow]Step {current_step_index + 1} of {total_steps}: {step_status} - {step_name}[/yellow]"
        )


def print_current_status(job_data: dict):
    """
    Print the current job status with appropriate color.
    Args:
        job_data (dict): The current job data
    """
    status = job_data.get("status", "Unknown")
    duration = job_data.get("duration", "Unknown")

    if job_data.get("is_success"):
        logger.debug("Job is successful")
        console.print(f"[green]Current status: {status} (Duration: {duration})[/green]")
    elif job_data.get("is_error"):
        logger.debug("Job has error")
        console.print(f"[red]Current status: {status} (Duration: {duration})[/red]")
    elif job_data.get("in_progress"):
        logger.debug("Job is in progress")
        console.print(
            f"[yellow]Current status: {status} (Duration: {duration})[/yellow]"
        )
    else:
        logger.debug("Job status unknown")
        console.print(f"Current status: {status} (Duration: {duration})")
