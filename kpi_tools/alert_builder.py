from typing import Dict, Any
import datetime

class AlertBuilderTool:
    def build_alert(self, deviation_info: Dict[str, Any]) -> Dict[str, Any]:
        import uuid
        alert = deviation_info.copy()
        alert["alert_id"] = str(uuid.uuid4())
        alert["generated_at"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        return alert



# builder = AlertBuilderTool()
# alert = builder.build_alert(deviation_info)
# print(alert)
