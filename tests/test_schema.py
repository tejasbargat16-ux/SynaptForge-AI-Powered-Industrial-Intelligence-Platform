"""
Unit tests for SynaptForge Telemetry Schema and Data Validation.
Compatible with standard library unittest and pytest.
"""

import unittest
from simulator.schema import TelemetryRecord, validate_telemetry_dict


class TestTelemetrySchema(unittest.TestCase):
    def test_valid_telemetry_record(self):
        valid_data = {
            "device_id": "synapt-motor-01",
            "timestamp": "2026-10-29T12:00:00Z",
            "temperature_c": 42.5,
            "vibration_rms": 0.18,
            "rpm": 1480.0,
            "voltage_v": 230.0,
            "current_a": 1.4,
            "power_w": 322.0,
            "status": "nominal",
        }
        record = TelemetryRecord.from_dict(valid_data)
        self.assertEqual(record.device_id, "synapt-motor-01")
        self.assertEqual(record.temperature_c, 42.5)
        self.assertEqual(record.power_w, 322.0)
        self.assertEqual(record.status, "nominal")

    def test_automatic_power_calculation(self):
        data = {
            "device_id": "synapt-motor-01",
            "timestamp": "2026-10-29T12:00:00Z",
            "temperature_c": 35.0,
            "vibration_rms": 0.12,
            "rpm": 1450.0,
            "voltage_v": 200.0,
            "current_a": 1.5,
        }
        record = TelemetryRecord.from_dict(data)
        # Power = 200.0 * 1.5 = 300.0 W
        self.assertEqual(record.power_w, 300.0)

    def test_invalid_device_id(self):
        with self.assertRaises(ValueError):
            TelemetryRecord(
                device_id="",
                timestamp="2026-10-29T12:00:00Z",
                temperature_c=35.0,
                vibration_rms=0.1,
                rpm=1450.0,
                voltage_v=230.0,
                current_a=1.0,
            )

    def test_invalid_timestamp(self):
        with self.assertRaises(ValueError):
            TelemetryRecord(
                device_id="motor-01",
                timestamp="invalid-timestamp-string",
                temperature_c=35.0,
                vibration_rms=0.1,
                rpm=1450.0,
                voltage_v=230.0,
                current_a=1.0,
            )

    def test_out_of_bounds_temperature(self):
        with self.assertRaises(ValueError):
            TelemetryRecord(
                device_id="motor-01",
                timestamp="2026-10-29T12:00:00Z",
                temperature_c=250.0,  # Max allowed is 180.0
                vibration_rms=0.1,
                rpm=1450.0,
                voltage_v=230.0,
                current_a=1.0,
            )

    def test_out_of_bounds_vibration(self):
        with self.assertRaises(ValueError):
            TelemetryRecord(
                device_id="motor-01",
                timestamp="2026-10-29T12:00:00Z",
                temperature_c=40.0,
                vibration_rms=50.0,  # Max allowed is 25.0
                rpm=1450.0,
                voltage_v=230.0,
                current_a=1.0,
            )

    def test_invalid_status(self):
        with self.assertRaises(ValueError):
            TelemetryRecord(
                device_id="motor-01",
                timestamp="2026-10-29T12:00:00Z",
                temperature_c=40.0,
                vibration_rms=0.1,
                rpm=1450.0,
                voltage_v=230.0,
                current_a=1.0,
                status="catastrophic_error",
            )


if __name__ == "__main__":
    unittest.main()
