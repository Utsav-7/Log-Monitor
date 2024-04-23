import logging
import time
import random
from constants import AVAILABLE_API_PATH

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set the root logger level to DEBUG

# Create a logger
logger = logging.getLogger(__name__)

# getting all possible api path of application
api_paths = AVAILABLE_API_PATH

# Define log message formats
formats = {
    logging.INFO: "INFO message",
    logging.DEBUG: "DEBUG message",
    logging.ERROR: "ERROR message",
}

# Define log levels to cycle through
log_levels = [logging.INFO, logging.DEBUG, logging.ERROR]

# Main loop to log messages
while True:
    try:
        # Randomly select a log level and, path
        log_level = random.choice(log_levels)

        path = random.choice(api_paths)
        
        # Get the log message format for the selected log level
        log_message = formats[log_level] + f" for {path}"
        
        # Log the message
        logger.log(log_level, log_message)

        time.sleep(1)

    except KeyboardInterrupt:
        
        # Handle keyboard interrupt (Ctrl+C)
        print("\nLogging interrupted. Exiting.")
        break
    
    except Exception as e:
        warnings.warn(f"Error occurred: {e}")