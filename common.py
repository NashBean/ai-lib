#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# common.py - Shared logic for all AIs
# ai_lib/common.py - Shared helpers for AbrahamAI/MosesAI/JesusAI (iBeanSoftware-inspired efficiency)
# ai_lib/common.py - Fully merged shared library for AbrahamAI, MosesAI, JesusAI
# Adds centralized ai_data.db (knowledge/settings/research links), Git-tracked logs/reports
# Preserves ALL original functionality from common.py, CommonAI.py, monitoring.py, ai_tracker.py

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
import datetime
import threading
import hashlib  # Used in original ai_tracker for hashing

# Version
MAJOR_VERSION = 0
MINOR_VERSION = 4
FIX_VERSION = 0
VERSION_STRING = f"v{MAJOR_VERSION}.{MINOR_VERSION}.{FIX_VERSION}"

# ────────────────────────────────────────────────
# Logging (original + enhanced)
# ────────────────────────────────────────────────

logger = logging.getLogger("ai_lib")
logger.setLevel(logging.INFO)

console = logging.StreamHandler()
console.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console)

file_handler = logging.FileHandler("ai.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

LOGS_DIR = "logs"
REPORTS_DIR = "reports"
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
def get_version(major, minor, fix):
    return f"v{major}.{minor}.{fix}"

def setup_logging(log_file="ai.log"):
    handlers = []
    if os.path.exists(log_file):
        handlers.append(logging.FileHandler(log_file))
    handlers.append(logging.StreamHandler())
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=handlers)

def log_message(message, level="INFO", ai_name="System"):
    """Unified log - writes to console, ai.log, and Git-tracked logs/ folder"""
    log_entry = f"[{ai_name}] [{level}] {message}"
    logger.log(getattr(logging, level.upper(), logging.INFO), log_entry)

    # Git-tracked log file
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = os.path.join(LOGS_DIR, f"{timestamp}_{ai_name}_{level}.log")
    with open(log_path, "a") as f:
        f.write(log_entry + "\n")


# System limits check (interweave all monitoring)
def check_system_limits1(config):
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
        msg["Subject"] = "AI Alert"
        msg["From"] = config["SMTP_USER"]
        msg["To"] = config["ALERT_EMAIL"]
        server = smtplib.SMTP(config["SMTP_SERVER"], config["SMTP_PORT"])
        server.starttls()
        server.login(config["SMTP_USER"], config["SMTP_PASS"])
        server.sendmail(config["SMTP_USER"], config["ALERT_EMAIL"], msg.as_string())
        server.quit()
        log_message("Alert sent", "INFO")
    except Exception as e:
        log_message(f"Alert failed: {e}", "ERROR")
# for new version
def check_system_limits(config):
    try:
        if psutil.virtual_memory().used / (1024 ** 3) > config.get("RAM_LIMIT_GB", 4):
            log_message("RAM limit exceeded", "WARNING")
            return False
        if psutil.cpu_percent(interval=1) > config.get("CPU_LIMIT_PERCENT", 80):
            log_message("CPU limit exceeded", "WARNING")
            return False
        disk = psutil.disk_usage('/')
        if disk.free / (1024 ** 3) < config.get("DISK_MIN_FREE_GB", 5):
            log_message("Disk space low", "WARNING")
            return False
        # Net check (original)
        net_start = psutil.net_io_counters()
        time.sleep(1)
        net_end = psutil.net_io_counters()
        bandwidth_mbps = ((net_end.bytes_sent + net_end.bytes_recv - net_start.bytes_sent - net_start.bytes_recv) / 1024 / 1024) * 8
        if bandwidth_mbps < config.get("NET_BANDWIDTH_THRESHOLD_MBPS", 1):
            log_message("Bandwidth low", "WARNING")
            return False
        return True
    except Exception as e:
        log_message(f"System check error: {e}", "ERROR")
        return False


# Research (self-learn)
def self_research(topic):
    if not get_setting("RESEARCH_ENABLED", True):
        return "Research disabled."
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&exintro=&titles={topic.replace(' ', '_')}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        pages = data["query"]["pages"]
        page_id = list(pages.keys())[0]
        if page_id != "-1":
            extract = pages[page_id]["extract"]
            log_message(f"Researched: {topic}", "INFO")
            return extract
        return "No info."
    except Exception as e:
        log_message(f"Research error: {e}", "ERROR")
        return "Research failed."

def self_update(config):
    try:
        owner, repo = config["GITHUB_REPO"].split("/")
        url = f"https://api.github.com/repos/{owner}/{repo}/commits/main"
        headers = {"Authorization": f"Bearer {config.get('GITHUB_TOKEN', '')}"}
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
        log_message(f"Update failed: {e}", "ERROR")
        return "Update failed"

# ────────────────────────────────────────────────
# BDH / pathway integration stubs (from bdh_wrapper.py - preserved)
# ────────────────────────────────────────────────

# Placeholder - replace with your actual BDH import/code when ready
def bdh_generate(model, prompt):
    log_message("BDH generate called", "DEBUG")
    return "BDH placeholder response"

def bdh_self_learn(model, topic, research):
    log_message(f"BDH self-learn on {topic}", "INFO")
    # Your original BDH logic here
    return "Learned via BDH"

# Add any other original BDH/pathway functions here...

print("ai_lib/common.py fully loaded - all original functionality preserved + new DB/Git system")


# GitHub self-update
def self_update_old(config):
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
# ────────────────────────────────────────────────
# Git-tracked logs & reports (small local git db)
# ────────────────────────────────────────────────

def save_report(content, filename_prefix="report"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(REPORTS_DIR, f"{filename_prefix}_{timestamp}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    log_message(f"Report saved: {filename}", "INFO")


# ────────────────────────────────────────────────
# Config loading (original style preserved)
# ────────────────────────────────────────────────

def load_config(config_file="config.json", defaults=None):
    if defaults is None:
        defaults = {}
    config = defaults.copy()
    try:
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                loaded = json.load(f)
                config.update(loaded)
        log_message(f"Loaded config: {config_file}", "INFO")
    except Exception as e:
        log_message(f"Config load failed: {e}", "ERROR")
    return config

# ────────────────────────────────────────────────
# Central SQLite DB (ai_data.db) - knowledge, settings, research links
# NOT tracked in Git (add to .gitignore)
# ────────────────────────────────────────────────

AI_DB_FILE = "ai_data.db"

def init_ai_db():
    conn = sqlite3.connect(AI_DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS knowledge
                 (prophet TEXT PRIMARY KEY, content TEXT, updated_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS research_links
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, prophet TEXT, title TEXT, url TEXT, notes TEXT, added_at TEXT)''')
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


def get_knowledge(prophet):
    try:
        conn = sqlite3.connect(AI_DB_FILE)
        c = conn.cursor()
        c.execute("SELECT content FROM knowledge WHERE prophet = ?", (prophet,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else ""
    except Exception as e:
        log_message(f"Knowledge read error for {prophet}: {e}", "ERROR")
        return ""

def update_knowledge(prophet, new_content, append=True):
    try:
        conn = sqlite3.connect(AI_DB_FILE)
        c = conn.cursor()
        current = get_knowledge(prophet)
        updated = current + "\n" + new_content if append and current else new_content
        timestamp = datetime.datetime.now().isoformat()
        c.execute("INSERT OR REPLACE INTO knowledge (prophet, content, updated_at) VALUES (?, ?, ?)",
                  (prophet, updated, timestamp))
        conn.commit()
        conn.close()
        log_message(f"Knowledge updated for {prophet} ({len(updated.split())} words)", "INFO")
    except Exception as e:
        log_message(f"Knowledge update error: {e}", "ERROR")

def add_research_link(prophet, title, url, notes=""):
    try:
        conn = sqlite3.connect(AI_DB_FILE)
        c = conn.cursor()
        added_at = datetime.datetime.now().isoformat()
        c.execute("INSERT INTO research_links (prophet, title, url, notes, added_at) VALUES (?, ?, ?, ?, ?)",
                  (prophet, title, url, notes, added_at))
        conn.commit()
        conn.close()
        log_message(f"Research link added: {title} ({url})", "INFO")
    except Exception as e:
        log_message(f"Research link save error: {e}", "ERROR")

init_ai_db()  # Ensure DB exists


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
