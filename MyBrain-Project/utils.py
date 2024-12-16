# utils.py

import logging
from pathlib import Path

def setup_logging(log_level: str, log_format: str, log_file: str, delete_existing: bool = False) -> None:
    """
    Sets up logging configuration for the application.
    
    Parameters:
        log_level (str): Logging level (e.g., "DEBUG", "INFO").
        log_format (str): Format string for log messages.
        log_file (str): File path to save log messages.
        delete_existing (bool, optional): Whether to delete the existing log file before setup. Defaults to False.
    """
    log_path = Path(log_file)
    if delete_existing and log_path.exists():
        log_path.unlink()
        logging.info(f"Deleted existing log file: {log_path}")
    logging.basicConfig(level=log_level, format=log_format, filename=log_file, filemode='a')
    logging.info("Logging setup complete.")