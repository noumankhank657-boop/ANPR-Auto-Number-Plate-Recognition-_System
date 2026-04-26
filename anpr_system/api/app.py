from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from database.db import get_all_logs, get_analytics

app = FastAPI(title="ANPR Traffic API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "ANPR API is healthy"}


@app.get("/logs")
def read_logs(vehicle_type: Optional[str] = Query(None), video_source: Optional[str] = Query(None)):
    logs = get_all_logs()
    if vehicle_type:
        logs = [log for log in logs if log["vehicle_type"] == vehicle_type]
    if video_source:
        logs = [log for log in logs if log["video_source"] == video_source]
    return {"count": len(logs), "logs": logs}


@app.get("/analytics")
def analytics():
    analytics_data = get_analytics()
    return analytics_data


@app.get("/analytics/hourly")
def analytics_hourly():
    analytics_data = get_analytics()
    return {"hourly": analytics_data.get("hourly_counts", [])}
