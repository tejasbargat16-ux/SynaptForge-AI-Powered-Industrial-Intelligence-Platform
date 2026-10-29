"""
SynaptForge FastAPI Backend Service.
Provides REST ingestion endpoints, health monitoring, and telemetry query APIs.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
from pathlib import Path
import json

try:
    from fastapi import FastAPI, HTTPException, status
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
except ImportError:
    # Allow code inspection or fallback if fastapi is not yet installed in host environment
    FastAPI = None

from simulator.schema import TelemetryRecord, validate_telemetry_dict
from simulator.generator import TelemetrySimulator
from ai.anomaly_engine import AnomalyDetector


def create_app():
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Run 'pip install fastapi uvicorn' to run backend server.")

    app = FastAPI(
        title="SynaptForge Industrial Intelligence API",
        description="Core telemetry ingestion, digital twin state, and anomaly detection backend.",
        version="1.0.0",
    )

    # Enable CORS for local dashboards
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Internal state storage
    telemetry_buffer: List[Dict[str, Any]] = []
    simulator = TelemetrySimulator()
    detector = AnomalyDetector()

    # Prepopulate buffer with simulated data
    initial_records = simulator.generate_batch(count=20, interval_seconds=2, mode="mixed")
    for r in initial_records:
        telemetry_buffer.append(r.to_dict())

    @app.get("/")
    def root():
        return {
            "platform": "SynaptForge",
            "architecture": "Nexus Sentinel",
            "status": "online",
            "version": "1.0.0",
            "documentation": "/docs",
        }

    @app.get("/api/health")
    def health():
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "buffered_records": len(telemetry_buffer),
            "asset_id": "synapt-motor-01",
        }

    @app.get("/api/telemetry/latest")
    def get_latest_telemetry():
        if not telemetry_buffer:
            reading = simulator.generate_reading(datetime.now(timezone.utc))
            return reading.to_dict()
        return telemetry_buffer[-1]

    @app.get("/api/telemetry/history")
    def get_history(limit: int = 50):
        return telemetry_buffer[-limit:]

    @app.post("/api/telemetry", status_code=status.HTTP_201_CREATED)
    def ingest_telemetry(payload: Dict[str, Any]):
        try:
            record = validate_telemetry_dict(payload)
        except (ValueError, TypeError) as err:
            raise HTTPException(status_code=400, detail=f"Schema validation failure: {str(err)}")

        record_dict = record.to_dict()
        telemetry_buffer.append(record_dict)
        if len(telemetry_buffer) > 500:
            telemetry_buffer.pop(0)

        # Evaluate anomalies
        analysis = detector.score_record(record_dict)

        return {
            "message": "Telemetry record ingested successfully.",
            "record": record_dict,
            "analysis": analysis,
        }

    @app.get("/api/anomalies/latest")
    def get_latest_anomaly_score():
        latest = telemetry_buffer[-1] if telemetry_buffer else simulator.generate_reading(datetime.now(timezone.utc)).to_dict()
        return detector.score_record(latest)

    # Mount static dashboard folder if it exists
    dashboard_dir = Path(__file__).resolve().parent.parent / "dashboard"
    if dashboard_dir.exists():
        app.mount("/dashboard", StaticFiles(directory=str(dashboard_dir), html=True), name="dashboard")

    return app


if FastAPI is not None:
    app = create_app()
else:
    app = None


if __name__ == "__main__":
    if FastAPI is not None:
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        print("FastAPI is not installed in the current environment.")
