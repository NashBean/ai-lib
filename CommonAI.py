# CommonAI.py - Shared library for TrinityAI projects
#Monitoring (RAM, CPU, disk, net from earlier code).
#Research/self-learn (Wikipedia/GitHub API functions).
#Version control (your MAJOR/MINOR/FIX variables as functions).
#Logging/alerting (email on limits).
#Data load/save utils (for ./data/json).

import logging
import json
import os
import psutil
import requests
import time
import subprocess
import sys
import smtplib
from email.mime.text import MIMEText

# Version
MAJOR_VERSION = 0
MINOR_VERSION = 1
FIX_VERSION = 4
VERSION_STRING = f"v{MAJOR_VERSION}.{MINOR_VERSION}.{FIX_VERSION}"

DATA_DIR = "data"
DATA_PATH = "data/data.json"

logger = logging.getLogger("ai-lib")

# Version helper
def get_version(major, minor, fix):
    return f"v{major}.{minor}.{fix}"

def setup_logging(log_file="ai.log"):
    handlers = []
    if os.path.exists(log_file):
        handlers.append(logging.FileHandler(log_file))
    handlers.append(logging.StreamHandler())
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=handlers)

def load_config(config_file="config.json"):
    try:
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Config load error: {e}")
    default = {
        "RESEARCH_ENABLED": False,
        "DATA_MAX_SIZE_MB": 100,
        "RAM_LIMIT_GB": 4,
        "CPU_LIMIT_PERCENT": 80,
        "DISK_MIN_FREE_GB": 5,
        "NET_BANDWIDTH_THRESHOLD_MBPS": 1.0,
        "NET_LATENCY_MAX_MS": 200
    }
#        "ALERT_EMAIL": "your_email@example.com",
#       "SMTP_SERVER": "smtp.example.com",
#        "SMTP_PORT": 587,
#        "SMTP_USER": "user",
#        "SMTP_PASS": "pass",
#        "RESEARCH_SCHEDULE": "daily",
#        "GITHUB_REPO": "NashBean/AbrahamAI",
#        "GITHUB_TOKEN": "your_github_pat_here"

    return default

# System monitoring
def check_system_limits(config):
    try:
        if psutil.virtual_memory().used / (1024 ** 3) > config["RAM_LIMIT_GB"]:
            logger.warning("RAM limit exceeded")
            return False
        if psutil.cpu_percent(interval=1) > config["CPU_LIMIT_PERCENT"]:
            logger.warning("CPU limit exceeded")
            return False
        disk = psutil.disk_usage('/')
        if disk.free / (1024 ** 3) < config["DISK_MIN_FREE_GB"]:
            logger.warning("Disk space low")
            return False
        net_start = psutil.net_io_counters()
        time.sleep(1)
        net_end = psutil.net_io_counters()
        bandwidth_mbps = ((net_end.bytes_sent + net_end.bytes_recv - net_start.bytes_sent - net_start.bytes_recv) / 1024 / 1024) * 8
        if bandwidth_mbps < config["NET_BANDWIDTH_THRESHOLD_MBPS"]:
            logger.warning("Bandwidth low")
            return False
        return True
    except Exception as e:
        logger.error(f"System check error: {e}")
        return False

def self_research(topic):
    if not CONFIG["RESEARCH_ENABLED"]:
        return "Research disabled."
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&exintro=&titles={topic.replace(' ', '_')}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        pages = data["query"]["pages"]
        page_id = list(pages.keys())[0]
        if page_id != "-1":
            return pages[page_id]["extract"]
        return "No info."
    except Exception as e:
        logger.error(f"Research error: {e}")
        return "Research failed."

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

def get_response(ai_data, query):
    q = query.lower()
    if "parable" in q:
        parable = q.split("parable of")[1].strip() if "of" in q else "sower"
        p = ai_data["PARABLES"].get(parable, {})
        return f"Parable of {parable.capitalize()}\nReferences: {p.get('references', '')}\nVerses: {p.get('verses', '')}"
    # Add OT fulfillment for JesusAI
    if "fulfill" in q or "prophecy" in q:
        return ai_data.get("OT_FULFILLMENT", "No info")
    # Shared keyword logic
    return ai_data["RESPONSES"].get(q, ai_data["RESPONSES"]["default"])

def understand_language(language, text):
    # Simple placeholder - expand with NLTK or web research
    if language == "hebrew":
        return f"Hebrew text: {text} - Meaning: [research]"
    return text

def get_culture(ai_data, query):
    return ai_data["CULTURE"].get(query, "No info")