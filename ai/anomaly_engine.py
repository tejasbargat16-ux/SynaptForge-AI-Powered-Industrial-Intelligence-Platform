"""
SynaptForge AI Feature Extraction and Statistical Anomaly Engine.
Provides descriptive statistics, Z-score baseline anomaly scoring, and windowed feature extraction.
"""

import math
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class SignalFeatures:
    mean: float
    std_dev: float
    min_val: float
    max_val: float
    rms: float
    crest_factor: float


def compute_features(values: List[float]) -> SignalFeatures:
    """Computes descriptive time-domain features for a sensor series."""
    if not values:
        return SignalFeatures(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    n = len(values)
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / n if n > 1 else 0.0
    std_dev = math.sqrt(variance)
    min_val = min(values)
    max_val = max(values)
    rms = math.sqrt(sum(x ** 2 for x in values) / n)
    peak = max(abs(min_val), abs(max_val))
    crest_factor = (peak / rms) if rms > 1e-6 else 0.0

    return SignalFeatures(
        mean=round(mean, 3),
        std_dev=round(std_dev, 3),
        min_val=round(min_val, 3),
        max_val=round(max_val, 3),
        rms=round(rms, 3),
        crest_factor=round(crest_factor, 3),
    )


class AnomalyDetector:
    """
    Statistical Z-Score baseline anomaly evaluator with adaptive thresholds.
    """
    def __init__(self, z_warning: float = 2.5, z_critical: float = 3.5):
        self.z_warning = z_warning
        self.z_critical = z_critical
        self.baselines: Dict[str, Dict[str, float]] = {
            "temperature_c": {"mean": 41.5, "std": 3.2},
            "vibration_rms": {"mean": 0.16, "std": 0.08},
            "voltage_v": {"mean": 230.0, "std": 4.5},
            "rpm": {"mean": 1475.0, "std": 12.0},
        }

    def update_baseline(self, metric: str, history: List[float]) -> None:
        """Dynamically recalibrate baseline from verified nominal operations."""
        if len(history) < 10:
            return
        features = compute_features(history)
        self.baselines[metric] = {
            "mean": features.mean,
            "std": max(1e-4, features.std_dev),
        }

    def score_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a telemetry dictionary and returns Z-scores and anomaly classifications.
        """
        anomalies = []
        max_z = 0.0
        scores = {}

        for metric, stats in self.baselines.items():
            val = record.get(metric)
            if val is not None and isinstance(val, (int, float)):
                z = abs(val - stats["mean"]) / stats["std"]
                scores[f"{metric}_z"] = round(z, 2)
                if z > max_z:
                    max_z = z

                if z >= self.z_critical:
                    anomalies.append({
                        "metric": metric,
                        "value": val,
                        "z_score": round(z, 2),
                        "severity": "critical",
                    })
                elif z >= self.z_warning:
                    anomalies.append({
                        "metric": metric,
                        "value": val,
                        "z_score": round(z, 2),
                        "severity": "warning",
                    })

        severity = "nominal"
        if max_z >= self.z_critical:
            severity = "critical"
        elif max_z >= self.z_warning:
            severity = "warning"

        return {
            "device_id": record.get("device_id"),
            "timestamp": record.get("timestamp"),
            "max_z_score": round(max_z, 2),
            "severity": severity,
            "detected_anomalies": anomalies,
            "scores": scores,
        }
