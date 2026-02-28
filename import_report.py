import sqlite3
import datetime

MAJOR_VERSION = 0
MINOR_VERSION = 1
FIX_VERSION = 0

REPORT_FILE = "code_base_report.txt"
DB_FILE = "code_reports.db"

with open(REPORT_FILE, "r") as f:
    report_text = f.read()

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute("""
    INSERT INTO reports (generated_at, report_text, source_path, notes)
    VALUES (?, ?, ?, ?)
""", (datetime.datetime.now().isoformat(), report_text, "/home/nash/code", "Initial full scan"))
conn.commit()
conn.close()
print("Report imported successfully.")