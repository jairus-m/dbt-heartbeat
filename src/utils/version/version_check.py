import logging
import requests
from importlib.metadata import version, PackageNotFoundError
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()


def get_current_version() -> str:
    """
    Get the current installed version of dbt-heartbeat.
    Returns:
        str: Current version or 'unknown' if not found
    """
    try:
        return version("dbt-heartbeat")
    except PackageNotFoundError:
        return "unknown"


def get_latest_version() -> str:
    """
    Get the latest version of dbt-heartbeat from PyPI.
    Returns:
        str: Latest version or 'unknown' if not found
    """
    logger.debug("Attempting to fetch latest version from PyPI...")
    try:
        response = requests.get("https://pypi.org/pypi/dbt-heartbeat/json", timeout=5)
        response.raise_for_status()
        version = response.json()["info"]["version"]
        logger.debug(f"Successfully fetched latest version: {version}")
        return version
    except (requests.RequestException, KeyError, ValueError) as e:
        logger.debug(f"Failed to fetch latest version from PyPI: {e}")
        return "unknown"


def check_version() -> None:
    """
    Check if the current version is up to date and print a message if not.
    """
    logger.debug("Starting version check...")
    current = get_current_version()
    latest = get_latest_version()

    logger.debug(f"Current version: {current}, Latest version: {latest}")

    if current == "unknown" or latest == "unknown":
        logger.debug("Skipping version check due to unknown version(s)")
        return

    if current != latest:
        logger.debug("New version available, showing update message")
        console.print(
            f"\n[yellow]A new version of dbt-heartbeat is available: {latest}[/yellow]"
            f"\n[yellow]You are currently using version: {current}[/yellow]"
        )
    else:
        logger.debug("Version is up to date")
