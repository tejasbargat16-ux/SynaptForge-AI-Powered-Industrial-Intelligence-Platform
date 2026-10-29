# SynaptForge Architecture & Specification

## 1. System Overview
SynaptForge is an AI-powered industrial intelligence and energy optimization platform. It tracks mechanical and electrical parameters for rotating machinery (motors, pumps, turbines) or electrical test benches.

```
[ Sensor Node / Simulator ] ──(JSON Telemetry)──> [ Ingestion & Validation ] ──> [ TimeSeries Store ]
                                                          │                                │
                                                          ▼                                ▼
                                               [ Anomaly Detection ]            [ Digital Twin Dashboard ]
                                               [ Feature Extraction]            [ Real-time Analytics   ]
```

## 2. Telemetry Specification

| Field | Type | Unit | Allowed Range | Description |
|---|---|---|---|---|
| `device_id` | String | - | Alphanumeric | Unique asset identifier (e.g. `synapt-motor-01`) |
| `timestamp` | String (ISO 8601) | UTC | - | RFC 3339 formatted UTC timestamp |
| `temperature_c` | Float | °C | -40.0 to 180.0 | Motor housing or bearing temperature |
| `vibration_rms` | Float | mm/s | 0.0 to 25.0 | Overall velocity RMS vibration level |
| `rpm` | Float | rev/min | 0.0 to 10000.0 | Revolutions per minute |
| `voltage_v` | Float | V | 0.0 to 600.0 | Operating RMS supply voltage |
| `current_a` | Float | A | 0.0 to 100.0 | Drawn RMS phase current |
| `power_w` | Float | W | >= 0.0 | Active electrical power consumption |
| `status` | String | - | nominal, warning, critical | Assessed device condition |

## 3. Anomaly Heuristics & Baselines

- **Nominal Baseline:**
  - Temperature: 35°C – 50°C
  - Vibration RMS: < 0.35 mm/s (ISO 10816 Class I machine baseline)
  - Voltage: 220V – 240V AC
  - Power: Proportional to mechanical load

- **Warning Thresholds:**
  - Temperature: > 55°C
  - Vibration RMS: > 1.8 mm/s
  - Voltage: < 195V or > 255V

- **Critical Thresholds:**
  - Temperature: > 75°C (thermal runaway risk)
  - Vibration RMS: > 4.5 mm/s (severe unbalance, bearing breakdown)
  - Voltage: < 170V (severe line sag)
