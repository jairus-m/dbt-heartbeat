import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def load_env_vars() -> tuple[str | None, str | None]:
    """
    Load environment variables with proper precedence:
    1. Terminal session variables (from export or .zshrc)
    2. .env file variables (only if not found in environment)
    Returns:
        tuple[str | None, str | None]: Tuple of (api_key, account_id)
    """
    # Check for environment variables before loading .env
    api_key = os.getenv("DBT_CLOUD_API_KEY")
    account_id = os.getenv("DBT_CLOUD_ACCOUNT_ID")

    if api_key and account_id:
        logger.debug("Using environment variables from terminal session")
    else:
        # Load from .env file if variables aren't in environment
        logger.debug("Loading environment variables from .env file")
        load_dotenv(override=False)  # Don't override existing env vars
        api_key = os.getenv("DBT_CLOUD_API_KEY")
        account_id = os.getenv("DBT_CLOUD_ACCOUNT_ID")

    if account_id:
        logger.debug(f"Using dbt Cloud Account ID: {account_id}")

    return api_key, account_id


def validate_environment_vars(required_vars: list) -> list:
    """
    Validate that required environment variables are set.
    Args:
        required_vars (list): List of required environment variable names
    Returns:
        list: List of missing environment variable names
    """
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if not missing_vars:
        logger.debug("Environment variables validated")
    return missing_vars
