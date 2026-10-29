"""
Unit tests for SynaptForge Telemetry Generator.
Compatible with standard library unittest and pytest.
"""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from simulator.generator import TelemetrySimulator, export_to_csv, export_to_json


class TestTelemetrySimulator(unittest.TestCase):
    def test_generator_batch_size(self):
        sim = TelemetrySimulator(device_id="test-rig-01")
        records = sim.generate_batch(count=105, interval_seconds=1, mode="nominal")
        self.assertEqual(len(records), 105)
        self.assertTrue(all(r.device_id == "test-rig-01" for r in records))

    def test_generator_timestamp_sequence(self):
        sim = TelemetrySimulator()
        records = sim.generate_batch(count=10, interval_seconds=2, mode="nominal")
        parsed_timestamps = [
            datetime.fromisoformat(r.timestamp.replace("Z", "+00:00")) for r in records
        ]
        for i in range(1, len(parsed_timestamps)):
            delta = (parsed_timestamps[i] - parsed_timestamps[i - 1]).total_seconds()
            self.assertEqual(delta, 2.0)

    def test_thermal_runaway_mode(self):
        sim = TelemetrySimulator(base_temp_c=40.0)
        records = sim.generate_batch(count=50, interval_seconds=1, mode="thermal_runaway")
        # Temperature at end should be higher than at the start
        self.assertGreater(records[-1].temperature_c, records[0].temperature_c + 10.0)
        self.assertTrue(any(r.status in ("warning", "critical") for r in records))

    def test_bearing_fault_mode(self):
        sim = TelemetrySimulator(base_vibration_rms=0.15)
        records = sim.generate_batch(count=20, interval_seconds=1, mode="bearing_fault")
        self.assertTrue(any(r.vibration_rms > 2.0 for r in records))
        self.assertTrue(any(r.status in ("warning", "critical") for r in records))

    def test_export_to_csv_and_json(self):
        sim = TelemetrySimulator()
        records = sim.generate_batch(count=5, interval_seconds=1, mode="nominal")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            csv_path = tmp_path / "telemetry_test.csv"
            export_to_csv(records, csv_path)
            self.assertTrue(csv_path.exists())
            content = csv_path.read_text(encoding="utf-8")
            self.assertIn("device_id", content)
            self.assertIn("power_w", content)

            json_path = tmp_path / "telemetry_test.json"
            export_to_json(records, json_path)
            self.assertTrue(json_path.exists())
            json_content = json_path.read_text(encoding="utf-8")
            self.assertIn("device_id", json_content)


if __name__ == "__main__":
    unittest.main()
