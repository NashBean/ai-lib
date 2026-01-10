#!/usr/bin/env python3
# ai_tracker.py - Persistent tracker for TrinityAI project (repos, files, functions, versions, connections)
# Run: python3 ai_tracker.py to init/update
# Call from servers/main.py: from ai_tracker import update_project_track

import sqlite3
import datetime
import logging

logger = logging.getLogger("ai-lib")

DB_FILE = "ai_tracker.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS project_track
                 (repo_name TEXT,
                  file_name TEXT,
                  description TEXT,
                  version TEXT,
                  last_update TEXT,
                  functions TEXT,
                  variables TEXT,
                  connections TEXT,
                  PRIMARY KEY (repo_name, file_name))''')
    conn.commit()
    conn.close()
    logger.info("DB initialized.")

def update_project_track(repo_name, file_name, description, version, functions="", variables="", connections=""):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO project_track VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (repo_name, file_name, description, version, str(datetime.datetime.now()), functions, variables, connections))
        conn.commit()
        conn.close()
        logger.info(f"Tracked {file_name} in {repo_name}.")
    except Exception as e:
        logger.error(f"DB update error: {e}")

def get_project_track(repo_name=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        if repo_name:
            c.execute("SELECT * FROM project_track WHERE repo_name=?", (repo_name,))
        else:
            c.execute("SELECT * FROM project_track")
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"DB query error: {e}")
        return []

# Initial population example (run once or on update)
if __name__ == "__main__":
    init_db()
    # Sample for AbrahamAI
    update_project_track("AbrahamAI", "AbrahamAI_Server.py", "Server for queries", "v0.2.4", "handle_client, main", "MAJOR_VERSION=0, MINOR_VERSION=2, FIX_VERSION=4", "Links to ai-lib/CommonAI.py, queries TrintityAI")
    update_project_track("AbrahamAI", "main.py", "Console chat", "v0.2.4", "main", "", "Uses data/abraham_data.json")
    update_project_track("AbrahamAI", "AbrahamAI_Console.cpp", "C++ console", "v0.2.4", "main", "", "Queries server on port 5001")
    update_project_track("AbrahamAI", "edit_data.cpp", "C++ JSON editor", "v0.2.4", "main", "", "Edits data/abraham_data.json")
    # Add for other repos...
    print("Example track for AbrahamAI:")
    print(get_project_track("AbrahamAI"))