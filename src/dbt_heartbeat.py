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
    
    # Setup logging with the specified level
    logger.setLevel(getattr(logging, args.log_level.upper()))
    
    # Validate environment variables
    required_vars = ['DBT_CLOUD_API_KEY', 'DBT_CLOUD_ACCOUNT_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing environment variables: {missing_vars}")
        console.print(f"[red]Missing required environment variables: {', '.join(missing_vars)}[/red]")
        sys.exit(1)
    
    logger.debug("Environment variables validated")
    final_status = poll_job(args.job_run_id, args.poll_interval)
    
    # Get status from the correct location in the response
    status = final_status.get('data', {}).get('status_humanized', 'Unknown')
    logger.info(f"Job completed with final status: {status}")
    console.print(f"[bold]Job completed with status: {status}[/bold]")
    
    # Send system notification
    logger.info("Attempting to send system notification...")
    send_system_notification(final_status)

if __name__ == "__main__":
    main() 