from typing import Dict, Any, List

class AlertDispatcherTool:
    def __init__(self):
        self.alerts: List[Dict[str, Any]] = []

    def dispatch(self, alert: Dict[str, Any]):
        self.alerts.append(alert)
        print(f"[ALERT DISPATCHED] {alert}")

    def get_alerts(self, limit=100) -> List[Dict[str, Any]]:
        return self.alerts[-limit:]

    def clear_alerts(self):
        self.alerts.clear()

# dispatcher = AlertDispatcherTool()
# dispatcher.dispatch(alert)  # alert is a dict
# print(dispatcher.get_alerts())
# dispatcher.clear_alerts()


