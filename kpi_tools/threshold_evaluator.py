import json
from typing import List, Dict, Any, Optional


class ThresholdEvaluatorTool:
    def __init__(self, rules_path: str = "data/kpi_rules.json"):
        with open(rules_path, "r") as f:
            self.rules = json.load(f)

    def get_rule(self, kpi_name: str, entity: str) -> Optional[Dict[str, Any]]:
        for rule in self.rules:
            if rule["kpi_name"] == kpi_name and rule["entity"] == entity:
                # print('rule ',rule)
                return rule
        return None

    def evaluate(self, kpi_record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        rule = self.get_rule(kpi_record["kpi_name"], kpi_record["entity"])
        if not rule:
            return None
        value = float(kpi_record["value"])
        target = float(rule["target"])
        threshold_type = rule["threshold_type"]
        threshold_value = float(rule["threshold_value"])
        comparison = rule["comparison"]
        severity = rule.get("severity", "medium")

        deviation = 0
        deviation_type = None
        violated = False

        if threshold_type == "percent":
            percent_dev = ((value - target) / target) * 100 if target != 0 else 0
            deviation = round(percent_dev, 2)
            if comparison == "below" and value < target * (1 - threshold_value/100):
                violated = True
                deviation_type = f"{deviation}% below target"
            elif comparison == "above" and value > target * (1 + threshold_value/100):
                violated = True
                deviation_type = f"{deviation}% above target"
        else:  # absolute
            abs_dev = value - target
            deviation = round(abs_dev, 2)
            if comparison == "below" and value < target - threshold_value:
                violated = True
                deviation_type = f"{deviation} below target"
            elif comparison == "above" and value > target + threshold_value:
                violated = True
                deviation_type = f"{deviation} above target"

        if violated:
            return {
                "kpi_name": kpi_record["kpi_name"],
                "entity": kpi_record["entity"],
                "value": value,
                "target": target,
                "deviation": deviation,
                "deviation_type": deviation_type,
                "severity": severity,
                "timestamp": kpi_record["timestamp"]
            }
        return None

# eval_tool = ThresholdEvaluatorTool()
# for kpi in latest_kpis:
#     alert_info = eval_tool.evaluate(kpi)
#     if alert_info:
#         print(alert_info)
