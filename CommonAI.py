# CommonAI.py - Shared library for TrinityAI projects
#Monitoring (RAM, CPU, disk, net from earlier code).
#Research/self-learn (Wikipedia/GitHub API functions).
#Version control (your MAJOR/MINOR/FIX variables as functions).
#Logging/alerting (email on limits).
#Data load/save utils (for ./AIName_data/json).

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
# CommonAI.py - Shared library for TrinityAI projects
# ... (keep your existing imports and functions; only replace/fix BDH section)

import bdh  # Directly import the model file

logger = logging.getLogger("ai_lib")


# ... keep the rest of your file (version, logging, etc.) ...
# Version
MAJOR_VERSION = 0
MINOR_VERSION = 3
FIX_VERSION = 4
VERSION_STRING = f"v{MAJOR_VERSION}.{MINOR_VERSION}.{FIX_VERSION}"

DATA_DIR = "data"
CONFIG_FILE = "data/commonAI_config.json"
DATA_PATH = "data/commonAI_data.json"

logger = logging.getLogger("ai_lib")

# BDH Integration (Baby Dragon Hatchling for core learning/response)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'bdh')))

from bdh.train import BDHModel  # Adapt from BDH code (train.py)

# Load or train BDH on AI data
def load_bdh_model(data_file, param_size=10000000):  # Small for testing
    try:
        model = BDHModel(param_size=param_size)
        # Train on data.json (adapt from README's train.py example)
        with open(data_file, "r") as f:
            data_text = json.dump(json.load(f), indent=4)  # Convert to text for training
        model.train(data_text)  # BDH training call (customize as per code)
        logger.info("BDH model loaded/trained.")
        return model
    except Exception as e:
        logger.error(f"BDH load error: {e}")
        return None

# Load or train BDH on code data
def load_bdh_model(data_file="input_code.txt", config=bdh.BDHConfig()):
    try:
        model = bdh.BDH(config).to("cpu")  # CPU for your setup
        # Train (adapted from train.py logic)
        # For simplicity, run a short train here; use full train.py for long sessions
        with open(data_file, "r") as f:
            data_text = f.read()
        # Byte-level training loop (simplified; full in train.py)
        data = torch.tensor(bytearray(data_text, "utf-8"), dtype=torch.long).to("cpu")
        for _ in range(100):  # Short train; adjust
            ix = torch.randint(0, len(data) - 512, (4,))
            x = torch.stack([data[i:i+512] for i in ix])
            y = torch.stack([data[i+1:i+513] for i in ix])
            logits, loss = model(x, y)
            loss.backward()
            # Simple optimizer (full in train.py)
        logger.info("BDH model loaded/trained on code.")
        return model
    except Exception as e:
        logger.error(f"BDH load error: {e}")
        return None

# ... keep the rest of your file (version, logging, etc.) ...


# Generate response using BDH
def bdh_generate(model, prompt):
    if model is None:
        return "BDH not loaded."
    # Use BDH for "deep" response (adapt from BDH generation logic)
    return model.generate(prompt)  # Placeholder - customize from BDH code

# Generate code/response using BDH
def bdh_generate(model, prompt, max_tokens=100, temp=0.7):
    if model is None:
        return "BDH not loaded."
    prompt_tensor = torch.tensor(bytearray(prompt, "utf-8"), dtype=torch.long).unsqueeze(0).to("cpu")
    return bytes(model.generate(prompt_tensor, max_new_tokens=max_tokens, temperature=temp, top_k=40).squeeze().tolist()).decode(errors="backslashreplace")

# Self-learn with BDH
def bdh_self_learn(model, topic, research):
    if model is None:
        return "BDH not loaded."
    # Update model with new data (Hebbian-style)
    model.update(research)  # Placeholder - adapt BDH's memory update
    return "Learned via BDH."

# Self-learn with BDH on code topics (e.g., research Python funcs)
def bdh_self_learn(model, topic):
    if model is None:
        return "BDH not loaded."
    research = self_research(topic)  # Your existing function
    # Append to data and retrain lightly
    with open("input_code.txt", "a") as f:
        f.write(research + "\n")
    # Retrain short
    load_bdh_model("input_code.txt")  # Reloads with new data
    return "Learned code topic via BDH."

# Load or train BDH on code data
def load_bdh_model(data_file="input_code.txt", config=bdh.BDHConfig()):
    try:
        model = bdh.BDH(config).to("cpu")  # CPU for your setup
        # Train (adapted from train.py logic)
        # For simplicity, run a short train here; use full train.py for long sessions
        with open(data_file, "r") as f:
            data_text = f.read()
        # Byte-level training loop (simplified; full in train.py)
        data = torch.tensor(bytearray(data_text, "utf-8"), dtype=torch.long).to("cpu")
        for _ in range(100):  # Short train; adjust
            ix = torch.randint(0, len(data) - 512, (4,))
            x = torch.stack([data[i:i+512] for i in ix])
            y = torch.stack([data[i+1:i+513] for i in ix])
            logits, loss = model(x, y)
            loss.backward()
            # Simple optimizer (full in train.py)
        logger.info("BDH model loaded/trained on code.")
        return model
    except Exception as e:
        logger.error(f"BDH load error: {e}")
        return None


# Version helper
def get_version(major, minor, fix):
    return f"v{major}.{minor}.{fix}"

def setup_logging(log_file="ai.log"):
    handlers = []
    if os.path.exists(log_file):
        handlers.append(logging.FileHandler(log_file))
    handlers.append(logging.StreamHandler())
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=handlers)

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Config load failed: {e} — using defaults.")
    # Default config...
    return default_config  # Your defaults here

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

def save_config(config=None):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config or CONFIG, f, indent=4)
    except Exception as e:
        logger.error(f"Config save failed: {e}")

def update_data(new_data, file=DATA_FILE):
    try:
        data = load_data(file)
        data.update(new_data)
        with open(file, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Data update failed: {e}")

def load_knowledge(knowledge_file = "knowledge.json"):
    try:
        if os.path.exists(knowledge_file):
            size_mb = os.path.getsize(knowledge_file) / (1024 * 1024)
            if size_mb > CONFIG["DATA_MAX_SIZE_MB"]:
                logger.warning("Data size exceeded — skipping load.")
                return {}
            with open(knowledge_file, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Knowledge load failed: {e} — using empty dict.")
        return {}

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

    # Speak
def speak(text):
    clean = text.replace('\n', ' ').replace('"', '\\"').replace("'", "\\'")
    os.system(f'espeak "{clean}" 2>/dev/null &')

    # CommonAI.py - minimal stub for now

def bdh_generate(model, prompt, max_tokens=300, temp=0.8):
    """Placeholder - will connect to real BDH later"""
    return "# Generated by BDH (stub)\n" + prompt.upper()  # dummy output