"""Utility functions for UFC scraper project."""

import os
import json
import logging
import traceback
from typing import Tuple
import requests


def basic_request(url: str, logger: logging.Logger, timeout: int = 30) -> str:
    """
    Make a basic HTTP GET request and return the HTML content.

    Args:
        url: The URL to fetch
        logger: Logger instance for logging
        timeout: Request timeout in seconds

    Returns:
        HTML content as string

    Raises:
        RuntimeError: If the request fails
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        logger.debug('Successfully fetched URL: %s', url)
        return response.text
    except requests.RequestException as e:
        logger.error('Request failed for URL %s: %s', url, format_error(e))
        raise RuntimeError(f'Failed to fetch {url}') from e


def setup_basic_file_paths(project_name: str) -> Tuple[str, str, str, str, str]:
    """
    Set up basic file paths for the project.

    Creates necessary directories if they don't exist.

    Args:
        project_name: Name of the project

    Returns:
        Tuple of (project_dir, data_folder, logs_folder, output_folder, log_file_path)
    """
    # Get the current directory as project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))

    # Create subdirectories
    data_folder = os.path.join(project_dir, 'data')
    logs_folder = os.path.join(project_dir, 'logs')
    output_folder = os.path.join(project_dir, 'output')

    # Create directories if they don't exist
    for folder in [data_folder, logs_folder, output_folder]:
        os.makedirs(folder, exist_ok=True)

    # Create log file path
    log_file_path = os.path.join(logs_folder, f'{project_name}.log')

    return project_dir, data_folder, logs_folder, output_folder, log_file_path


def setup_logger(log_file_path: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up and configure a logger.

    Args:
        log_file_path: Path to the log file
        level: Logging level (default: logging.INFO)

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('ufc_scraper')
    logger.setLevel(level)

    # Clear any existing handlers
    logger.handlers.clear()

    # Create file handler
    file_handler = logging.FileHandler(log_file_path, mode='a')
    file_handler.setLevel(level)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Add formatter to handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def save_ndjson(data: dict, file_path: str) -> None:
    """
    Save a dictionary as a newline-delimited JSON (NDJSON) file.

    Appends the data as a new line to the file.

    Args:
        data: Dictionary to save
        file_path: Path to the NDJSON file
    """
    with open(file_path, 'a', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
        f.write('\n')


def format_error(exception: Exception) -> str:
    """
    Format an exception with its traceback for logging.

    Args:
        exception: The exception to format

    Returns:
        Formatted error string with traceback
    """
    return f'{type(exception).__name__}: {str(exception)}\n{"".join(traceback.format_tb(exception.__traceback__))}'
