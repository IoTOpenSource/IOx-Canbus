from flask import Flask, jsonify, render_template
from Canbus_data import fetch_canbus_data
import threading
import time
import json
import logging
import os
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# Global variable to store the latest data
latest_data = {}

# Environment variables for logging
DEBUG_VERBOSE = int(os.getenv('DEBUG_VERBOSE', 0))
CAF_APP_LOG_DIR = os.getenv("CAF_APP_LOG_DIR", "/tmp")

def setup_logger():
    log_file_path = os.path.join(CAF_APP_LOG_DIR, "iox-vehicle-obd2.log")
    logger = logging.getLogger(__name__)
    if DEBUG_VERBOSE == 0:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(log_file_path, maxBytes=5000000, backupCount=1)
    log_format = logging.Formatter('[%(asctime)s]{%(pathname)s:%(lineno)d}%(levelname)s- %(message)s')
    handler.setFormatter(log_format)
    logger.addHandler(handler)
    return logger

logger = setup_logger()

def fetch_data_periodically():
    global latest_data
    while True:
        latest_data = fetch_canbus_data()
        logger.info(json.dumps(latest_data))
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    global latest_data
    return jsonify(latest_data)

if __name__ == "__main__":
    # Start the data fetching thread
    data_thread = threading.Thread(target=fetch_data_periodically)
    data_thread.daemon = True
    data_thread.start()
    # Run the Flask app
    app.run(host='0.0.0.0', port=9001, debug=False)
