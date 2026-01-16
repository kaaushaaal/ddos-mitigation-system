# 🛡️ DDoS Detection & Mitigation System (Application Layer)

A real-time **application-layer DDoS detection and mitigation system** built to demonstrate how backend services detect abnormal traffic patterns and protect user-facing applications under load.

This project simulates realistic attack behavior, learns normal traffic baselines, detects anomalies statistically, and applies adaptive rate limiting to maintain availability.

---

## 🚀 Problem Statement

Many real-world outages are caused not by massive bandwidth floods, but by **application-layer DDoS attacks** where traffic appears legitimate yet arrives at abnormal rates.

This project focuses on:
- Learning normal traffic behavior automatically
- Detecting statistically significant anomalies
- Mitigating attacks early without taking the service offline
- Visualizing system behavior in real time

---

## 🧠 High-Level Architecture
```
              ┌────────────────────────┐
              │   Traffic Generator     │
              │  (Attack Simulation)    │
              └───────────┬────────────┘
                          │
                          ▼
┌───────────────┐   ┌───────────────┐   ┌────────────────────┐
│ Monitoring UI │◄──│  FastAPI App  │──▶│ Rate Limiter       │
│ (Dashboard)   │   │ (Protected    │   │ (Mitigation Layer) │
└───────────────┘   │  Service)     │   └────────────────────┘
                    │       │       │
                    │       ▼       │
                    │    Detection  │
                    │    Engine     │
                    │ (Baseline +   │
                    │      Stats)   │
                    └───────────────┘
```
---

## 🔍 Core Components

### Protected Application (HooliChat)
A realistic SaaS-style login page served by FastAPI that represents a production service under attack.

- Continues to function during attacks
- Displays warnings when traffic anomalies are detected
- Serves as the protected resource

Endpoint:
```
http://localhost:8000/
```

---

### Traffic Monitoring
The backend continuously tracks:
- Total request count
- Requests per IP
- Requests per time window

Metrics are exposed via API and consumed by the dashboard.

Endpoint:
```
http://localhost:8000/metrics
```

---

### Baseline Learning
Instead of hardcoded thresholds, the system:
- Groups traffic into fixed time windows
- Stores request counts per window
- Computes mean and standard deviation dynamically
- Adapts as usage patterns change

This reduces false positives and mirrors real-world anomaly detection.

---

### Detection Engine
Each traffic window is evaluated against the learned baseline.

System states:
- LEARNING – insufficient data
- NORMAL – expected behavior
- SUSPICIOUS – elevated traffic
- ATTACK – statistically significant anomaly

Endpoint:
```
http://localhost:8000/status
```

---

### Mitigation Layer
Adaptive rate limiting is applied per IP using a token bucket algorithm.

Key design choice:
Mitigation may activate **before** global attack classification to reduce blast radius early.

Blocked requests receive HTTP 429 responses while the service remains available.

---

### Monitoring Dashboard
A SOC-style dashboard visualizes:
- Live request counts
- Unique IPs
- Traffic trends
- Current system state

Endpoint:
```
http://localhost:5500/index.html
```

---

## ⚔️ Attack Simulation

A controlled HTTP flood generator simulates burst-style attacks:
- Fixed number of requests
- High concurrency
- Silent execution (errors only)

This validates detection and mitigation logic without unethical behavior.

Script:
```
attack/http_flood.py
```

---

## 🧪 Demo Behavior

### Detection-Focused Mode
- Rate limiting disabled
- Full traffic reaches the application
- Detection engine classifies ATTACK
- Dashboard turns red

### Mitigation-Focused Mode (Production-like)
- Rate limiting enabled
- Excess traffic blocked early
- Service remains responsive
- Detection may not escalate due to reduced throughput

This trade-off reflects real-world systems.

---

## 🏗️ Project Structure

```
ddos-mitigation-system/
├── backend/
│   ├── app/
│   ├── detection/
│   ├── mitigation/
│   ├── baseline/
│   ├── storage/
│   └── static/
├── frontend/
├── attack/
├── README.md
└── .gitignore
```

---

## ▶️ Running Locally

Backend:
```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Dashboard:
Open `frontend/index.html` using a static server.

Attack simulation:
```
python attack/http_flood.py
```

---

## ⚖️ Ethical Disclaimer

This project is strictly for educational and local testing purposes.
Never run traffic generation tools against systems you do not own or control.

---

## 🎯 What This Demonstrates

- Application-layer DDoS defense
- Statistical anomaly detection
- Adaptive rate limiting
- Real-time observability
- Security engineering trade-offs

---

## 🧩 Future Improvements

- Detection based on allowed + blocked traffic
- Multi-source attack simulation
- Cloud deployment with CDN/WAF integration
- Historical attack analysis

---

## 🙌 Final Note

This project emphasizes **engineering judgment and system design**, not brute-force attack power.
It reflects how real backend, SRE, and security teams reason about availability and protection.
