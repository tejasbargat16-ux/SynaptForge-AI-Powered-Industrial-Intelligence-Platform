# ⚡ NEXUS SENTINEL

**An AI-powered industrial intelligence and energy optimization platform**  
*Embedded Systems · Edge AI · Industrial IoT · Digital Twins · Cybersecurity · Energy Analytics*

> **Project status:** Planning / initial prototype. Features marked as planned are not implemented until working code and tests are added.

NEXUS SENTINEL is a modular engineering project designed to monitor a machine or low-voltage test rig, collect sensor telemetry, identify unusual operating conditions, estimate energy use, and present insights through a live dashboard.

The first version will use simulated sensor readings so the software can be developed and tested before connecting physical electronics. Later versions can integrate an ESP32 and suitable sensors.

---

## 🎯 Project vision

Build an affordable, extensible system that turns raw sensor data into useful operational information. The platform is intended for learning, prototyping, college demonstrations, and future research into industrial monitoring.

### The problem

Small workshops, laboratories, and student projects may not have an affordable way to view machine conditions, review historical sensor readings, spot unusual behavior, and understand energy consumption in one place.

### The proposed solution

NEXUS SENTINEL combines a sensor node, a data pipeline, analytics, and a dashboard. It should help an operator answer questions such as:

- What is the machine's current measured state?
- Which readings are outside the configured baseline?
- When did an unusual event occur?
- How has energy consumption changed over time?
- What evidence caused the system to raise an alert?

**Important:** An anomaly is not automatically a fault, and anomaly detection is not the same as validated failure prediction. The project will report measured results and limitations rather than making unsupported reliability claims.

---

## 🧩 Planned capabilities

### Phase 1 — Software MVP

- Generate realistic, timestamped sample telemetry.
- Validate incoming data and reject malformed readings.
- Store readings and events in a local database.
- Provide a documented backend API.
- Show sensor values and recent events on a dashboard.
- Include automated tests and repeatable setup instructions.

### Phase 2 — Hardware and IoT

- Read measurements from an ESP32-based sensor node.
- Add suitable temperature and vibration sensing.
- Transmit readings using MQTT.
- Compare simulated readings with real sensor measurements.
- Track device status and communication failures.

### Phase 3 — Signal processing and AI

- Calculate descriptive statistics and signal features.
- Explore frequency-domain analysis using the Fast Fourier Transform (FFT) where the sensor and sampling rate support it.
- Establish a documented normal-operation baseline.
- Evaluate simple rule-based alerts against machine-learning anomaly detection.
- Record test data, false positives, false negatives, and evaluation limitations.

### Phase 4 — Security and energy analytics

- Authenticate devices and restrict dashboard/API access.
- Use encrypted communication when supported by the deployment environment.
- Validate incoming messages and maintain audit logs.
- Estimate energy use and cost from suitable, calibrated measurements.
- Optionally add low-voltage solar and battery telemetry.

### Phase 5 — Advanced extensions

- A stateful digital-twin model for each monitored device.
- Multi-device comparison and historical reports.
- A data-grounded AI assistant that explains alerts using stored readings and configured rules.
- Lightweight edge analytics on the microcontroller.
- A deployment and maintenance guide for reproducible demonstrations.

These items are a roadmap, not a claim that the functionality already exists.

---

## 🏗️ System architecture

```text
┌──────────────────────────────────────┐
│ Physical test rig or data simulator  │
│ Temperature · Vibration · RPM        │
│ Voltage/current when safely measured │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│ ESP32 edge device (later phase)      │
│ Acquisition · Filtering · Health     │
└──────────────────┬───────────────────┘
                   │ MQTT / validated data
                   ▼
┌──────────────────────────────────────┐
│ Python backend and data pipeline     │
│ FastAPI · Validation · Event logging │
└──────────────────┬───────────────────┘
                   │
          ┌────────┴─────────┐
          ▼                  ▼
┌─────────────────┐  ┌──────────────────┐
│ Storage         │  │ Analytics / ML   │
│ SQLite initially│  │ Rules · Features │
└────────┬────────┘  └─────────┬────────┘
         └──────────┬─────────┘
                    ▼
┌──────────────────────────────────────┐
│ Dashboard / digital-twin view        │
│ Telemetry · Trends · Alerts · Reports│
└──────────────────────────────────────┘
```

The initial milestone uses a simulator in place of the physical test rig. Each layer should have a clear interface so it can be tested independently.

---

## 🛠️ Proposed technology stack

| Layer | Planned tools | Purpose |
|---|---|---|
| Embedded firmware | C/C++, ESP32 | Sensor acquisition and basic edge processing |
| Hardware simulation | Wokwi or equivalent | Test embedded concepts before hardware is available |
| Backend | Python, FastAPI | API endpoints, validation, and application logic |
| Messaging | MQTT, Mosquitto | Telemetry transport when the hardware phase begins |
| Database | SQLite; PostgreSQL later if needed | Store readings, device metadata, and events |
| Data analysis | NumPy, pandas | Data cleaning, descriptive statistics, and features |
| Machine learning | scikit-learn | Baselines and exploratory anomaly detection |
| Frontend | HTML, CSS, JavaScript; React optionally | Monitoring dashboard |
| Security | TLS, authentication, authorization, audit logs | Protect devices and telemetry |
| Quality | pytest, Git, GitHub Actions | Automated tests and reproducible development |
| Deployment | Docker optionally | Consistent setup across environments |

Start with the minimum stack needed for the software MVP. Add a technology only when a specific requirement justifies it.

---

## 📊 Example telemetry format

The software simulator is expected to produce records similar to this example. These are illustrative values, not real sensor measurements.

```json
{
  "device_id": "motor-sim-01",
  "timestamp": "2026-10-29T12:00:00Z",
  "temperature_c": 34.8,
  "vibration_rms": 0.12,
  "rpm": 1450,
  "voltage_v": 12.0,
  "current_a": 0.65
}
```

Telemetry fields depend on the selected sensors. Missing or unavailable measurements should be represented explicitly rather than fabricated. Sensor units, calibration, sampling rate, and data quality should be documented.

---

## 🗂️ Suggested repository structure

```text
nexus-sentinel/
├── simulator/          # Synthetic telemetry generator
├── firmware/           # ESP32 firmware (later phase)
├── backend/            # API and application logic
├── ai/                 # Feature extraction and model experiments
├── dashboard/          # Frontend interface
├── tests/              # Unit and integration tests
├── data/               # Small, non-sensitive sample datasets
├── docs/               # Architecture, wiring, and test reports
├── .github/workflows/  # CI workflows
├── .gitignore
├── LICENSE
└── README.md
```

Keep generated datasets, API keys, passwords, private certificates, and other secrets out of version control. Do not commit personal or sensitive telemetry.

---

## 🚀 Getting started

The repository begins with a planned architecture, so the exact setup commands will be added as each component is implemented. The first development milestone is to:

1. Create the repository and folder structure.
2. Build a Python telemetry simulator.
3. Generate at least 100 valid sample readings.
4. Validate the schema and save the readings to CSV.
5. Add automated tests and document how to reproduce the output.
6. Connect the backend and dashboard only after the simulator output is reliable.

### Initial completion criteria

- [ ] The simulator produces at least 100 timestamped readings.
- [ ] Every record follows a documented schema.
- [ ] Invalid readings are detected and handled.
- [ ] The sample dataset can be regenerated from documented steps.
- [ ] Tests pass on the supported Python version.

---

## 🗺️ 12-week development roadmap

| Weeks | Focus | Deliverable |
|---|---|---|
| 1–2 | Python simulator, schema, API foundation | Reproducible sample telemetry and tests |
| 3–4 | Database and frontend | Dashboard backed by actual API/database data |
| 5–6 | ESP32 and sensors | Real readings visible in the dashboard |
| 7–8 | Signal processing and anomaly evaluation | Documented experiment and measured metrics |
| 9–10 | Security and energy analytics | Access controls, event logs, and initial energy reports |
| 11–12 | Integration and documentation | Reproducible demo, diagrams, testing report, and presentation |

This is a target plan, not a guarantee. Hardware availability, sensor quality, and college workload may affect the schedule.

---

## 🔐 Safety and security principles

- Start with a simulated device or a low-voltage DC test rig.
- Do not connect experimental electronics directly to mains electricity.
- Use correctly rated sensors and measurement modules; seek qualified supervision for electrical testing.
- Keep the early prototype observational. Do not let an unvalidated model directly operate hazardous machinery.
- Any later automatic control requires independent safeguards, safe-state behavior, and physical testing.
- Never test security controls against systems without authorization.
- Keep credentials and private keys out of source control.
- Validate, authenticate, and log device messages; do not trust telemetry merely because it arrives over the network.

---

## 📈 How success will be measured

The project should report evidence rather than only screenshots. Useful measurements include:

- **Data quality:** valid records received, missing readings, and malformed-message rejection.
- **Latency:** time from a reading entering the backend to its appearance on the dashboard.
- **Reliability:** communication dropouts and recovery behavior during controlled tests.
- **Anomaly detection:** precision, recall, false-alarm rate, and the test conditions used.
- **Energy analytics:** measurement method, calibration assumptions, and error compared with a reference meter where available.
- **Security:** documented authentication and authorization tests, including expected rejection of unauthorized requests.

Do not claim a result until the corresponding test has been run and documented.

---

## 💼 Potential product direction

A possible future customer is a small workshop, teaching laboratory, or maker space that wants basic monitoring without a complex industrial control system. Before treating this as a business, validate the problem with interviews and a simple demo.

Potential value proposition:

> Affordable machine-condition and energy visibility for small facilities, with transparent alerts and a reproducible, modular architecture.

Future business validation could include hardware cost, installation effort, maintenance needs, willingness to pay, and comparison with existing alternatives. No cost savings or commercial performance should be claimed until measured.

---

## 🤝 Contribution workflow

1. Open an issue describing the change or bug.
2. Make a focused branch and keep the change small.
3. Add or update tests when behavior changes.
4. Update documentation and units for any new telemetry field.
5. Submit a pull request with evidence from the tests or demo.

---

## 📚 Documentation to add

- System block diagram and data-flow diagram
- Wiring diagram and bill of materials for the selected sensors
- API specification and telemetry schema
- Dataset description and experiment methodology
- Model evaluation report, including limitations
- Security threat model and test results
- Setup guide, demo instructions, and troubleshooting notes
- Bill of materials and customer-discovery findings for any product prototype

---

## 📄 License

Choose a license before publishing. For example, MIT is often used for permissive open-source software, but confirm that it fits your intended distribution and any third-party dependencies. Do not imply that the project has a license until the license file is actually included.

---

**NEXUS SENTINEL — Measure first. Understand the data. Build safely. Improve with evidence.**
