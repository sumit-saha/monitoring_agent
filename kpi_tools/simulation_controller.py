from typing import Optional
import pandas as pd
import datetime

class SimulationControllerTool:
    def __init__(self, csv_path: str = "data/dummy_kpis.csv"):
        self.csv_path = csv_path

    def inject_kpi(self, kpi_name: str, entity: str, value: float, timestamp: Optional[str] = None):
        if not timestamp:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = {"timestamp": timestamp, "kpi_name": kpi_name, "entity": entity, "value": value}
        df = pd.read_csv(self.csv_path)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(self.csv_path, index=False)
        return new_row

sim_tool = SimulationControllerTool()
sim_tool.inject_kpi("Attrition Rate", "Sales Department", 115.5)
