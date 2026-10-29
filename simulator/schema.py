"""
SynaptForge Telemetry Schema and Data Validation.
Enforces type, bounds, and required field integrity on industrial telemetry.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Union


VALID_STATUSES = {"nominal", "warning", "critical"}

# Physical / plausible operational constraints for sanity validation
CONSTRAINTS = {
    "temperature_c": (-40.0, 180.0),   # Industrial operating window
    "vibration_rms": (0.0, 25.0),      # RMS vibration in mm/s or g
    "rpm": (0.0, 10000.0),             # Rotational speed
    "voltage_v": (0.0, 600.0),         # Voltage
    "current_a": (0.0, 100.0),         # Current in Amperes
}


@dataclass
class TelemetryRecord:
    device_id: str
    timestamp: str
    temperature_c: float
    vibration_rms: float
    rpm: float
    voltage_v: float
    current_a: float
    power_w: Optional[float] = None
    status: str = "nominal"

    def __post_init__(self):
        if not self.device_id or not isinstance(self.device_id, str):
            raise ValueError("device_id must be a non-empty string.")

        # Ensure timestamp is ISO-parseable
        try:
            # Handle ISO string validation
            dt_str = self.timestamp.replace("Z", "+00:00")
            datetime.fromisoformat(dt_str)
        except Exception as e:
            raise ValueError(f"Invalid timestamp format '{self.timestamp}': {e}")

        # Ensure numeric types and range sanity
        for field, (min_val, max_val) in CONSTRAINTS.items():
            val = getattr(self, field)
            if not isinstance(val, (int, float)):
                raise TypeError(f"Field '{field}' must be a numeric value, got {type(val).__name__}")
            if val < min_val or val > max_val:
                raise ValueError(
                    f"Field '{field}' with value {val} is outside allowed operational limits [{min_val}, {max_val}]."
                )

        if self.power_w is None:
            # Active power calculation assuming resistive / balanced baseline (P = V * I)
            self.power_w = round(self.voltage_v * self.current_a, 2)
        else:
            if not isinstance(self.power_w, (int, float)) or self.power_w < 0:
                raise ValueError("power_w must be a non-negative number.")

        if self.status not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{self.status}'. Must be one of {VALID_STATUSES}")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TelemetryRecord":
        return cls(
            device_id=str(data.get("device_id", "")),
            timestamp=str(data.get("timestamp", "")),
            temperature_c=float(data.get("temperature_c", 0.0)),
            vibration_rms=float(data.get("vibration_rms", 0.0)),
            rpm=float(data.get("rpm", 0.0)),
            voltage_v=float(data.get("voltage_v", 0.0)),
            current_a=float(data.get("current_a", 0.0)),
            power_w=float(data["power_w"]) if "power_w" in data and data["power_w"] is not None else None,
            status=str(data.get("status", "nominal")),
        )


def validate_telemetry_dict(data: Dict[str, Any]) -> Union[TelemetryRecord, Dict[str, str]]:
    """
    Validates a dictionary against the TelemetryRecord schema.
    Returns the parsed TelemetryRecord on success, or raises ValueError.
    """
    return TelemetryRecord.from_dict(data)
