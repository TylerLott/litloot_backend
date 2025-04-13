import os
import sys
import logging
from app import app
from config import DEBUG

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
log_level = logging.DEBUG if DEBUG else logging.INFO
print(f"Debug mode is {'enabled' if DEBUG else 'disabled'}")

# Configure root logger
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True  # This will override any existing configuration
)

# Test logging
logging.debug("This is a debug message")
logging.info("This is an info message")

if __name__ == '__main__':
    # Run the app
    app.run(debug=DEBUG, use_reloader=False, host='127.0.0.1', port=5001)  # Disable reloader to prevent duplicate logs 