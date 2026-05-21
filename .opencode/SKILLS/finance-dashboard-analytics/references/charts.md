# Chart.js Implementation Reference

Chart.js v3+ syntax throughout. All charts use the canonical `CATEGORY_COLORS` map.

---

## 0. Shared Setup (put once at top of script block)

```js
const CATEGORY_COLORS = {
  "Food":          "#FF6384",
  "Transport":     "#36A2EB",
  "Bills":         "#FFCE56",
  "Health":        "#4BC0C0",
  "Movie tickets": "#9966FF",
  "Shopping":      "#FF9F40",
  "Other":         "#C9CBCF"
};

function gbpTooltip(context) {
  return ` £${parseFloat(context.parsed.y ?? context.parsed).toFixed(2)}`;
}
```

---

## 1. Horizontal Bar Chart — Spending by Category

```html
<div style="position:relative; height:300px;">
  <canvas id="categoryBarChart"></canvas>
</div>
```

```js
const catData  = CHART_DATA.category_totals; // { "Food": 120.5, ... }
const catLabels = Object.keys(catData);
const catValues = Object.values(catData);
const catColors = catLabels.map(l => CATEGORY_COLORS[l] || "#C9CBCF");

new Chart(document.getElementById("categoryBarChart"), {
  type: "bar",
  data: {
    labels: catLabels,
    datasets: [{
      label: "Total Spent",
      data: catValues,
      backgroundColor: catColors,
      borderRadius: 6,
    }]
  },
  options: {
    indexAxis: "y",           // ← makes it horizontal
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: ctx => ` £${ctx.parsed.x.toFixed(2)}`
        }
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        ticks: { callback: v => `£${v}` }
      }
    }
  }
});
```

---

## 2. Pie Chart — Category Share (%)

```html
<div style="position:relative; height:300px;">
  <canvas id="categoryPieChart"></canvas>
</div>
```

```js
const pieLabels = Object.keys(catData);
const pieValues = Object.values(catData);
const pieColors = pieLabels.map(l => CATEGORY_COLORS[l] || "#C9CBCF");
const pieTotal  = pieValues.reduce((a, b) => a + b, 0);

new Chart(document.getElementById("categoryPieChart"), {
  type: "pie",
  data: {
    labels: pieLabels,
    datasets: [{
      data: pieValues,
      backgroundColor: pieColors,
      borderWidth: 2,
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: "right" },
      tooltip: {
        callbacks: {
          label: ctx => {
            const pct = ((ctx.parsed / pieTotal) * 100).toFixed(1);
            return ` ${ctx.label}: £${ctx.parsed.toFixed(2)} (${pct}%)`;
          }
        }
      }
    }
  }
});
```

---

## 3. Vertical Bar Chart — Time Series with Toggle + Timeline Overlay

### HTML (button group + canvas)

```html
<div class="btn-group mb-2" role="group" id="periodToggle">
  <button type="button" class="btn btn-sm btn-primary"   data-period="weekly">Weekly</button>
  <button type="button" class="btn btn-sm btn-outline-primary" data-period="monthly">Monthly</button>
  <button type="button" class="btn btn-sm btn-outline-primary" data-period="yearly">Yearly</button>
</div>

<div class="form-check form-switch mb-2">
  <input class="form-check-input" type="checkbox" id="timelineToggle">
  <label class="form-check-label" for="timelineToggle">Show Trend Line</label>
</div>

<div style="position:relative; height:320px;">
  <canvas id="timeSeriesChart"></canvas>
</div>
```

### JS

```js
// CHART_DATA.weekly  = [ { period: "2025-W01", total: 210.5 }, ... ]
// CHART_DATA.monthly = [ { period: "2025-01", total: 890.0 }, ... ]
// CHART_DATA.yearly  = [ { period: "2024", total: 3200.0 }, ... ]

function buildTimeDatasets(rows, showLine) {
  const labels = rows.map(r => r.period);
  const values = rows.map(r => r.total);

  // Running total for trend line
  let running = 0;
  const trend = values.map(v => { running += v; return running; });

  const datasets = [{
    label: "Spending",
    data: values,
    backgroundColor: "#36A2EB",
    borderRadius: 6,
    order: 2,
  }];

  if (showLine) {
    datasets.push({
      label: "Cumulative",
      data: trend,
      type: "line",
      borderColor: "#FF6384",
      backgroundColor: "rgba(255,99,132,0.1)",
      fill: true,
      tension: 0.3,
      pointRadius: 3,
      order: 1,
    });
  }

  return { labels, datasets };
}

let currentPeriod = "weekly";
let showTrend = false;

const tsCtx = document.getElementById("timeSeriesChart");
const { labels, datasets } = buildTimeDatasets(CHART_DATA[currentPeriod], showTrend);

const timeSeriesChart = new Chart(tsCtx, {
  type: "bar",
  data: { labels, datasets },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      tooltip: {
        callbacks: { label: ctx => ` £${ctx.parsed.y.toFixed(2)}` }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { callback: v => `£${v}` }
      }
    }
  }
});

// Period toggle
document.getElementById("periodToggle").addEventListener("click", e => {
  const btn = e.target.closest("[data-period]");
  if (!btn) return;
  currentPeriod = btn.dataset.period;

  // Update button styles
  document.querySelectorAll("#periodToggle [data-period]").forEach(b => {
    b.classList.toggle("btn-primary", b === btn);
    b.classList.toggle("btn-outline-primary", b !== btn);
  });

  const { labels, datasets } = buildTimeDatasets(CHART_DATA[currentPeriod], showTrend);
  timeSeriesChart.data.labels = labels;
  timeSeriesChart.data.datasets = datasets;
  timeSeriesChart.update();
});

// Timeline overlay toggle
document.getElementById("timelineToggle").addEventListener("change", e => {
  showTrend = e.target.checked;
  const { labels, datasets } = buildTimeDatasets(CHART_DATA[currentPeriod], showTrend);
  timeSeriesChart.data.labels = labels;
  timeSeriesChart.data.datasets = datasets;
  timeSeriesChart.update();
});
```

---

## 4. KPI Cards (Jinja2 + Python)

### Python (in route handler)

```python
cursor.execute("""
  SELECT AVG(amount), MAX(amount), MIN(amount), SUM(amount)
  FROM expenses WHERE user_id = ?
""", (user_id,))
row = cursor.fetchone()
stats = {
    "avg": round(row[0] or 0, 2),
    "max": round(row[1] or 0, 2),
    "min": round(row[2] or 0, 2),
    "total": round(row[3] or 0, 2),
}
```

### HTML

```html
<div class="row g-3 mb-4">
  {% for label, key, icon in [
    ("Total Spent",   "total", "💰"),
    ("Avg per Entry", "avg",   "📊"),
    ("Highest",       "max",   "📈"),
    ("Lowest",        "min",   "📉"),
  ] %}
  <div class="col-6 col-md-3">
    <div class="card text-center shadow-sm h-100">
      <div class="card-body py-3">
        <div class="fs-4">{{ icon }}</div>
        <div class="text-muted small fw-semibold">{{ label }}</div>
        <div class="fw-bold fs-5 mt-1">£{{ "%.2f"|format(stats[key]) }}</div>
      </div>
    </div>
  </div>
  {% endfor %}
</div>
```

---

## Empty State Guard

Always wrap chart init in a guard:

```js
if (!CHART_DATA || !CHART_DATA.category_totals || Object.keys(CHART_DATA.category_totals).length === 0) {
  document.getElementById("analyticsSection").innerHTML =
    `<div class="text-center text-muted py-5">No expenses yet — add some to see analytics.</div>`;
} else {
  // initialise all charts
}
```