import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def load_environment():
    """
    Load environment variables from .env file.
    """
    load_dotenv()
    logger.debug("Environment variables loaded")


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
