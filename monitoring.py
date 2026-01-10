import psutil
import logging
import smtplib
from email.mime.text import MIMEText

logger = logging.getLogger("ai-lib")

def check_system_limits(config):
    used_ram_gb = psutil.virtual_memory().used / (1024 ** 3)
    if used_ram_gb > config.get("RAM_LIMIT_GB", 4):
        logger.warning(f"RAM high: {used_ram_gb:.2f}GB")
        return False
    # Add CPU, disk, net from your code
    return True

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
    except Exception as e:
        logger.error(f"Alert failed: {e}")