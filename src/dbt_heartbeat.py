import os
import sys
import logging
import argparse
from dotenv import load_dotenv
from rich.console import Console

from utils.dbt_cloud_api import poll_job
from utils.os_notifs import send_system_notification

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
logger.debug("Environment variables loaded")

# Initialize Rich console for pretty terminal output
console = Console()

# Configuration
DBT_CLOUD_API_KEY = os.getenv('DBT_CLOUD_API_KEY')
DBT_CLOUD_ACCOUNT_ID = os.getenv('DBT_CLOUD_ACCOUNT_ID')
logger.debug(f"Using dbt Cloud Account ID: {DBT_CLOUD_ACCOUNT_ID}")

def main():
    """
    Main function to handle command line arguments and start polling.
    """
    parser = argparse.ArgumentParser(description='Poll dbt Cloud job status')
    parser.add_argument('job_run_id', help='The ID of the dbt Cloud job run')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                      help='Set the logging level (default: INFO)')
    parser.add_argument('--poll-interval', type=int, default=30,
                      help='Time in seconds between polls (default: 30)')
    
    args = parser.parse_args()
    
    # Setup logging with the specified level for all loggers
    log_level = getattr(logging, args.log_level.upper())
    logging.getLogger().setLevel(log_level)
    for logger_name in ['dbt_heartbeat', 'utils.dbt_cloud_api', 'utils.os_notifs']:
        logging.getLogger(logger_name).setLevel(log_level)
    
    # Validate environment variables
    required_vars = ['DBT_CLOUD_API_KEY', 'DBT_CLOUD_ACCOUNT_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing environment variables: {missing_vars}")
        console.print(f"[red]Missing required environment variables: {', '.join(missing_vars)}[/red]")
        console.print("\n[red]Add them to a .env file:[/red]")
        for var in missing_vars:
            console.print(f"[red]{var}=your_{var.lower()}[/red]")
        console.print("\n[red]Or export them directly in your terminal:[/red]")
        for var in missing_vars:
            console.print(f"[red]export {var}=your_{var.lower()}[/red]")
        sys.exit(1)
    logger.debug("Environment variables validated")
    final_status = poll_job(args.job_run_id, args.poll_interval)
    
    # Get status from the correct location in the response
    status = final_status.get('data', {}).get('status_humanized', 'Unknown')
    logger.debug(f"Job completed with final status: {status}")
    console.print(f"[bold green]Job completed with status: {status}[/bold green]")
    
    # Send system notification
    logger.debug("Attempting to send system notification...")
    send_system_notification(final_status)

if __name__ == "__main__":
    main() 