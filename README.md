# 🏗️ Freeway M365 Enterprise Dashboard

An interactive analytics dashboard built with **Streamlit** and **Plotly** for monitoring workforce, security, and operations across Freeway's Saudi Arabia construction projects.

---

## 📸 Dashboard Overview

| Tab | Focus |
|-----|-------|
| 📊 Executive Overview | KPIs, daily sign-in trends, status & risk distribution |
| 🔐 Security & Identity | Failures by role, risk over time, risky apps, device OS |
| 👷 Workforce Analytics | Nationality, role, city, project headcount, camp utilization |
| 🏗️ Projects & Sites | Budget comparison, interactive site map, project rankings |
| 📈 Sign-in Activity | Heatmap, hourly patterns, top users, status over time |

---

## 🗂️ Project Structure

```
freeway_ent/
├── dashboard.py                        # Main Streamlit application
├── freeway_m365_enterprise_simulator.py  # Dataset generator
├── freeway_m365_dataset/
│   ├── bronze/                         # Raw CSV source files (28 tables)
│   ├── silver/                         # Cleaned Parquet files
│   └── gold/                           # Dimensional model (star schema)
│       ├── dim_camp.parquet
│       ├── dim_device.parquet
│       ├── dim_equipment.parquet
│       ├── dim_material.parquet
│       ├── dim_project.parquet
│       ├── dim_site.parquet
│       ├── dim_user.parquet
│       ├── dim_vehicle.parquet
│       ├── fact_daily_signins.parquet
│       └── fact_signin.parquet
├── freeway.ipynb
├── freeway2.ipynb
├── freeway_gold_data_analysis.ipynb
└── README.md
```

---

## 🧱 Data Model (Gold Layer)

### Dimension Tables

| Table | Rows | Key Columns |
|-------|------|-------------|
| `dim_user` | 10,000 | user_id, name, nationality, role, site_city, camp_id, project_id, visa_expiry_date |
| `dim_project` | 50 | project_id, project_name, budget_usd |
| `dim_site` | 75 | site_id, site_name, latitude, longitude |
| `dim_camp` | 20 | camp_id, camp_name, capacity |
| `dim_device` | 12,000 | device_id, device_name, os |
| `dim_equipment` | 50 | equipment_id, equipment_name, category |
| `dim_material` | 100 | material_id, material_name, unit |
| `dim_vehicle` | 200 | vehicle_id, plate_number, type |

### Fact Tables

| Table | Rows | Key Columns |
|-------|------|-------------|
| `fact_signin` | 500,000 | signin_id, user_id, device_id, timestamp, status, risk_level, application |
| `fact_daily_signins` | 467,187 | user_id, date, signin_count |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip

### Install Dependencies

```bash
pip install streamlit pandas plotly pyarrow
```

### Run the Dashboard

```bash
# From the freeway_ent directory
python -m streamlit run dashboard.py
```

Then open your browser at **http://localhost:8501**

---

## 📊 Dashboard Features

### 📊 Tab 1 — Executive Overview
- **6 KPI cards**: Total Users, Total Sign-ins, Failure Rate %, Critical Risk %, Active Projects, Total Budget (USD)
- **Daily sign-in trend** with 7-day rolling average overlay
- **Sign-in status donut** chart (Success vs Failure)
- **Risk level bar chart** (Low / Medium / High / Critical)

### 🔐 Tab 2 — Security & Identity
- Sign-in **failures by role** (horizontal bar)
- **Risk level distribution over time** (stacked area by month)
- **Top risky applications** (High + Critical sign-ins)
- **Failure rate by nationality** (%)
- **Device OS breakdown** (pie chart)

### 👷 Tab 3 — Workforce Analytics
- **Workforce by nationality** (donut chart)
- **Headcount by role** (horizontal bar)
- **Workforce by site city** (bar — Jeddah, Dammam, Riyadh, NEOM)
- **Top 10 projects by user count**
- **Camp capacity utilization** (overlay bar: capacity vs residents)

### 🏗️ Tab 4 — Projects & Sites
- **Project budget comparison** (all 50 projects, sorted by budget)
- **Interactive site map** (scatter_mapbox on dark carto basemap, Saudi Arabia)
- **Top projects by assigned users**
- **Site details table**

### 📈 Tab 5 — Sign-in Activity
- **Monthly sign-in heatmap** (month × day of month)
- **Sign-ins by application over time** (multi-line by month)
- **Hourly sign-in pattern** (24-hour bar chart)
- **Top 10 most active users** (colored by role)
- **Sign-in status stacked bar** over time (Success vs Failure)

---

## 🎛️ Sidebar Filters

All filters apply globally across every tab:

| Filter | Type | Applies To |
|--------|------|------------|
| 📅 Date Range | Date picker (From / To) | fact_daily_signins, sign-in activity |
| 👷 Role | Multiselect | dim_user, fact_signin |
| 🌍 Nationality | Multiselect | dim_user, fact_signin |
| 🏙️ Site City | Multiselect | dim_user |

---

## 🎨 Design System

| Element | Value |
|---------|-------|
| Background | `#0d1117` (GitHub dark) |
| Card surface | `#161b22` |
| Border | `#30363d` |
| Accent blue | `#58a6ff` |
| Success green | `#3fb950` |
| Warning amber | `#d29922` |
| Critical red | `#f85149` |
| Chart theme | `plotly_dark` |
| Color palette | `px.colors.qualitative.Bold` |

---

## 🏢 Business Context

The dataset simulates a large construction enterprise operating across **4 Saudi cities** (Jeddah, Dammam, Riyadh, NEOM) with:

- **10,000 employees** across 9 roles (Engineer, Foreman, Labor, HR, Finance, Executive, Project Manager, Supervisor, Procurement)
- **7 nationalities** (Pakistan, Bangladesh, India, Nepal, Egypt, Sri Lanka, Saudi Arabia)
- **50 active projects** with budgets ranging from ~$2M to ~$50M
- **500,000 M365 sign-in events** across 6 applications (Teams, Exchange, OneDrive, SharePoint, Power BI, Azure Portal)
- **20 worker camps** with tracked capacity and residency

---

## ⚙️ Configuration

To point the dashboard at a different gold layer path, edit line 24 of `dashboard.py`:

```python
GOLD_PATH = r"C:\path\to\your\freeway_m365_dataset\gold"
```

---

## 🛠️ Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| [Streamlit](https://streamlit.io) | 1.57+ | Web app framework |
| [Plotly](https://plotly.com/python/) | 6.7+ | Interactive charts & maps |
| [Pandas](https://pandas.pydata.org) | — | Data manipulation |
| [PyArrow](https://arrow.apache.org/docs/python/) | — | Parquet file reading |

---

