/**
 * SynaptForge Digital Twin & Industrial Telemetry Dashboard Controller
 */

(function () {
  // State variables
  let isRunning = true;
  let currentStep = 0;
  let totalEnergyJoules = 0;
  let recordCount = 0;
  let rotationAngle = 0;
  let streamTimer = null;
  let simulatedRecords = [];
  let currentMode = "mixed";

  // Rolling buffers for chart histories (last 30 samples)
  const maxHistory = 30;
  const history = {
    temp: [],
    vib: [],
    power: [],
  };

  // DOM Elements
  const playBtn = document.getElementById("togglePlayBtn");
  const playBtnLabel = document.getElementById("playBtnLabel");
  const injectFaultBtn = document.getElementById("injectFaultBtn");
  const modeSelect = document.getElementById("simulationMode");
  const connectionDot = document.getElementById("connectionDot");
  const connectionStatusText = document.getElementById("connectionStatusText");

  // Digital Twin Elements
  const rotatingCoupling = document.getElementById("twinRotatingCoupling");
  const thermalGlow = document.getElementById("twinThermalGlow");
  const vibWave = document.getElementById("twinVibWave");
  const assetBadge = document.getElementById("assetOverallBadge");

  const twinRpmVal = document.getElementById("twinRpmVal");
  const twinTempVal = document.getElementById("twinTempVal");
  const twinVibVal = document.getElementById("twinVibVal");

  // KPI elements
  const kpiPowerW = document.getElementById("kpiPowerW");
  const kpiEnergyKwh = document.getElementById("kpiEnergyKwh");
  const kpiZScore = document.getElementById("kpiZScore");
  const kpiRecordCount = document.getElementById("kpiRecordCount");
  const subVolt = document.getElementById("subVolt");
  const subCurr = document.getElementById("subCurr");
  const lastUpdatedTs = document.getElementById("lastUpdatedTs");

  // Alert elements
  const alertBanner = document.getElementById("activeAlertBanner");
  const alertHeading = document.getElementById("alertHeading");
  const alertDetail = document.getElementById("alertDetail");
  const alertIcon = document.getElementById("alertIcon");
  const eventsContainer = document.getElementById("eventsContainer");
  const eventCountBadge = document.getElementById("eventCountBadge");

  // Charts
  const tempCanvas = document.getElementById("tempCanvas");
  const vibCanvas = document.getElementById("vibCanvas");
  const powerCanvas = document.getElementById("powerCanvas");

  const metricTempVal = document.getElementById("metricTempVal");
  const metricVibVal = document.getElementById("metricVibVal");
  const metricPowerVal = document.getElementById("metricPowerVal");

  // Table
  const telemetryTbody = document.getElementById("telemetryTbody");

  let eventsList = [];

  // Physics Simulation Model for Browser Stream
  function generateSimulatedPoint(step, mode) {
    const baseTemp = 40.0;
    const baseVib = 0.16;
    const baseRpm = 1480.0;
    const baseVolt = 230.0;
    const baseCurr = 1.45;

    const oscillation = Math.sin(step * 0.15) * 0.9;
    let temp = baseTemp + (Math.random() - 0.5) * 0.8 + oscillation * 0.2;
    let vib = Math.max(0.04, baseVib + (Math.random() - 0.5) * 0.04 + Math.abs(oscillation) * 0.02);
    let rpm = baseRpm + (Math.random() - 0.5) * 6.0 + oscillation * 3.0;
    let volt = baseVolt + (Math.random() - 0.5) * 1.2;
    let curr = baseCurr + (Math.random() - 0.5) * 0.05;
    let status = "nominal";

    if (mode === "thermal_runaway") {
      const creep = Math.min(50.0, Math.pow(step % 60, 1.1) * 0.85);
      temp += creep;
      curr += creep * 0.02;
      status = temp > 72.0 ? "critical" : (temp > 54.0 ? "warning" : "nominal");
    } else if (mode === "bearing_fault") {
      const spike = 2.5 + Math.random() * 4.2;
      vib += spike;
      rpm -= 35.0;
      status = vib > 4.2 ? "critical" : "warning";
    } else if (mode === "voltage_sag") {
      const sag = 45.0 + Math.random() * 20.0;
      volt -= sag;
      curr += 1.35; // Compensatory current
      status = volt < 175.0 ? "critical" : "warning";
    } else if (mode === "mixed") {
      // Periodic mixed anomaly occurrences
      if (step > 15 && step % 30 in [0, 1, 2]) {
        vib += 2.8 + Math.random() * 2.0;
        status = "warning";
      } else if (step > 35 && step % 45 in [0, 1, 2, 3]) {
        temp += 24.0 + Math.random() * 12.0;
        status = temp > 70 ? "critical" : "warning";
      } else if (step > 50 && step % 50 === 0) {
        volt -= 50.0;
        curr += 1.4;
        status = "critical";
      }
    }

    const power = Number((volt * curr).toFixed(2));
    const now = new Date();
    const tsStr = now.toISOString().replace(/\.\d+Z$/, "Z");

    return {
      device_id: "synapt-motor-01",
      timestamp: tsStr,
      temperature_c: Number(temp.toFixed(2)),
      vibration_rms: Number(vib.toFixed(3)),
      rpm: Number(rpm.toFixed(1)),
      voltage_v: Number(volt.toFixed(1)),
      current_a: Number(curr.toFixed(2)),
      power_w: power,
      status: status,
    };
  }

  // Draw Smooth Sparkline Canvas
  function drawSparkline(canvas, data, strokeColor, fillColor, minBound, maxBound) {
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    if (data.length < 2) return;

    const min = minBound !== undefined ? minBound : Math.min(...data) * 0.95;
    const max = maxBound !== undefined ? maxBound : Math.max(...data) * 1.05;
    const range = (max - min) || 1;

    // Draw grid horizontal guideline
    ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, height * 0.5);
    ctx.lineTo(width, height * 0.5);
    ctx.stroke();

    // Plot data path
    ctx.beginPath();
    const stepX = width / (data.length - 1);

    data.forEach((val, i) => {
      const x = i * stepX;
      const normalized = (val - min) / range;
      const y = height - normalized * (height - 18) - 9;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });

    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = 2.2;
    ctx.stroke();

    // Area fill
    ctx.lineTo(width, height);
    ctx.lineTo(0, height);
    ctx.closePath();
    ctx.fillStyle = fillColor;
    ctx.fill();

    // Highlight latest point
    const latestVal = data[data.length - 1];
    const latestNormalized = (latestVal - min) / range;
    const latestY = height - latestNormalized * (height - 18) - 9;
    ctx.beginPath();
    ctx.arc(width - 2, latestY, 4, 0, Math.PI * 2);
    ctx.fillStyle = strokeColor;
    ctx.fill();
  }

  // Process and ingest incoming telemetry frame
  function processTelemetryFrame(frame) {
    recordCount++;
    currentStep++;

    // Accumulate active energy (Joules = Watts * delta_t (1 sec), 1 kWh = 3.6e6 Joules)
    totalEnergyJoules += frame.power_w * 1.0;
    const kwh = (totalEnergyJoules / 3600000).toFixed(4);

    // Update histories
    history.temp.push(frame.temperature_c);
    history.vib.push(frame.vibration_rms);
    history.power.push(frame.power_w);

    if (history.temp.length > maxHistory) history.temp.shift();
    if (history.vib.length > maxHistory) history.vib.shift();
    if (history.power.length > maxHistory) history.power.shift();

    // Update Digital Twin graphics
    rotationAngle = (rotationAngle + (frame.rpm / 60) * 36) % 360;
    if (rotatingCoupling) {
      rotatingCoupling.setAttribute("transform", `translate(370, 112) rotate(${rotationAngle})`);
    }

    // Thermal glow color & radius modulation
    if (thermalGlow) {
      if (frame.temperature_c > 70.0) {
        thermalGlow.setAttribute("fill", "rgba(239, 68, 68, 0.45)");
        thermalGlow.setAttribute("rx", "135");
      } else if (frame.temperature_c > 52.0) {
        thermalGlow.setAttribute("fill", "rgba(245, 158, 11, 0.32)");
        thermalGlow.setAttribute("rx", "125");
      } else {
        thermalGlow.setAttribute("fill", "rgba(6, 182, 212, 0.15)");
        thermalGlow.setAttribute("rx", "110");
      }
    }

    // Vibration wave visual ripple
    if (vibWave) {
      if (frame.vibration_rms > 1.8) {
        const jitter = (Math.random() - 0.5) * 8;
        vibWave.setAttribute("stroke", frame.vibration_rms > 4.0 ? "rgba(239, 68, 68, 0.85)" : "rgba(245, 158, 11, 0.75)");
        vibWave.setAttribute("transform", `translate(${jitter}, 0)`);
      } else {
        vibWave.setAttribute("stroke", "rgba(245, 158, 11, 0)");
      }
    }

    // Update Readouts
    twinRpmVal.textContent = `${Math.round(frame.rpm).toLocaleString()} RPM`;
    twinTempVal.textContent = `${frame.temperature_c.toFixed(1)} °C`;
    twinVibVal.textContent = `${frame.vibration_rms.toFixed(2)} mm/s`;

    // Asset status badge
    assetBadge.className = `asset-badge ${frame.status}`;
    assetBadge.textContent = frame.status.toUpperCase();

    // Update KPIs
    kpiPowerW.textContent = frame.power_w.toFixed(1);
    kpiEnergyKwh.textContent = kwh;
    subVolt.textContent = `${frame.voltage_v.toFixed(1)}V`;
    subCurr.textContent = `${frame.current_a.toFixed(2)}A`;
    kpiRecordCount.textContent = recordCount;
    lastUpdatedTs.textContent = frame.timestamp.split("T")[1] || "--:--:--";

    // Statistical Z-score calculation
    const tempZ = Math.abs(frame.temperature_c - 41.5) / 3.2;
    const vibZ = Math.abs(frame.vibration_rms - 0.16) / 0.08;
    const voltZ = Math.abs(frame.voltage_v - 230.0) / 4.5;
    const maxZ = Math.max(tempZ, vibZ, voltZ).toFixed(2);
    kpiZScore.textContent = maxZ;

    // Update Alert Banner
    if (frame.status === "critical") {
      alertBanner.className = "active-alert-box alert-crit";
      alertIcon.textContent = "!";
      alertHeading.textContent = "CRITICAL: Operational threshold exceeded!";
      alertDetail.textContent = `High deviation detected (Z-Score: ${maxZ}σ). Inspect asset diagnostics immediately.`;
      addEventEntry("Critical Anomaly Alert", `T: ${frame.temperature_c}°C, Vib: ${frame.vibration_rms}mm/s, V: ${frame.voltage_v}V`, "critical", frame.timestamp);
    } else if (frame.status === "warning") {
      alertBanner.className = "active-alert-box alert-warn";
      alertIcon.textContent = "▲";
      alertHeading.textContent = "WARNING: Baseline parameter drift detected.";
      alertDetail.textContent = `Telemetry is approaching ISO advisory tolerance bounds (Z-Score: ${maxZ}σ).`;
      addEventEntry("Warning Parameter Drift", `Readings drifted past standard baseline.`, "warning", frame.timestamp);
    } else {
      alertBanner.className = "active-alert-box";
      alertIcon.textContent = "✓";
      alertHeading.textContent = "All subsystems operating within calibrated baselines.";
      alertDetail.textContent = "ISO 10816-1 vibration class I & thermal parameters nominal.";
    }

    // Metric Header Values
    metricTempVal.textContent = `${frame.temperature_c.toFixed(1)} °C`;
    metricVibVal.textContent = `${frame.vibration_rms.toFixed(2)} mm/s`;
    metricPowerVal.textContent = `${frame.power_w.toFixed(1)} W`;

    // Render Canvas Sparklines
    const tempColor = frame.temperature_c > 55 ? "#f59e0b" : "#06b6d4";
    const vibColor = frame.vibration_rms > 1.8 ? "#ef4444" : "#10b981";
    const powerColor = frame.power_w > 450 ? "#f59e0b" : "#8b5cf6";

    drawSparkline(tempCanvas, history.temp, tempColor, "rgba(6, 182, 212, 0.08)", 30, 90);
    drawSparkline(vibCanvas, history.vib, vibColor, "rgba(16, 185, 129, 0.08)", 0, 7.5);
    drawSparkline(powerCanvas, history.power, powerColor, "rgba(139, 92, 246, 0.08)", 150, 650);

    // Append to live feed table (keep max 10 rows in DOM)
    const row = document.createElement("tr");
    const timeOnly = frame.timestamp.includes("T") ? frame.timestamp.split("T")[1].replace("Z", "") : frame.timestamp;
    row.innerHTML = `
      <td>${timeOnly}</td>
      <td>${frame.temperature_c.toFixed(1)}</td>
      <td>${frame.vibration_rms.toFixed(2)}</td>
      <td>${Math.round(frame.rpm)}</td>
      <td>${frame.voltage_v.toFixed(1)}</td>
      <td>${frame.current_a.toFixed(2)}</td>
      <td>${frame.power_w.toFixed(1)}</td>
      <td><span class="status-badge-inline status-${frame.status}">${frame.status}</span></td>
    `;
    telemetryTbody.insertBefore(row, telemetryTbody.firstChild);
    if (telemetryTbody.children.length > 12) {
      telemetryTbody.removeChild(telemetryTbody.lastChild);
    }
  }

  function addEventEntry(title, desc, severity, timestamp) {
    // Avoid spamming consecutive identical warnings
    if (eventsList.length > 0 && eventsList[0].title === title && (Date.now() - eventsList[0].time) < 4000) {
      return;
    }

    const event = { title, desc, severity, timestamp, time: Date.now() };
    eventsList.unshift(event);
    if (eventsList.length > 25) eventsList.pop();

    eventCountBadge.textContent = `${eventsList.length} Events`;

    const entry = document.createElement("div");
    entry.className = `event-entry ${severity}`;
    const timeShort = timestamp.split("T")[1] || timestamp;
    entry.innerHTML = `
      <span class="event-time">${timeShort}</span>
      <span class="event-msg">${title}: ${desc}</span>
      <span class="event-tag status-badge-inline status-${severity}">${severity}</span>
    `;

    if (eventsContainer.querySelector(".empty-state")) {
      eventsContainer.innerHTML = "";
    }
    eventsContainer.insertBefore(entry, eventsContainer.firstChild);
  }

  // Simulation tick
  function tick() {
    if (!isRunning) return;
    const frame = generateSimulatedPoint(currentStep, currentMode);
    processTelemetryFrame(frame);
  }

  // Start stream interval
  function startStream() {
    if (streamTimer) clearInterval(streamTimer);
    streamTimer = setInterval(tick, 1000);
    connectionDot.classList.add("pulsing");
    connectionStatusText.textContent = "SIMULATOR ACTIVE";
    playBtnLabel.textContent = "Pause Stream";
  }

  function pauseStream() {
    if (streamTimer) clearInterval(streamTimer);
    streamTimer = null;
    connectionDot.classList.remove("pulsing");
    connectionStatusText.textContent = "PAUSED";
    playBtnLabel.textContent = "Resume Stream";
  }

  // Event Listeners
  playBtn.addEventListener("click", () => {
    isRunning = !isRunning;
    if (isRunning) startStream();
    else pauseStream();
  });

  modeSelect.addEventListener("change", (e) => {
    currentMode = e.target.value;
    addEventEntry("Simulation Mode Switched", `Switched operational mode to '${currentMode}'.`, "nominal", new Date().toISOString());
  });

  injectFaultBtn.addEventListener("click", () => {
    // Injects an immediate severe harmonic bearing + thermal fault burst
    const burstFrame = {
      device_id: "synapt-motor-01",
      timestamp: new Date().toISOString(),
      temperature_c: 84.5,
      vibration_rms: 6.82,
      rpm: 1410.0,
      voltage_v: 215.0,
      current_a: 2.85,
      power_w: 612.75,
      status: "critical",
    };
    processTelemetryFrame(burstFrame);
  });

  // Preload initial buffer
  for (let i = 0; i < 8; i++) {
    tick();
  }
  startStream();
})();
