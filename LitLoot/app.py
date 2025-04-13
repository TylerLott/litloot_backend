import logging
import sys
from typing import Any, Dict
from flask import Flask, render_template, request, Response, send_from_directory
from flask_cors import CORS
from routes.chat import chat_bp
from routes.quiz import quiz_bp
from config import DEBUG
import os
import secrets

# Configure logging when app is imported
log_level: int = logging.DEBUG if DEBUG else logging.INFO
print(f"Debug mode is {'enabled' if DEBUG else 'disabled'}")

# Remove any existing handlers
root_logger: logging.Logger = logging.getLogger()
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Configure root logger
root_logger.setLevel(log_level)

# Create console handler
console_handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(log_level)

# Create formatter
formatter: logging.Formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add handler to root logger
root_logger.addHandler(console_handler)

# Test logging
logging.debug("This is a debug message")
logging.info("This is an info message")

# Get the absolute path to the LitLoot directory
base_dir: str = os.path.dirname(os.path.abspath(__file__))

# Create static directory if it doesn't exist
static_dir = os.path.join(base_dir, 'static')
os.makedirs(static_dir, exist_ok=True)

app: Flask = Flask(__name__,
    template_folder=os.path.join(base_dir, 'templates'),
    static_folder=static_dir
)

# Set a secret key for session management
app.secret_key = secrets.token_hex(32)

# Enable CORS with more permissive settings
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

app.register_blueprint(chat_bp)
app.register_blueprint(quiz_bp)

@app.route("/", methods=["GET"])
def index() -> str:
    logging.debug("Index route accessed")
    return render_template("index.html")

@app.route('/static/<path:filename>')
def serve_static(filename: str) -> Response:
    try:
        logging.debug(f"Serving static file: {filename}")
        return send_from_directory(app.static_folder, filename)
    except Exception as e:
        logging.error(f"Error serving static file {filename}: {str(e)}")
        return Response("File not found", status=404)

@app.after_request
def after_request(response: Response) -> Response:
    """Add CORS headers to all responses."""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5001)
