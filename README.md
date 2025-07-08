
# Monitoring Agent — README

## Overview

This project implements a KPI Monitoring Agent that:

* Monitors key business metrics (KPIs) from a dummy dataset
* Evaluates against rules
* Sends alerts (including via email) if thresholds are breached

## A. **LangChain Version**

### **Setup Instructions**

1. **Clone and prepare**

   ```bash
   git clone <your_repo_url>
   cd monitoring_agent
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Prepare config and data**

   * Fill out `data/dummy_kpis.csv` and `data/kpi_rules.json` with your metrics and rules
   * Configure email settings in `config/email.json`

3. **(Optional) Set OpenAI API Key for LLM-driven orchestration**

   ```bash
   export OPENAI_API_KEY=sk-...  # Linux/Mac
   # or set OPENAI_API_KEY=sk-... on Windows
   ```

4. **Run the server**

   ```bash
   uvicorn main:app --reload
   ```

---

### **Sample Input/Output**

* **Input:**

  * `dummy_kpis.csv`

    ```
    timestamp,kpi_name,entity,value
    2025-07-01 10:00:00,Revenue,Group,92.5
    2025-07-01 10:00:00,Attrition Rate,HR Department,18.2
    ```
  * `kpi_rules.json`

    ```json
    [
      {
        "kpi_name": "Revenue",
        "entity": "Group",
        "target": 100,
        "threshold_type": "percent",
        "threshold_value": 10,
        "comparison": "below",
        "severity": "high"
      }
    ]
    ```

* **How to simulate a new KPI (via API):**

  ```
  POST /simulate/update-data
  {
    "kpi_name": "Revenue",
    "entity": "Group",
    "value": 85.0
  }
  ```

* **Output:**

  * If a value deviates, `/alerts` endpoint returns:

    ```json
    [
      {
        "alert_id": "b2c9d...e6",
        "kpi_name": "Revenue",
        "entity": "Group",
        "value": 85.0,
        "target": 100,
        "deviation": -15.0,
        "deviation_type": "-15.0% below target",
        "severity": "high",
        "timestamp": "2025-07-01 11:00:00",
        "generated_at": "2025-07-01 11:00:03"
      }
    ]
    ```
  * And you receive an alert email (if configured).

---

### **Agent Architecture Diagram **

![Architecture Image](assets\Langchain.png)
