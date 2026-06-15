# POG RTIP — Real-Time Intelligence Platform
### Paul Oil & Gas | Streamlit Dashboard

A 6-page professional Streamlit dashboard connecting to a Databricks Gold Layer for real-time operational intelligence across your fuel station network.

---

## Project Structure

```
streamlit_app/
├── app.py                          # Main entry point + navigation
├── requirements.txt
├── .streamlit/
│   ├── config.toml                 # Dark theme + server config
│   └── secrets.toml.template       # Credentials template
├── utils/
│   ├── __init__.py
│   ├── databricks.py               # Query runner (cached 60s)
│   └── charts.py                   # Shared Plotly theme + formatters
└── pages/
    ├── __init__.py
    ├── p1_executive.py             # Page 1 — Executive Command Center
    ├── p2_revenue.py               # Page 2 — Revenue & Sales Analytics
    ├── p3_inventory.py             # Page 3 — Inventory & Tank Monitoring
    ├── p4_fraud.py                 # Page 4 — Fraud & Loss Monitoring
    ├── p5_pump.py                  # Page 5 — Pump Health & Maintenance
    └── p6_station360.py            # Page 6 — Station 360° & Nigeria Network Map
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Databricks credentials

```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`:

```toml
DATABRICKS_HOST      = "your-workspace.azuredatabricks.net"
DATABRICKS_HTTP_PATH = "/sql/1.0/warehouses/your-warehouse-id"
DATABRICKS_TOKEN     = "dapi-your-personal-access-token"
```

> ⚠️ Never commit `secrets.toml` to Git. Add it to `.gitignore`.

### 3. Run the dashboard

```bash
streamlit run app.py
```

---

## Data Sources

| Layer  | Catalog                                            | Tables Used                                                                                         |
|--------|---------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| Gold   | `workspace.pog_rtip_bronze_pog_rtip_gold`        | gold_executive_command_center, gold_sales_daily, gold_sales_hourly, gold_station_revenue, gold_attendant_performance, gold_inventory_position, gold_tank_utilization, gold_stockout_risk, gold_fraud_events, gold_fraud_losses, gold_fraud_station_ranking, gold_fraud_attendants, gold_pump_health, gold_failure_risk, gold_maintenance_scores |
| Silver | `workspace.pog_rtip_bronze_pog_rtip_silver`      | silver_stations                                                                                     |

---

## Dashboard Pages

| Page | Title | Key Features |
|------|-------|-------------|
| 1 | Executive Command Center | KPI cards, dual-axis trend, top/bottom stations, fraud pulse |
| 2 | Revenue & Sales Analytics | Stacked fuel-type trend, hourly pattern, attendant scatter |
| 3 | Inventory & Tank Monitoring | Network gauge, stockout donut, utilisation heatmap, low-tank alerts |
| 4 | Fraud & Loss Monitoring | Daily fraud trend, state×fuel heatmap, violin variance, attendant ranking |
| 5 | Pump Health & Maintenance | Health histogram, IoT scatter matrix, state maintenance bar, alert table |
| 6 | Station 360° & Nigeria Map | Scatter mapbox, state density bubbles, per-station deep-dive |

---

## Key Design Decisions

- **60-second cache** via `@st.cache_data(ttl=60)` — balances freshness vs Databricks cost
- **Dark theme** (`#060d1f` base, `#f97316` orange accent) — professional O&G aesthetic
- **Mapbox (carto-darkmatter)** — no API key required for this style
- **Nigeria state centroids** hardcoded as fallback when GeoJSON not available
- All queries go through `utils/databricks.py` — swap to any connector easily
