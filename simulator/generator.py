"""
SynaptForge Telemetry Generator.
Generates synthetic multi-parameter industrial telemetry with nominal and anomaly profiles.
"""

import argparse
import csv
import json
import math
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Generator

# Allow running as standalone script or imported module
try:
    from .schema import TelemetryRecord
except ImportError:
    from schema import TelemetryRecord


class TelemetrySimulator:
    def __init__(
        self,
        device_id: str = "synapt-motor-01",
        base_temp_c: float = 40.0,
        base_vibration_rms: float = 0.15,
        base_rpm: float = 1480.0,
        base_voltage_v: float = 230.0,
        base_current_a: float = 1.35,
    ):
        self.device_id = device_id
        self.base_temp_c = base_temp_c
        self.base_vibration_rms = base_vibration_rms
        self.base_rpm = base_rpm
        self.base_voltage_v = base_voltage_v
        self.base_current_a = base_current_a

    def generate_reading(
        self,
        timestamp: datetime,
        step: int = 0,
        mode: str = "nominal",
    ) -> TelemetryRecord:
        """
        Generates a single TelemetryRecord based on time index and operational mode.
        """
        # Periodic oscillation to mimic continuous mechanical load cycles
        oscillation = math.sin(step * 0.1) * 0.8

        temp = self.base_temp_c + random.gauss(0, 0.3) + (oscillation * 0.2)
        vib = max(0.02, self.base_vibration_rms + random.gauss(0, 0.02) + (abs(oscillation) * 0.01))
        rpm = self.base_rpm + random.gauss(0, 3.5) + (oscillation * 2.0)
        volt = self.base_voltage_v + random.gauss(0, 0.6)
        curr = self.base_current_a + random.gauss(0, 0.03)
        status = "nominal"

        # Apply specific mode perturbations
        if mode == "thermal_runaway":
            # Progressive temperature rise
            creep = min(45.0, (step ** 1.15) * 0.8)
            temp += creep
            curr += creep * 0.02
            if temp > 75.0:
                status = "critical"
            elif temp > 55.0:
                status = "warning"

        elif mode == "bearing_fault":
            # High vibration spikes with intermittent severity
            vib_boost = random.uniform(2.5, 6.8)
            vib += vib_boost
            rpm -= random.uniform(15.0, 45.0)  # Increased mechanical drag
            curr += random.uniform(0.3, 0.8)
            status = "critical" if vib > 4.0 else "warning"

        elif mode == "voltage_sag":
            # Supply voltage drop, motor draws compensatory current
            sag = random.uniform(35.0, 65.0)
            volt = max(150.0, volt - sag)
            curr += random.uniform(0.8, 1.8)
            status = "warning" if volt > 180.0 else "critical"

        elif mode == "mixed":
            # Random anomalies occur intermittently
            if step > 20 and step % 35 in (0, 1, 2):
                vib += random.uniform(2.0, 4.5)
                status = "warning"
            elif step > 50 and step % 45 in (0, 1, 2, 3):
                temp += random.uniform(20.0, 32.0)
                status = "warning" if temp < 70.0 else "critical"
            elif step > 80 and step % 60 == 0:
                volt -= 45.0
                curr += 1.2
                status = "critical"

        # Format ISO timestamp with UTC 'Z'
        ts_str = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

        return TelemetryRecord(
            device_id=self.device_id,
            timestamp=ts_str,
            temperature_c=round(temp, 2),
            vibration_rms=round(vib, 3),
            rpm=round(rpm, 1),
            voltage_v=round(volt, 2),
            current_a=round(curr, 2),
            status=status,
        )

    def generate_batch(
        self,
        count: int = 100,
        interval_seconds: int = 2,
        mode: str = "nominal",
        start_time: datetime = None,
    ) -> List[TelemetryRecord]:
        """
        Generates a sequence of timestamped records.
        """
        if start_time is None:
            start_time = datetime.now(timezone.utc) - timedelta(seconds=count * interval_seconds)

        records = []
        for i in range(count):
            curr_ts = start_time + timedelta(seconds=i * interval_seconds)
            record = self.generate_reading(curr_ts, step=i, mode=mode)
            records.append(record)
        return records


def export_to_csv(records: List[TelemetryRecord], filepath: Path) -> None:
    """Exports a list of TelemetryRecord objects to a CSV file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        return

    fieldnames = list(records[0].to_dict().keys())
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(r.to_dict())


def export_to_json(records: List[TelemetryRecord], filepath: Path) -> None:
    """Exports a list of TelemetryRecord objects to a JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, mode="w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in records], f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="SynaptForge Telemetry Generator")
    parser.add_argument("--count", type=int, default=120, help="Number of records to generate (default: 120)")
    parser.add_argument("--interval", type=int, default=2, help="Seconds between readings (default: 2)")
    parser.add_argument(
        "--mode",
        choices=["nominal", "thermal_runaway", "bearing_fault", "voltage_sag", "mixed"],
        default="mixed",
        help="Operational simulation mode (default: mixed)",
    )
    parser.add_argument("--device", type=str, default="synapt-motor-01", help="Device ID identifier")
    parser.add_argument("--output", type=str, default="data/sample_telemetry.csv", help="Output file path (CSV or JSON)")

    args = parser.parse_args()

    simulator = TelemetrySimulator(device_id=args.device)
    records = simulator.generate_batch(count=args.count, interval_seconds=args.interval, mode=args.mode)

    out_path = Path(args.output)
    if out_path.suffix.lower() == ".json":
        export_to_json(records, out_path)
    else:
        export_to_csv(records, out_path)

    # Print summary of generated dataset
    status_counts = {}
    for r in records:
        status_counts[r.status] = status_counts.get(r.status, 0) + 1

    print(f"Generated {len(records)} readings for '{args.device}' in '{args.mode}' mode.")
    print(f"Saved to: {out_path.resolve()}")
    print("Status breakdown:")
    for status, count in status_counts.items():
        print(f"  - {status}: {count} ({count / len(records) * 100:.1f}%)")


if __name__ == "__main__":
    main()
