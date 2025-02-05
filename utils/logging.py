import logging
import os

# Define log directory
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "app.log")),  # Logs to a file
        logging.StreamHandler(),  # Logs to the console
    ],
)

# Get a logger instance
logger = logging.getLogger(__name__)
