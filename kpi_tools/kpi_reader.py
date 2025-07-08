import pandas as pd
from typing import List, Dict, Any

class KPIReaderTool:
    def __init__(self, csv_path: str = "data/dummy_kpis.csv"):
        self.csv_path = csv_path

    def get_latest_kpis(self) -> List[Dict[str, Any]]:
        df = pd.read_csv(self.csv_path)
        df_sorted = df.sort_values(by="timestamp", ascending=False)
        latest_kpis = df_sorted.drop_duplicates(subset=["kpi_name", "entity"])
        return latest_kpis.to_dict(orient="records")

reader = KPIReaderTool()
print(reader.get_latest_kpis()[0])
# reader.update_kpi("Revenue", "Group", 91.2)
