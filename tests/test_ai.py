"""
Unit tests for SynaptForge AI and Anomaly Engine.
"""

import unittest
from ai.anomaly_engine import compute_features, AnomalyDetector


class TestAnomalyEngine(unittest.TestCase):
    def test_compute_features(self):
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        feats = compute_features(values)
        self.assertEqual(feats.mean, 30.0)
        self.assertEqual(feats.min_val, 10.0)
        self.assertEqual(feats.max_val, 50.0)
        self.assertGreater(feats.rms, 0)
        self.assertGreater(feats.crest_factor, 0)

    def test_nominal_record_score(self):
        detector = AnomalyDetector()
        record = {
            "device_id": "synapt-motor-01",
            "timestamp": "2026-10-29T12:00:00Z",
            "temperature_c": 41.5,
            "vibration_rms": 0.16,
            "voltage_v": 230.0,
            "rpm": 1475.0,
        }
        res = detector.score_record(record)
        self.assertEqual(res["severity"], "nominal")
        self.assertEqual(len(res["detected_anomalies"]), 0)

    def test_critical_anomaly_detection(self):
        detector = AnomalyDetector()
        record = {
            "device_id": "synapt-motor-01",
            "timestamp": "2026-10-29T12:00:00Z",
            "temperature_c": 82.0,  # Critical thermal deviation
            "vibration_rms": 0.16,
            "voltage_v": 230.0,
            "rpm": 1475.0,
        }
        res = detector.score_record(record)
        self.assertEqual(res["severity"], "critical")
        self.assertTrue(any(a["metric"] == "temperature_c" for a in res["detected_anomalies"]))


if __name__ == "__main__":
    unittest.main()
