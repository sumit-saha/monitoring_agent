from fastapi import FastAPI
import threading
import time
import datetime
import pandas as pd
import json
from typing import Dict, Any, Optional, List

from langchain.tools import tool
from langchain_community.llms import FakeListLLM
from langchain.agents import initialize_agent, AgentType
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os

from kpi_tools.alert_builder import AlertBuilderTool
from kpi_tools.alert_dispatcher import AlertDispatcherTool
from kpi_tools.email_dispatcher import EmailDispatcherTool
from kpi_tools.kpi_reader import KPIReaderTool
from kpi_tools.simulation_controller import SimulationControllerTool
from kpi_tools.threshold_evaluator import ThresholdEvaluatorTool
load_dotenv()

kpi_reader = KPIReaderTool()
evaluator = ThresholdEvaluatorTool()
builder = AlertBuilderTool()
dispatcher = AlertDispatcherTool()
email_dispatcher = EmailDispatcherTool()
simulator = SimulationControllerTool()

@tool("read_latest_kpis", return_direct=True)
def read_latest_kpis_tool(dummy: str = ""):
    """Read the latest KPI values for each (kpi_name, entity) pair. Returns JSON string."""
    return json.dumps(kpi_reader.get_latest_kpis())

@tool("evaluate_threshold", return_direct=True)
def evaluate_threshold_tool(kpi_record_json: str):
    """Evaluate a single KPI record (as JSON string) against its threshold. Returns JSON string or 'null'."""
    kpi_record = json.loads(kpi_record_json)
    result = evaluator.evaluate(kpi_record)
    return json.dumps(result) if result else "null"

@tool("build_alert", return_direct=True)
def build_alert_tool(deviation_info_json: str):
    """Build a structured alert dictionary from deviation info (JSON string). Returns JSON string."""
    deviation_info = json.loads(deviation_info_json)
    return json.dumps(builder.build_alert(deviation_info))

@tool("dispatch_alert", return_direct=True)
def dispatch_alert_tool(alert_json: str):
    """Dispatch an alert (JSON string) (store and send email)."""
    alert = json.loads(alert_json)
    dispatcher.dispatch(alert)
    try:
        email_dispatcher.send_email(alert)
    except Exception as e:
        return f"Email dispatch failed: {e}"
    return "Alert dispatched and email sent"

tools = [
    read_latest_kpis_tool,
    evaluate_threshold_tool,
    build_alert_tool,
    dispatch_alert_tool
]

llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")  # For testing with smaller model

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

app = FastAPI(title="Monitoring Agent")

monitoring_active = False
monitoring_thread = None
MONITOR_INTERVAL_SECONDS = 300  # Use 30s for demo; use 300 for production

def monitoring_loop():
    global monitoring_active,last_run_time
    while monitoring_active:
        print("[MONITOR] Polling KPIs using LangChain Agent...")
        last_run_time = datetime.datetime.now()
        # Agent prompt: read, evaluate, alert, dispatch, email
        latest_kpis = kpi_reader.get_latest_kpis()
        for kpi in latest_kpis:
            deviation = evaluator.evaluate(kpi)
            if deviation:
                alert = builder.build_alert(deviation)
                print('deiation:', deviation)
                dispatcher.dispatch(alert)
                email_dispatcher.send_email(alert)
        time.sleep(MONITOR_INTERVAL_SECONDS)
        # Or, use LLM agent.run for full agent orchestration (see below)
        # prompt = (
        #     "Read the latest KPIs. For each KPI, if it violates its threshold, "
        #     "evaluate it, build an alert, and dispatch the alert (including sending email)."
        # )
        # try:
        #     agent.run(prompt)
        # except Exception as e:
        #     print(f"[AGENT ERROR] {e}")

@app.post("/monitor/start")
def start_monitoring():
    global monitoring_active, monitoring_thread
    if monitoring_active:
        return {"message": "Monitoring already running."}
    monitoring_active = True
    monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
    monitoring_thread.start()
    return {"message": "Monitoring started."}

@app.post("/monitor/stop")
def stop_monitoring():
    global monitoring_active
    monitoring_active = False
    return {"message": "Monitoring stopped."}

@app.get("/alerts")
def get_alerts(limit: int = 100):
    return dispatcher.get_alerts(limit=limit)

@app.post("/simulate/update-data")
def simulate_kpi(kpi_name: str, entity: str, value: float):
    row = simulator.inject_kpi(kpi_name, entity, value)
    return {"message": "KPI injected", "row": row}

@app.get("/health")
def health():
    status = "running" if monitoring_active else "stopped"
    last_time_str = last_run_time.strftime("%Y-%m-%d %H:%M:%S") if last_run_time else None
    num_alerts = len(dispatcher.get_alerts())
    return {
        "status": status,
        "last_monitor_time": last_time_str,
        "alert_count": num_alerts,
        "recent_alerts": dispatcher.get_alerts(limit=5)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# reader = KPIReaderTool()
# latest_kpis =reader.get_latest_kpis()
# print("Latest KPI:", latest_kpis)
# print("type:", type(latest_kpis))

# eval_tool = ThresholdEvaluatorTool()
# for kpi in latest_kpis:
#     # print(f"Evaluating KPI: {kpi['kpi_name']} for entity: {kpi['entity']}")
#     alert_info = eval_tool.evaluate(kpi)
#     # alert_info = eval_tool.evaluate(kpi)
#     if alert_info:
#         print("alert_info",alert_info)
