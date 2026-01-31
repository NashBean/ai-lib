#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# common.py - Shared logic for all AIs
# ai_lib/common.py - Shared helpers for AbrahamAI/MosesAI/JesusAI (iBeanSoftware-inspired efficiency)

import datetime  # For logging timestamps

import requests
import psutil
import logging
import json
import os
import sys
import time
import sqlite3
import subprocess
import smtplib
from email.mime.text import MIMEText

# Version
MAJOR_VERSION = 0
MINOR_VERSION = 3
FIX_VERSION = 3
VERSION_STRING = f"v{MAJOR_VERSION}.{MINOR_VERSION}.{FIX_VERSION}"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ai.log"), logging.StreamHandler()]
)
logger = logging.getLogger("TrinityAI")

# System limits check (interweave all monitoring)
def check_system_limits(config):
    # RAM
    used_ram_gb = psutil.virtual_memory().used / (1024 ** 3)
    if used_ram_gb > config["RAM_LIMIT_GB"]:
        logger.warning(f"RAM usage high: {used_ram_gb:.2f}GB")
        return False

    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > config["CPU_LIMIT_PERCENT"]:
        logger.warning(f"CPU usage high: {cpu_percent}%")
        return False

    # Disk
    disk = psutil.disk_usage('/')
    free_gb = disk.free / (1024 ** 3)
    if free_gb < config["DISK_MIN_FREE_GB"]:
        logger.warning(f"Disk space low: {free_gb:.2f}GB")
        return False

    # Network (bandwidth approx, latency to Google DNS)
    net_start = psutil.net_io_counters()
    time.sleep(1)
    net_end = psutil.net_io_counters()
    bandwidth_mbps = ((net_end.bytes_sent + net_end.bytes_recv - net_start.bytes_sent - net_start.bytes_recv) / 1024 / 1024) * 8
    if bandwidth_mbps < config["NET_BANDWIDTH_THRESHOLD_MBPS"]:
        logger.warning(f"Bandwidth low: {bandwidth_mbps:.2f}Mbps")
        return False
    try:
        latency_output = subprocess.check_output(["ping", "-c", "1", "8.8.8.8"]).decode()
        latency_ms = float(latency_output.split("time=")[1].split(" ms")[0])
        if latency_ms > config["NET_LATENCY_MAX_MS"]:
            logger.warning(f"Latency high: {latency_ms}ms")
            return False
    except:
        logger.error("Network check failed")
        return False

    return True

# Send alert (email)
def send_alert(config, message):
    try:
        msg = MIMEText(message)
        msg["Subject"] = "TrinityAI Alert"
        msg["From"] = config["SMTP_USER"]
        msg["To"] = config["ALERT_EMAIL"]
        server = smtplib.SMTP(config["SMTP_SERVER"], config["SMTP_PORT"])
        server.starttls()
        server.login(config["SMTP_USER"], config["SMTP_PASS"])
        server.sendmail(config["SMTP_USER"], config["ALERT_EMAIL"], msg.as_string())
        server.quit()
        logger.info("Alert sent")
    except Exception as e:
        logger.error(f"Alert failed: {e}")

# Research (self-learn)
def self_research(topic):
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&exintro=&titles={topic.replace(' ', '_')}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        pages = data["query"]["pages"]
        page_id = list(pages.keys())[0]
        if page_id != "-1":
            return pages[page_id]["extract"]
        return "No info found."
    except Exception as e:
        logger.error(f"Research failed: {e}")
        return "Research failed"

# GitHub self-update
def self_update(config):
    try:
        owner, repo = config["GITHUB_REPO"].split("/")
        url = f"https://api.github.com/repos/{owner}/{repo}/commits/main"
        headers = {"Authorization": f"Bearer {config['GITHUB_TOKEN']}"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        head_sha = resp.json()["sha"]
        base_sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
        if base_sha != head_sha:
            subprocess.run(["git", "pull"], check=True)
            os.execv(sys.executable, [sys.executable] + sys.argv)
            return "Updated and restarted"
        return "Up to date"
    except Exception as e:
        logger.error(f"Update failed: {e}")
        return "Update failed"

# Scheduler for research/update (manual or timed)
def scheduler(config, ai_name):
    while True:
        if config["RESEARCH_SCHEDULE"] == "none":
            time.sleep(3600)
            continue
        interval = 86400 if config["RESEARCH_SCHEDULE"] == "daily" else 3600
        self_update(config)
        # Self-research example (add topics for AI to learn)
        topic = f"{ai_name} archaeology"
        research = self_research(topic)
        update_data({"new_research": research})
        time.sleep(interval)

def update_data(new_data):
    try:
        data = load_data()
        data.update(new_data)
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Update data error: {e}")

# Load data.json (parables, responses, etc.)
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Data load error: {e}")
        return {}

# Speak
def speak(text):
    clean = text.replace('\n', ' ').replace('"', '\\"').replace("'", "\\'")
    os.system(f'espeak "{clean}" 2>/dev/null &')

    # -------------------------------------------------

def load_config(config_file, defaults):
    """Load JSON config with fallbacks."""
    config = defaults.copy()
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config.update(json.load(f))
    return config

def get_knowledge(db_file, prophet):
    """Get knowledge from DB."""
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("SELECT content FROM knowledge WHERE prophet = ?", (prophet,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else ""

def update_knowledge(db_file, prophet, new_content, max_words, append=True):
    """Update knowledge in DB, enforce max words."""
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    current = get_knowledge(db_file, prophet)
    updated = current + " " + new_content if append else new_content
    # Enforce max words (trim oldest if over)
    words = updated.split()
    if len(words) > max_words:
        updated = " ".join(words[-max_words:])
    c.execute("INSERT OR REPLACE INTO knowledge (prophet, content) VALUES (?, ?)", (prophet, updated))
    conn.commit()
    conn.close()

def init_db(db_file, prophet, initial_content):
    """Init DB with table and initial content."""
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS knowledge (id INTEGER PRIMARY KEY, prophet TEXT UNIQUE, content TEXT)''')
    c.execute("INSERT OR IGNORE INTO knowledge (prophet, content) VALUES (?, ?)", (prophet, initial_content))
    conn.commit()
    conn.close()

def load_todos(todos_file):
    """Load todos from JSON file."""
    if os.path.exists(todos_file):
        with open(todos_file, "r") as f:
            return json.load(f)
    return {}

def save_todos(todos_file, todos):
    """Save todos to JSON file."""
    with open(todos_file, "w") as f:
        json.dump(todos, f)

def log_message(message, log_file="ai_log.txt"):
    """Log messages (for comm with Grok/user/AI) – promotes debugging."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open(log_file, "a") as f:
        f.write(log_entry)
    print(log_entry)  # Also to console for real-time

def edit_file(file_path, new_content, append=True):
    """General file editor (for .config or others)."""
    if append and os.path.exists(file_path):
        with open(file_path, "r") as f:
            current = f.read()
        updated = current + "\n" + new_content
    else:
        updated = new_content
    with open(file_path, "w") as f:
        f.write(updated)
    log_message(f"Edited file: {file_path}")
