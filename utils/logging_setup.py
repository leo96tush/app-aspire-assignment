import os
import logging
from logging.handlers import RotatingFileHandler


# Set up the log directory
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Log file path
log_file = os.path.join(log_dir, 'app.log')

# Configure logging settings
def setup_logger():
    # Create the logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set the default log level to DEBUG

    # Create a formatter that outputs log in a readable format
    formatter = logging.Formatter(
        '%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s'
    )

    # File handler with rotation: maximum log file size of 10MB, keep 3 backups
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=3)
    file_handler.setLevel(logging.INFO)  # Set the log level for the file handler (INFO logs and above)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Console will display all logs (DEBUG and above)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
