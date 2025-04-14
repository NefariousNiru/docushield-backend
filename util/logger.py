import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# Get the base directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ensure logs directory exists
logs_dir = os.path.join(base_dir, 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Custom log filename format
def get_log_file_name():
    return os.path.join(logs_dir, f"app_{datetime.now().strftime('%Y-%m-%d')}.log")

# Rotating file handler with dynamic file names
class CustomRotatingFileHandler(RotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def doRollover(self):
        self.baseFilename = get_log_file_name()  # Update the filename dynamically
        super().doRollover()

# Configure the custom handler
log_file = get_log_file_name()
handler = CustomRotatingFileHandler(
    log_file, maxBytes=1024 * 1024 * 5, backupCount=5  # 5MB per log file, keep 5 backups
)

# Set log formatting
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Configure the root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
