#!/usr/bin/env python3
# tracker.py - Database to track all AIs (versions, features, updates)

import sqlite3
import datetime
import logging

logger = logging.getLogger("ai-lib")

DB_FILE = "ai_tracker.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS ais
                     (name TEXT PRIMARY KEY,
                      github_url TEXT,
                      major_version INTEGER,
                      minor_version INTEGER,
                      fix_version INTEGER,
                      features TEXT,
                      last_update TEXT)''')
        conn.commit()
        conn.close()
        logger.info("DB initialized.")
    except Exception as e:
        logger.error(f"DB init error: {e}")

def add_or_update_ai(name, url, major, minor, fix, features):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO ais VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (name, url, major, minor, fix, features, str(datetime.datetime.now())))
        conn.commit()
        conn.close()
        logger.info(f"Updated {name} in DB.")
    except Exception as e:
        logger.error(f"DB update error: {e}")

def get_ai_status(name):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM ais WHERE name=?", (name,))
        row = c.fetchone()
        conn.close()
        if row:
            return {
                "name": row[0],
                "url": row[1],
                "version": f"{row[2]}.{row[3]}.{row[4]}",
                "features": row[5],
                "last_update": row[6]
            }
        return "No info"
    except Exception as e:
        logger.error(f"DB query error: {e}")
        return "Error"

# Initial population (run once)
if __name__ == "__main__":
    init_db()
    # Add your AIs
    add_or_update_ai("AbrahamAI", "https://github.com/NashBean/AbrahamAI", 1, 1, 0, "Culture, Journey, Archaeology, Self-research")
    add_or_update_ai("MosesAI", "https://github.com/NashBean/MosesAI", 1, 1, 0, "Exodus route, Tabernacle, Plagues, Self-research")
    add_or_update_ai("JesusAI", "https://github.com/NashBean/JesusAI", 1, 1, 0, "Parables, Gospels Greek, OT fulfillment, Archaeology, Self-research")
    add_or_update_ai("TrintityAI", "https://github.com/NashBean/TrintityAI", 1, 1, 0, "Unified Trinity, GUI, Server connections, Self-research")
    print("DB created and populated. Example status for AbrahamAI:")
    print(get_ai_status("AbrahamAI"))