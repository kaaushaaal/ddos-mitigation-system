from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict
from baseline.learner import save_window, compute_baseline
from detection.detector import detect_attack
from mitigation.rate_limiter import is_allowed
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import threading
import time
from storage.db import init_db



init_db()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ CORS (allow frontend to call backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OK for local demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

metrics = {
    "total_requests": 0,
    "per_ip": defaultdict(int),
    "timestamps": []
}

rolling_counter = {
    "last_check": time.time(),
    "count": 0
}


system_status = {
    "state": "LEARNING",
    "last_window": 0
}

WINDOW = 5

def baseline_worker():
    last_total = 0
    while True:
        time.sleep(WINDOW)
        current_total = metrics["total_requests"]
        window_count = current_total - last_total
        last_total = current_total

        save_window(window_count)

        state = detect_attack(window_count)
        system_status["state"] = state
        system_status["last_window"] = window_count

        baseline = compute_baseline()
        if baseline:
            print(
                f"[BASELINE] mean={baseline['mean']:.2f} "
                f"std={baseline['std']:.2f} "
                f"samples={baseline['samples']} "
                f"state={state}"
    )


threading.Thread(target=baseline_worker, daemon=True).start()


@app.middleware("http")
async def collect_metrics(request: Request, call_next):
    ip = request.client.host

    #  Rate limit check
    #if not is_allowed(ip, system_status["state"]):
    #    return JSONResponse(
    #       status_code=429,
    #        content={"detail": "Rate limit exceeded"}
    #   )

    metrics["total_requests"] += 1
    metrics["per_ip"][ip] += 1
    metrics["timestamps"].append(time.time())
    rolling_counter["count"] += 1

    response = await call_next(request)
    return response

@app.get("/", response_class=HTMLResponse)
def hoolichat_login():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>HooliChat | Login</title>

  <style>
    * {
      box-sizing: border-box;
      font-family: Inter, Arial, sans-serif;
    }

    body {
      margin: 0;
      background: linear-gradient(135deg, #020617, #020617);
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #e5e7eb;
    }

    .container {
      display: flex;
      width: 900px;
      max-width: 95%;
      background: #020617;
      border-radius: 14px;
      overflow: hidden;
      box-shadow: 0 20px 60px rgba(0,0,0,0.6);
    }

    .left {
      flex: 1;
      background: linear-gradient(160deg, #2563eb, #1e40af);
      padding: 50px;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    .left h1 {
      font-size: 36px;
      margin-bottom: 10px;
    }

    .left p {
      font-size: 16px;
      line-height: 1.6;
      color: #e0e7ff;
    }

    .badge {
      margin-top: 20px;
      display: inline-block;
      padding: 6px 12px;
      background: rgba(0,0,0,0.25);
      border-radius: 999px;
      font-size: 13px;
      width: fit-content;
    }

    .right {
      flex: 1;
      padding: 50px;
      background: #020617;
    }

    .right h2 {
      margin-bottom: 20px;
      font-size: 22px;
    }

    .input-group {
      margin-bottom: 15px;
    }

    .input-group label {
      font-size: 13px;
      color: #9ca3af;
      display: block;
      margin-bottom: 6px;
    }

    .input-group input {
      width: 100%;
      padding: 12px;
      border-radius: 8px;
      border: 1px solid #1f2937;
      background: #020617;
      color: #e5e7eb;
      font-size: 14px;
    }

    .input-group input:focus {
      outline: none;
      border-color: #2563eb;
    }

    .login-btn {
      margin-top: 20px;
      width: 100%;
      padding: 12px;
      background: #2563eb;
      border: none;
      border-radius: 8px;
      color: white;
      font-size: 15px;
      font-weight: bold;
      cursor: pointer;
    }

    .login-btn:hover {
      background: #1d4ed8;
    }

    .footer {
      margin-top: 20px;
      font-size: 13px;
      color: #6b7280;
      text-align: center;
    }

    .attack-banner {
      display: none;
      margin-bottom: 15px;
      padding: 10px;
      background: rgba(239,68,68,0.15);
      color: #ef4444;
      border-radius: 8px;
      font-size: 14px;
      text-align: center;
    }
  </style>
</head>

<body>

  <div class="container">

    <div class="left">
      <div style="display: flex; align-items: center; gap: 12px;">
            <img src="/static/logo.png"
            alt="HooliChat"
            style="height: 175px;" />
        </div>
      <p>
        Secure real-time messaging for teams that care about privacy,
        reliability, and performance.
      </p>
      <div class="badge">🛡️ Protected by DDoS Mitigation</div>
    </div>

    <div class="right">
      <div id="attackBanner" class="attack-banner">
        ⚠️ High traffic detected. Login may be temporarily rate limited.
      </div>

      <h2>Sign in to your account</h2>

      <div class="input-group">
        <label>Email</label>
        <input type="email" placeholder="you@hoolichat.com" />
      </div>

      <div class="input-group">
        <label>Password</label>
        <input type="password" placeholder="••••••••" />
      </div>

      <button class="login-btn">Login</button>

      <div class="footer">
        © 2026 HooliChat Inc. All rights reserved.
      </div>
    </div>

  </div>

  <script>
    async function checkStatus() {
      try {
        const res = await fetch("http://localhost:8000/status");
        const data = await res.json();

        if (data.state === "ATTACK") {
          document.getElementById("attackBanner").style.display = "block";
        } else {
          document.getElementById("attackBanner").style.display = "none";
        }
      } catch (e) {}
    }

    setInterval(checkStatus, 2000);
  </script>

</body>
</html>
"""


@app.get("/metrics")
def metrics_view():
    return {
        "total_requests": metrics["total_requests"],
        "unique_ips": len(metrics["per_ip"]),
        "top_ips": dict(list(metrics["per_ip"].items())[:5])
    }

@app.get("/status")
def status():
    return system_status
