import smtplib
from email.mime.text import MIMEText
import json

class EmailDispatcherTool:
    def __init__(self, config_path="config/email.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)

    def send_email(self, alert):
        msg = MIMEText(self.format_body(alert))
        msg['Subject'] = f"ALERT: [{alert.get('severity', 'INFO').upper()}] {alert.get('kpi_name', '')} deviation"
        msg['From'] = self.config["from_email"]
        msg['To'] = ", ".join(self.config["to_emails"])

        with smtplib.SMTP(self.config["smtp_host"], self.config["smtp_port"]) as server:
            server.starttls()
            server.login(self.config["smtp_user"], self.config["smtp_password"])
            server.send_message(msg)

    def format_body(self, alert):
        return f"""
ALERT: [{alert.get('severity', 'INFO').upper()}] {alert.get('kpi_name', '')} deviation detected!
KPI: {alert.get('kpi_name', '')}
Entity: {alert.get('entity', '')}
Value: {alert.get('value', '')} (Target: {alert.get('target', '')})
Deviation: {alert.get('deviation', '')} ({alert.get('deviation_type', '')})
Time: {alert.get('timestamp', '')}
"""


# Place this at the bottom of email_dispatcher.py for a manual test

test_alert = {
    "alert_id": "test-alert-001",
    "kpi_name": "Revenue",
    "entity": "Group",
    "value": 88.2,
    "target": 100,
    "deviation": -11.8,
    "deviation_type": "-11.8% below target",
    "severity": "high",
    "timestamp": "2025-07-01 10:05:00",
    "generated_at": "2025-07-01 10:05:01"
}

if __name__ == "__main__":
    dispatcher = EmailDispatcherTool()
    dispatcher.send_email(test_alert)
    print("Test email sent!")


# Usage (after alert is created and before/after mock dispatcher):
# email_tool = EmailDispatcherTool()
# email_tool.send_email(alert_dict)