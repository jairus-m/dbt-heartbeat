import sys
import logging
import argparse

from utils.api import DbtCloudApi, JobMonitor
from utils.notifications import send_system_notification
from utils.config import validate_environment_vars, load_env_vars
from utils.display import print_job_status, print_missing_env_vars
from utils.version import check_version, get_current_version

dbt_api = DbtCloudApi()
job_monitor = JobMonitor(dbt_api)

__version__ = get_current_version()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    """
    Main function to handle command line arguments and start polling.
    """
    # Create a basic parser just for log level
    log_parser = argparse.ArgumentParser(add_help=False)
    log_parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)",
    )

    # Parse just the log level argument
    log_args, _ = log_parser.parse_known_args()

    # Setup logging with the specified level
    log_level = getattr(logging, log_args.log_level.upper())
    logging.getLogger().setLevel(log_level)
    for logger_name in [
        "dbt_heartbeat",
        "utils.api.dbt_cloud_api",
        "utils.notifications",
        "utils.version",
        "utils.api.job_monitor",
        "utils.config.env",
    ]:
        logging.getLogger(logger_name).setLevel(log_level)

    # Load environment variables
    load_env_vars()

    # Check for version flag
    if "--version" in sys.argv:
        check_version()
        # Let argparse handle the version display and exit
        sys.argv.remove("--version")
        sys.argv.append("--version")

    # Create the main parser
    parser = argparse.ArgumentParser(
        description="Poll dbt Cloud job statuses for specific runs.\n"
        "\nRequires environment variables DBT_CLOUD_API_KEY and DBT_CLOUD_ACCOUNT_ID to be set.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("job_run_id", nargs="?", help="The ID of the dbt Cloud job run")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=30,
        help="Time in seconds between polls (default: 30)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version number",
    )

    args = parser.parse_args()

    # If no job_run_id is provided, show help
    if args.job_run_id is None:
        parser.print_help()
        sys.exit(1)

    # Validate environment variables
    required_vars = ["DBT_CLOUD_API_KEY", "DBT_CLOUD_ACCOUNT_ID"]
    missing_vars = validate_environment_vars(required_vars)
    if missing_vars:
        logger.error(f"Missing environment variables: {missing_vars}")
        print_missing_env_vars(missing_vars)
        sys.exit(1)

    # Monitor the job
    job_run_data = job_monitor.monitor_job(args.job_run_id, args.poll_interval)

    # Get job details using the job ID from the run data
    job_id = job_run_data.get("job_id")
    if not job_id:
        logger.error("No job ID found in run data")
        sys.exit(1)

    # Get the formatted job run info which has all the humanized fields
    job_run_info = dbt_api.get_job_run_info(args.job_run_id)
    if not job_run_info:
        logger.error("Failed to get job run info")
        sys.exit(1)

    # Get status from the job run info
    status = job_run_info.get("status", "Unknown")
    logger.debug(f"Job completed with final status: {status}")
    print_job_status(status)

    # Send system notification with job run info
    logger.debug("Attempting to send system notification...")
    send_system_notification(job_run_info)

    sys.exit(0)


if __name__ == "__main__":
    main()
