import logging
import sys

def setup_logging():
    """Configures the root logger for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
        stream=sys.stdout,
    )