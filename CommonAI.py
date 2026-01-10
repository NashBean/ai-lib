# CommonAI.py - Shared library for TrinityAI projects
#Monitoring (RAM, CPU, disk, net from earlier code).
#Research/self-learn (Wikipedia/GitHub API functions).
#Version control (your MAJOR/MINOR/FIX variables as functions).
#Logging/alerting (email on limits).
#Data load/save utils (for ./data/json).

import psutil
import logging
import json
import os
import requests
import time
import subprocess
import sys
import smtplib
from email.mime.text import MIMEText

# Version
MAJOR_VERSION = 0
MINOR_VERSION = 1
FIX_VERSION = 1
VERSION_STRING = f"v{MAJOR_VERSION}.{MINOR_VERSION}.{FIX_VERSION}"

DATA_DIR = "data"
DATA_PATH = "data/data.json"

logger = logging.getLogger("CommonAI")

def setup_logging(log_file="ai.log"):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
    )

def load_config(config_file="config.json"):
    # Your load code from earlier

# System monitoring
def check_system_limits(config):
    # Your full RAM/CPU/disk/net code from earlier
    return True  # or False

def self_research(topic):
    # Your Wikipedia research code

def self_update(config):
    # Your GitHub pull/restart code

def send_alert(config, message):
    # Your email code

# Data utils

def load_data(filename):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        DATA_PATH = os.path.join(DATA_DIR, filename)
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Data load error: {e}")
    return {}

def update_data(new_data):
    data = load_data()
    data.update(new_data)
    try:
        with open(DATA_PATH, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Data update error: {e}")

# Version helper
def get_version(major, minor, fix):
    return f"v{major}.{minor}.{fix}"