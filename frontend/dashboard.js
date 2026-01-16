const totalEl = document.getElementById("total");
const ipsEl = document.getElementById("ips");
const statusEl = document.getElementById("status");

const ctx = document.getElementById("trafficChart").getContext("2d");

let trafficData = {
  labels: [],
  datasets: [{
    label: "Requests",
    data: [],
    borderColor: "#38bdf8",
    tension: 0.3
  }]
};

const chart = new Chart(ctx, {
  type: "line",
  data: trafficData,
  options: {
    scales: {
      x: { ticks: { color: "#9ca3af" } },
      y: { ticks: { color: "#9ca3af" } }
    },
    plugins: {
      legend: { display: false }
    }
  }
});

async function fetchMetrics() {
  const res = await fetch("http://localhost:8000/metrics");
  const data = await res.json();

  totalEl.textContent = data.total_requests;
  ipsEl.textContent = data.unique_ips;

  const now = new Date().toLocaleTimeString();
  trafficData.labels.push(now);
  trafficData.datasets[0].data.push(data.total_requests);

  if (trafficData.labels.length > 25) {
    trafficData.labels.shift();
    trafficData.datasets[0].data.shift();
  }

  chart.update();
}

async function fetchStatus() {
  const res = await fetch("http://localhost:8000/status");
  const data = await res.json();

  statusEl.textContent = data.state;
  statusEl.className = "status " + data.state.toLowerCase();
}

setInterval(() => {
  fetchMetrics();
  fetchStatus();
}, 1000);
