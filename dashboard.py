# =============================================================================
# Freeway M365 Enterprise Dashboard
# Production-Grade Streamlit Application
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, date

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Freeway M365 Enterprise Dashboard",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Gold Path ─────────────────────────────────────────────────────────────────
GOLD_PATH = r"C:\Users\Siddique\Downloads\az\spark\pyspark\freeway_ent\freeway_m365_dataset\gold"

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Global background ── */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #58a6ff;
    }

    /* ── Header banner ── */
    .dashboard-header {
        background: linear-gradient(135deg, #1f2937 0%, #111827 50%, #0f172a 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 24px 32px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .dashboard-header h1 {
        color: #f0f6fc;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .dashboard-header p {
        color: #8b949e;
        margin: 4px 0 0 0;
        font-size: 0.9rem;
    }

    /* ── KPI Cards ── */
    .kpi-card {
        background: linear-gradient(145deg, #161b22, #1c2128);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px 24px;
        text-align: center;
        transition: border-color 0.2s;
    }
    .kpi-card:hover { border-color: #58a6ff; }
    .kpi-label {
        color: #8b949e;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 8px;
    }
    .kpi-value {
        color: #f0f6fc;
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
    }
    .kpi-delta-pos { color: #3fb950; font-size: 0.82rem; margin-top: 6px; }
    .kpi-delta-neg { color: #f85149; font-size: 0.82rem; margin-top: 6px; }

    /* ── Section divider ── */
    .section-title {
        color: #58a6ff;
        font-size: 1.1rem;
        font-weight: 600;
        border-left: 3px solid #58a6ff;
        padding-left: 10px;
        margin: 24px 0 16px 0;
    }

    /* ── Footer ── */
    .dashboard-footer {
        text-align: center;
        color: #484f58;
        font-size: 0.78rem;
        padding: 20px 0 8px 0;
        border-top: 1px solid #21262d;
        margin-top: 40px;
    }

    /* ── Tab styling ── */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #161b22;
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #8b949e;
        border-radius: 6px;
        font-weight: 500;
        padding: 8px 18px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #21262d !important;
        color: #f0f6fc !important;
    }

    /* ── Metric overrides ── */
    [data-testid="stMetricValue"] { color: #f0f6fc !important; font-size: 1.8rem !important; }
    [data-testid="stMetricLabel"] { color: #8b949e !important; }
    [data-testid="stMetricDelta"] svg { display: none; }

    /* ── Plotly chart containers ── */
    .js-plotly-plot { border-radius: 8px; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0d1117; }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Plotly dark layout defaults ───────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#161b22",
    plot_bgcolor="#0d1117",
    font=dict(family="Inter, sans-serif", color="#c9d1d9", size=12),
    margin=dict(l=40, r=20, t=50, b=40),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#30363d", borderwidth=1),
    xaxis=dict(gridcolor="#21262d", linecolor="#30363d"),
    yaxis=dict(gridcolor="#21262d", linecolor="#30363d"),
)

COLOR_SEQ   = px.colors.qualitative.Bold
COLOR_SAFE  = "#3fb950"
COLOR_WARN  = "#d29922"
COLOR_CRIT  = "#f85149"
COLOR_INFO  = "#58a6ff"

# =============================================================================
# DATA LOADING
# =============================================================================

@st.cache_data(show_spinner=False)
def load_parquet(filename: str) -> pd.DataFrame:
    path = os.path.join(GOLD_PATH, filename)
    try:
        return pd.read_parquet(path)
    except FileNotFoundError:
        st.error(f"❌ File not found: `{path}`")
        return pd.DataFrame()
    except Exception as exc:
        st.error(f"❌ Error loading `{filename}`: {exc}")
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_all_data():
    data = {
        "dim_camp":          load_parquet("dim_camp.parquet"),
        "dim_device":        load_parquet("dim_device.parquet"),
        "dim_equipment":     load_parquet("dim_equipment.parquet"),
        "dim_material":      load_parquet("dim_material.parquet"),
        "dim_project":       load_parquet("dim_project.parquet"),
        "dim_site":          load_parquet("dim_site.parquet"),
        "dim_user":          load_parquet("dim_user.parquet"),
        "dim_vehicle":       load_parquet("dim_vehicle.parquet"),
        "fact_daily_signins": load_parquet("fact_daily_signins.parquet"),
        "fact_signin":       load_parquet("fact_signin.parquet"),
    }
    # ── Type coercions ──
    if not data["fact_daily_signins"].empty:
        data["fact_daily_signins"]["date"] = pd.to_datetime(
            data["fact_daily_signins"]["date"], errors="coerce"
        )
    if not data["fact_signin"].empty:
        data["fact_signin"]["timestamp"] = pd.to_datetime(
            data["fact_signin"]["timestamp"], errors="coerce"
        )
    if not data["dim_user"].empty:
        for col in ["visa_expiry_date", "hire_date"]:
            if col in data["dim_user"].columns:
                data["dim_user"][col] = pd.to_datetime(
                    data["dim_user"][col], errors="coerce"
                )
    return data


# =============================================================================
# HELPER UTILITIES
# =============================================================================

def apply_layout(fig, title="", height=400):
    """Apply consistent dark layout to any plotly figure."""
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=title, font=dict(size=14, color="#f0f6fc"), x=0.01),
        height=height,
    )
    return fig


def fmt_number(n: float, decimals: int = 0) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return f"{n:.{decimals}f}"


def kpi_card(label: str, value: str, delta: str = "", positive: bool = True):
    delta_class = "kpi-delta-pos" if positive else "kpi-delta-neg"
    delta_html  = f'<div class="{delta_class}">{delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def section(title: str):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


# =============================================================================
# SIDEBAR FILTERS
# =============================================================================

def render_sidebar(data: dict):
    st.sidebar.markdown("## 🔍 Global Filters")
    st.sidebar.markdown("---")

    # ── Date range ──
    fds = data["fact_daily_signins"]
    if not fds.empty and "date" in fds.columns:
        min_date = fds["date"].min().date()
        max_date = fds["date"].max().date()
    else:
        min_date = date(2025, 1, 1)
        max_date = date(2025, 12, 30)

    st.sidebar.markdown("**📅 Date Range**")
    date_from = st.sidebar.date_input("From", value=min_date, min_value=min_date, max_value=max_date, key="date_from")
    date_to   = st.sidebar.date_input("To",   value=max_date, min_value=min_date, max_value=max_date, key="date_to")

    st.sidebar.markdown("---")

    # ── Role filter ──
    du = data["dim_user"]
    roles = sorted(du["role"].dropna().unique().tolist()) if not du.empty and "role" in du.columns else []
    selected_roles = st.sidebar.multiselect("👷 Role", options=roles, default=[], placeholder="All roles")

    # ── Nationality filter ──
    nats = sorted(du["nationality"].dropna().unique().tolist()) if not du.empty and "nationality" in du.columns else []
    selected_nats = st.sidebar.multiselect("🌍 Nationality", options=nats, default=[], placeholder="All nationalities")

    # ── Site City filter ──
    cities = sorted(du["site_city"].dropna().unique().tolist()) if not du.empty and "site_city" in du.columns else []
    selected_cities = st.sidebar.multiselect("🏙️ Site City", options=cities, default=[], placeholder="All cities")

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        '<div style="color:#484f58;font-size:0.75rem;text-align:center;">Freeway Analytics v1.0</div>',
        unsafe_allow_html=True,
    )

    return {
        "date_from":    pd.Timestamp(date_from),
        "date_to":      pd.Timestamp(date_to),
        "roles":        selected_roles,
        "nationalities": selected_nats,
        "cities":       selected_cities,
    }


def filter_users(du: pd.DataFrame, filters: dict) -> pd.DataFrame:
    df = du.copy()
    if filters["roles"]:
        df = df[df["role"].isin(filters["roles"])]
    if filters["nationalities"]:
        df = df[df["nationality"].isin(filters["nationalities"])]
    if filters["cities"]:
        df = df[df["site_city"].isin(filters["cities"])]
    return df


def filter_signins(fs: pd.DataFrame, filters: dict) -> pd.DataFrame:
    df = fs.copy()
    if filters["roles"]:
        df = df[df["role"].isin(filters["roles"])]
    if filters["nationalities"]:
        df = df[df["nationality"].isin(filters["nationalities"])]
    return df


def filter_daily(fds: pd.DataFrame, filters: dict) -> pd.DataFrame:
    df = fds.copy()
    mask = (df["date"] >= filters["date_from"]) & (df["date"] <= filters["date_to"])
    return df[mask]


# =============================================================================
# TAB 1 — EXECUTIVE OVERVIEW
# =============================================================================

def tab_executive(data: dict, filters: dict):
    du  = filter_users(data["dim_user"], filters)
    fs  = filter_signins(data["fact_signin"], filters)
    fds = filter_daily(data["fact_daily_signins"], filters)
    dp  = data["dim_project"]

    # ── KPI Calculations ──
    total_users    = len(du)
    total_signins  = len(fs)
    failure_rate   = (fs["status"] == "Failure").mean() * 100 if not fs.empty else 0
    critical_risk  = (fs["risk_level"] == "Critical").mean() * 100 if not fs.empty else 0
    active_projects = len(dp) if not dp.empty else 0
    total_budget   = dp["budget_usd"].sum() if not dp.empty and "budget_usd" in dp.columns else 0

    # ── KPI Row ──
    section("📊 Key Performance Indicators")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.metric("👥 Total Users",    fmt_number(total_users))
    with c2:
        st.metric("🔐 Total Sign-ins", fmt_number(total_signins))
    with c3:
        st.metric("❌ Failure Rate",   f"{failure_rate:.1f}%",
                  delta=f"{failure_rate - 25:.1f}% vs baseline", delta_color="inverse")
    with c4:
        st.metric("⚠️ Critical Risk",  f"{critical_risk:.1f}%",
                  delta=f"{critical_risk - 25:.1f}% vs baseline", delta_color="inverse")
    with c5:
        st.metric("🏗️ Active Projects", str(active_projects))
    with c6:
        st.metric("💰 Total Budget",   fmt_number(total_budget))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Daily trend + Status donut ──
    col_left, col_right = st.columns([2, 1])

    with col_left:
        section("📈 Daily Sign-in Trend")
        if not fds.empty:
            daily_agg = fds.groupby("date")["signin_count"].sum().reset_index()
            daily_agg["7d_avg"] = daily_agg["signin_count"].rolling(7, min_periods=1).mean()

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_agg["date"], y=daily_agg["signin_count"],
                mode="lines", name="Daily Sign-ins",
                line=dict(color=COLOR_INFO, width=1.5),
                fill="tozeroy", fillcolor="rgba(88,166,255,0.08)",
            ))
            fig.add_trace(go.Scatter(
                x=daily_agg["date"], y=daily_agg["7d_avg"],
                mode="lines", name="7-Day Avg",
                line=dict(color=COLOR_WARN, width=2, dash="dot"),
            ))
            apply_layout(fig, "Daily Sign-in Volume (2025)", height=320)
            fig.update_xaxes(title_text="Date")
            fig.update_yaxes(title_text="Sign-in Count")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No daily sign-in data available.")

    with col_right:
        section("🔵 Sign-in Status")
        if not fs.empty and "status" in fs.columns:
            status_counts = fs["status"].value_counts().reset_index()
            status_counts.columns = ["status", "count"]
            fig = px.pie(
                status_counts, names="status", values="count",
                hole=0.55,
                color="status",
                color_discrete_map={"Success": COLOR_SAFE, "Failure": COLOR_CRIT},
            )
            fig.update_traces(
                textposition="outside", textinfo="percent+label",
                marker=dict(line=dict(color="#0d1117", width=2)),
            )
            apply_layout(fig, "Sign-in Status Distribution", height=320)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sign-in status data available.")

    # ── Row 2: Risk level bar ──
    section("🚨 Risk Level Distribution")
    if not fs.empty and "risk_level" in fs.columns:
        risk_order  = ["Low", "Medium", "High", "Critical"]
        risk_colors = {"Low": COLOR_SAFE, "Medium": COLOR_WARN, "High": "#e3b341", "Critical": COLOR_CRIT}
        risk_counts = fs["risk_level"].value_counts().reindex(risk_order, fill_value=0).reset_index()
        risk_counts.columns = ["risk_level", "count"]

        fig = px.bar(
            risk_counts, x="risk_level", y="count",
            color="risk_level",
            color_discrete_map=risk_colors,
            text="count",
        )
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside",
                          marker_line_color="#0d1117", marker_line_width=1)
        apply_layout(fig, "Sign-ins by Risk Level", height=300)
        fig.update_xaxes(title_text="Risk Level")
        fig.update_yaxes(title_text="Count")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No risk level data available.")


# =============================================================================
# TAB 2 — SECURITY & IDENTITY
# =============================================================================

def tab_security(data: dict, filters: dict):
    fs = filter_signins(data["fact_signin"], filters)
    dd = data["dim_device"]

    if fs.empty:
        st.warning("No sign-in data available for the selected filters.")
        return

    # ── Row 1: Failures by role + Risk over time ──
    col1, col2 = st.columns(2)

    with col1:
        section("👷 Sign-in Failures by Role")
        if "role" in fs.columns and "status" in fs.columns:
            fail_role = (
                fs[fs["status"] == "Failure"]
                .groupby("role").size().reset_index(name="failures")
                .sort_values("failures", ascending=True)
            )
            fig = px.bar(
                fail_role, x="failures", y="role", orientation="h",
                color="failures",
                color_continuous_scale=["#1f2937", COLOR_CRIT],
                text="failures",
            )
            fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside",
                              marker_line_width=0)
            apply_layout(fig, "Sign-in Failures by Role", height=380)
            fig.update_xaxes(title_text="Failure Count")
            fig.update_yaxes(title_text="")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("📉 Risk Level Over Time")
        if "timestamp" in fs.columns and "risk_level" in fs.columns:
            fs_t = fs.copy()
            fs_t["month"] = fs_t["timestamp"].dt.to_period("M").astype(str)
            risk_time = (
                fs_t.groupby(["month", "risk_level"]).size()
                .reset_index(name="count")
            )
            risk_order = ["Low", "Medium", "High", "Critical"]
            risk_colors_list = [COLOR_SAFE, COLOR_WARN, "#e3b341", COLOR_CRIT]
            fig = px.area(
                risk_time, x="month", y="count", color="risk_level",
                color_discrete_sequence=risk_colors_list,
                category_orders={"risk_level": risk_order},
            )
            apply_layout(fig, "Risk Level Distribution Over Time", height=380)
            fig.update_xaxes(title_text="Month", tickangle=45)
            fig.update_yaxes(title_text="Sign-in Count")
            st.plotly_chart(fig, use_container_width=True)

    # ── Row 2: Top risky apps + Failure rate by nationality ──
    col3, col4 = st.columns(2)

    with col3:
        section("📱 Top Risky Applications")
        if "application" in fs.columns and "risk_level" in fs.columns:
            risky_apps = (
                fs[fs["risk_level"].isin(["High", "Critical"])]
                .groupby("application").size().reset_index(name="risky_signins")
                .sort_values("risky_signins", ascending=True)
            )
            fig = px.bar(
                risky_apps, x="risky_signins", y="application", orientation="h",
                color="risky_signins",
                color_continuous_scale=["#1f2937", "#e3b341"],
                text="risky_signins",
            )
            fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside",
                              marker_line_width=0)
            apply_layout(fig, "High/Critical Risk Sign-ins by Application", height=340)
            fig.update_xaxes(title_text="Risky Sign-ins")
            fig.update_yaxes(title_text="")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        section("🌍 Failure Rate by Nationality")
        if "nationality" in fs.columns and "status" in fs.columns:
            nat_stats = fs.groupby("nationality").agg(
                total=("status", "count"),
                failures=("status", lambda x: (x == "Failure").sum())
            ).reset_index()
            nat_stats["failure_rate"] = (nat_stats["failures"] / nat_stats["total"] * 100).round(1)
            nat_stats = nat_stats.sort_values("failure_rate", ascending=True)

            fig = px.bar(
                nat_stats, x="failure_rate", y="nationality", orientation="h",
                color="failure_rate",
                color_continuous_scale=["#1f2937", COLOR_CRIT],
                text="failure_rate",
            )
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                              marker_line_width=0)
            apply_layout(fig, "Sign-in Failure Rate by Nationality (%)", height=340)
            fig.update_xaxes(title_text="Failure Rate (%)")
            fig.update_yaxes(title_text="")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    # ── Row 3: Device OS breakdown ──
    section("💻 Device OS Breakdown")
    if not dd.empty and "os" in dd.columns:
        os_counts = dd["os"].value_counts().reset_index()
        os_counts.columns = ["os", "count"]
        fig = px.pie(
            os_counts, names="os", values="count",
            hole=0.5,
            color_discrete_sequence=COLOR_SEQ,
        )
        fig.update_traces(
            textposition="outside", textinfo="percent+label",
            marker=dict(line=dict(color="#0d1117", width=2)),
        )
        apply_layout(fig, "Device OS Distribution", height=340)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No device OS data available.")


# =============================================================================
# TAB 3 — WORKFORCE ANALYTICS
# =============================================================================

def tab_workforce(data: dict, filters: dict):
    du = filter_users(data["dim_user"], filters)
    dc = data["dim_camp"]

    if du.empty:
        st.warning("No user data available for the selected filters.")
        return

    # ── Row 1: Nationality donut + Role bar ──
    col1, col2 = st.columns(2)

    with col1:
        section("🌍 Workforce by Nationality")
        if "nationality" in du.columns:
            nat_counts = du["nationality"].value_counts().reset_index()
            nat_counts.columns = ["nationality", "count"]
            fig = px.pie(
                nat_counts, names="nationality", values="count",
                hole=0.5,
                color_discrete_sequence=COLOR_SEQ,
            )
            fig.update_traces(
                textposition="outside", textinfo="percent+label",
                marker=dict(line=dict(color="#0d1117", width=2)),
            )
            apply_layout(fig, "Workforce Nationality Distribution", height=380)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("👷 Workforce by Role")
        if "role" in du.columns:
            role_counts = du["role"].value_counts().reset_index()
            role_counts.columns = ["role", "count"]
            role_counts = role_counts.sort_values("count", ascending=True)
            fig = px.bar(
                role_counts, x="count", y="role", orientation="h",
                color="count",
                color_continuous_scale=["#1f2937", COLOR_INFO],
                text="count",
            )
            fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside",
                              marker_line_width=0)
            apply_layout(fig, "Headcount by Role", height=380)
            fig.update_xaxes(title_text="Headcount")
            fig.update_yaxes(title_text="")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    # ── Row 2: Site city bar + Users per project ──
    col3, col4 = st.columns(2)

    with col3:
        section("🏙️ Workforce by Site City")
        if "site_city" in du.columns:
            city_counts = du["site_city"].value_counts().reset_index()
            city_counts.columns = ["site_city", "count"]
            fig = px.bar(
                city_counts, x="site_city", y="count",
                color="site_city",
                color_discrete_sequence=COLOR_SEQ,
                text="count",
            )
            fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside",
                              marker_line_width=0)
            apply_layout(fig, "Workforce Distribution by Site City", height=340)
            fig.update_xaxes(title_text="City")
            fig.update_yaxes(title_text="Headcount")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        section("🏗️ Top 10 Projects by User Count")
        if "project_name" in du.columns:
            proj_counts = (
                du["project_name"].value_counts()
                .head(10).reset_index()
            )
            proj_counts.columns = ["project_name", "count"]
            proj_counts = proj_counts.sort_values("count", ascending=True)
            fig = px.bar(
                proj_counts, x="count", y="project_name", orientation="h",
                color="count",
                color_continuous_scale=["#1f2937", COLOR_SAFE],
                text="count",
            )
            fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside",
                              marker_line_width=0)
            apply_layout(fig, "Top 10 Projects by Headcount", height=340)
            fig.update_xaxes(title_text="User Count")
            fig.update_yaxes(title_text="")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    # ── Row 3: Camp capacity utilization ──
    section("🏕️ Camp Capacity Utilization")
    if not dc.empty and "camp_name" in dc.columns and "capacity" in dc.columns:
        if "camp_name" in du.columns:
            camp_users = du["camp_name"].value_counts().reset_index()
            camp_users.columns = ["camp_name", "residents"]
            camp_util = dc.merge(camp_users, on="camp_name", how="left").fillna({"residents": 0})
            camp_util["utilization_pct"] = (
                camp_util["residents"] / camp_util["capacity"] * 100
            ).clip(upper=100).round(1)
            camp_util = camp_util.sort_values("utilization_pct", ascending=False)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=camp_util["camp_name"], y=camp_util["capacity"],
                name="Capacity", marker_color="#21262d",
                marker_line_color="#30363d", marker_line_width=1,
            ))
            fig.add_trace(go.Bar(
                x=camp_util["camp_name"], y=camp_util["residents"],
                name="Residents", marker_color=COLOR_INFO,
                marker_line_color="#0d1117", marker_line_width=1,
                text=camp_util["utilization_pct"].astype(str) + "%",
                textposition="outside",
            ))
            apply_layout(fig, "Camp Capacity vs. Current Residents", height=340)
            fig.update_layout(barmode="overlay")
            fig.update_xaxes(title_text="Camp")
            fig.update_yaxes(title_text="People")
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Fallback: just show capacity
            fig = px.bar(
                dc, x="camp_name", y="capacity",
                color="capacity",
                color_continuous_scale=["#1f2937", COLOR_INFO],
                text="capacity",
            )
            fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            apply_layout(fig, "Camp Capacity", height=340)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No camp capacity data available.")


# =============================================================================
# TAB 4 — PROJECTS & SITES
# =============================================================================

def tab_projects(data: dict, filters: dict):
    dp  = data["dim_project"]
    ds  = data["dim_site"]
    du  = filter_users(data["dim_user"], filters)

    # ── Row 1: Budget comparison ──
    section("💰 Project Budget Comparison")
    if not dp.empty and "project_name" in dp.columns and "budget_usd" in dp.columns:
        dp_sorted = dp.sort_values("budget_usd", ascending=False)
        fig = px.bar(
            dp_sorted, x="project_name", y="budget_usd",
            color="budget_usd",
            color_continuous_scale=["#1f2937", COLOR_INFO],
            text="budget_usd",
        )
        fig.update_traces(
            texttemplate="%{text:$,.0f}", textposition="outside",
            marker_line_color="#0d1117", marker_line_width=1,
        )
        apply_layout(fig, "Project Budget (USD)", height=360)
        fig.update_xaxes(title_text="Project", tickangle=30)
        fig.update_yaxes(title_text="Budget (USD)")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No project budget data available.")

    # ── Row 2: Site map + Top projects by user count ──
    col1, col2 = st.columns([1.4, 1])

    with col1:
        section("🗺️ Site Locations Map")
        if not ds.empty and "latitude" in ds.columns and "longitude" in ds.columns:
            ds_map = ds.dropna(subset=["latitude", "longitude"]).copy()
            ds_map = ds_map.rename(columns={"latitude": "lat", "longitude": "lon"})

            # st.map for quick map, plus plotly scatter_mapbox for richer view
            fig = px.scatter_mapbox(
                ds_map,
                lat="lat", lon="lon",
                hover_name="site_name" if "site_name" in ds_map.columns else None,
                hover_data={col: True for col in ds_map.columns if col not in ["lat", "lon"]},
                color_discrete_sequence=[COLOR_INFO],
                zoom=4,
                height=420,
            )
            fig.update_traces(marker=dict(size=14, opacity=0.85))
            fig.update_layout(
                mapbox_style="carto-darkmatter",
                paper_bgcolor="#161b22",
                plot_bgcolor="#0d1117",
                font=dict(color="#c9d1d9"),
                margin=dict(l=0, r=0, t=40, b=0),
                title=dict(text="Project Site Locations", font=dict(size=14, color="#f0f6fc"), x=0.01),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No site location data available.")

    with col2:
        section("🏗️ Top Projects by User Count")
        if not du.empty and "project_name" in du.columns:
            proj_user = (
                du["project_name"].value_counts()
                .head(10).reset_index()
            )
            proj_user.columns = ["project_name", "user_count"]
            proj_user = proj_user.sort_values("user_count", ascending=True)

            fig = px.bar(
                proj_user, x="user_count", y="project_name", orientation="h",
                color="user_count",
                color_continuous_scale=["#1f2937", COLOR_SAFE],
                text="user_count",
            )
            fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside",
                              marker_line_width=0)
            apply_layout(fig, "Top Projects by Assigned Users", height=420)
            fig.update_xaxes(title_text="User Count")
            fig.update_yaxes(title_text="")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No project-user data available.")

    # ── Site details table ──
    section("📋 Site Details")
    if not ds.empty:
        st.dataframe(
            ds.style.set_properties(**{
                "background-color": "#161b22",
                "color": "#c9d1d9",
                "border-color": "#30363d",
            }),
            use_container_width=True,
            height=220,
        )


# =============================================================================
# TAB 5 — SIGN-IN ACTIVITY
# =============================================================================

def tab_activity(data: dict, filters: dict):
    fs  = filter_signins(data["fact_signin"], filters)
    fds = filter_daily(data["fact_daily_signins"], filters)

    if fs.empty:
        st.warning("No sign-in data available for the selected filters.")
        return

    # ── Row 1: Heatmap ──
    section("🗓️ Daily Sign-in Heatmap")
    if not fds.empty and "date" in fds.columns:
        hm = fds.copy()
        hm["month"] = hm["date"].dt.strftime("%b")
        hm["day"]   = hm["date"].dt.day
        month_order = ["Jan","Feb","Mar","Apr","May","Jun",
                       "Jul","Aug","Sep","Oct","Nov","Dec"]
        hm_pivot = (
            hm.groupby(["month", "day"])["signin_count"]
            .sum().reset_index()
            .pivot(index="month", columns="day", values="signin_count")
            .reindex(month_order)
        )
        fig = go.Figure(data=go.Heatmap(
            z=hm_pivot.values,
            x=hm_pivot.columns.tolist(),
            y=hm_pivot.index.tolist(),
            colorscale=[
                [0.0,  "#0d1117"],
                [0.25, "#0c2d48"],
                [0.5,  "#1a5276"],
                [0.75, "#2980b9"],
                [1.0,  "#58a6ff"],
            ],
            hoverongaps=False,
            hovertemplate="Month: %{y}<br>Day: %{x}<br>Sign-ins: %{z:,.0f}<extra></extra>",
        ))
        apply_layout(fig, "Monthly Sign-in Heatmap (Day of Month)", height=340)
        fig.update_xaxes(title_text="Day of Month", dtick=1)
        fig.update_yaxes(title_text="Month")
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 2: Sign-ins by application over time + Hourly pattern ──
    col1, col2 = st.columns(2)

    with col1:
        section("📱 Sign-ins by Application Over Time")
        if "timestamp" in fs.columns and "application" in fs.columns:
            fs_app = fs.copy()
            fs_app["month"] = fs_app["timestamp"].dt.to_period("M").astype(str)
            app_time = (
                fs_app.groupby(["month", "application"]).size()
                .reset_index(name="count")
            )
            fig = px.line(
                app_time, x="month", y="count", color="application",
                color_discrete_sequence=COLOR_SEQ,
                markers=True,
            )
            apply_layout(fig, "Monthly Sign-ins by Application", height=360)
            fig.update_xaxes(title_text="Month", tickangle=45)
            fig.update_yaxes(title_text="Sign-in Count")
            fig.update_traces(line=dict(width=2), marker=dict(size=5))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("⏰ Hourly Sign-in Pattern")
        if "timestamp" in fs.columns:
            fs_h = fs.copy()
            fs_h["hour"] = fs_h["timestamp"].dt.hour
            hourly = fs_h.groupby("hour").size().reset_index(name="count")

            fig = px.bar(
                hourly, x="hour", y="count",
                color="count",
                color_continuous_scale=["#1f2937", COLOR_INFO],
                text="count",
            )
            fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside",
                              marker_line_width=0)
            apply_layout(fig, "Sign-in Volume by Hour of Day", height=360)
            fig.update_xaxes(title_text="Hour (24h)", dtick=1)
            fig.update_yaxes(title_text="Sign-in Count")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    # ── Row 3: Top 10 most active users ──
    section("🏆 Top 10 Most Active Users")
    if "upn" in fs.columns:
        top_users = (
            fs.groupby("upn").size().reset_index(name="signin_count")
            .sort_values("signin_count", ascending=False)
            .head(10)
        )
        # Enrich with role/nationality if available
        if "role" in fs.columns and "nationality" in fs.columns:
            user_meta = (
                fs[["upn", "role", "nationality"]]
                .drop_duplicates(subset=["upn"])
            )
            top_users = top_users.merge(user_meta, on="upn", how="left")

        top_users_disp = top_users.sort_values("signin_count", ascending=True)
        color_col = "role" if "role" in top_users_disp.columns else "signin_count"

        if color_col == "role":
            fig = px.bar(
                top_users_disp, x="signin_count", y="upn", orientation="h",
                color="role",
                color_discrete_sequence=COLOR_SEQ,
                text="signin_count",
                hover_data=["nationality"] if "nationality" in top_users_disp.columns else None,
            )
        else:
            fig = px.bar(
                top_users_disp, x="signin_count", y="upn", orientation="h",
                color="signin_count",
                color_continuous_scale=["#1f2937", COLOR_INFO],
                text="signin_count",
            )
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside",
                          marker_line_width=0)
        apply_layout(fig, "Top 10 Most Active Users by Sign-in Count", height=380)
        fig.update_xaxes(title_text="Sign-in Count")
        fig.update_yaxes(title_text="User (UPN)")
        if color_col != "role":
            fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # ── Sign-in status over time (stacked bar) ──
    section("📊 Sign-in Status Over Time")
    if "timestamp" in fs.columns and "status" in fs.columns:
        fs_s = fs.copy()
        fs_s["month"] = fs_s["timestamp"].dt.to_period("M").astype(str)
        status_time = (
            fs_s.groupby(["month", "status"]).size()
            .reset_index(name="count")
        )
        fig = px.bar(
            status_time, x="month", y="count", color="status",
            color_discrete_map={"Success": COLOR_SAFE, "Failure": COLOR_CRIT},
            barmode="stack",
            text="count",
        )
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="inside",
                          marker_line_width=0)
        apply_layout(fig, "Monthly Sign-in Status (Success vs Failure)", height=320)
        fig.update_xaxes(title_text="Month", tickangle=45)
        fig.update_yaxes(title_text="Sign-in Count")
        st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# MAIN APP
# =============================================================================

def main():
    # ── Header ──
    st.markdown("""
    <div class="dashboard-header">
        <div style="font-size:3rem;line-height:1;">🏗️</div>
        <div>
            <h1>Freeway M365 Enterprise Dashboard</h1>
            <p>Real-time workforce, security & operations intelligence · Saudi Arabia Construction Projects</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Load data ──
    with st.spinner("Loading gold layer data..."):
        data = load_all_data()

    # ── Check critical tables loaded ──
    critical = ["dim_user", "fact_signin", "fact_daily_signins"]
    missing  = [k for k in critical if data.get(k, pd.DataFrame()).empty]
    if missing:
        st.error(
            f"⚠️ Critical datasets could not be loaded: **{', '.join(missing)}**. "
            f"Please verify the gold path: `{GOLD_PATH}`"
        )

    # ── Sidebar filters ──
    filters = render_sidebar(data)

    # ── Summary ribbon ──
    du_f  = filter_users(data["dim_user"], filters)
    fs_f  = filter_signins(data["fact_signin"], filters)
    fds_f = filter_daily(data["fact_daily_signins"], filters)

    r1, r2, r3, r4 = st.columns(4)
    r1.markdown(
        f'<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;'
        f'padding:10px 16px;text-align:center;">'
        f'<span style="color:#8b949e;font-size:0.75rem;">FILTERED USERS</span><br>'
        f'<span style="color:#f0f6fc;font-size:1.4rem;font-weight:700;">{len(du_f):,}</span></div>',
        unsafe_allow_html=True,
    )
    r2.markdown(
        f'<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;'
        f'padding:10px 16px;text-align:center;">'
        f'<span style="color:#8b949e;font-size:0.75rem;">FILTERED SIGN-INS</span><br>'
        f'<span style="color:#f0f6fc;font-size:1.4rem;font-weight:700;">{len(fs_f):,}</span></div>',
        unsafe_allow_html=True,
    )
    failure_pct = (fs_f["status"] == "Failure").mean() * 100 if not fs_f.empty else 0
    r3.markdown(
        f'<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;'
        f'padding:10px 16px;text-align:center;">'
        f'<span style="color:#8b949e;font-size:0.75rem;">FAILURE RATE</span><br>'
        f'<span style="color:#f85149;font-size:1.4rem;font-weight:700;">{failure_pct:.1f}%</span></div>',
        unsafe_allow_html=True,
    )
    date_range_str = (
        f"{filters['date_from'].strftime('%d %b')} – {filters['date_to'].strftime('%d %b %Y')}"
    )
    r4.markdown(
        f'<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;'
        f'padding:10px 16px;text-align:center;">'
        f'<span style="color:#8b949e;font-size:0.75rem;">DATE RANGE</span><br>'
        f'<span style="color:#f0f6fc;font-size:1rem;font-weight:600;">{date_range_str}</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Executive Overview",
        "🔐 Security & Identity",
        "👷 Workforce Analytics",
        "🏗️ Projects & Sites",
        "📈 Sign-in Activity",
    ])

    with tab1:
        tab_executive(data, filters)

    with tab2:
        tab_security(data, filters)

    with tab3:
        tab_workforce(data, filters)

    with tab4:
        tab_projects(data, filters)

    with tab5:
        tab_activity(data, filters)

    # ── Footer ──
    st.markdown("""
    <div class="dashboard-footer">
        🏗️ &nbsp; Powered by Freeway Analytics &nbsp;|&nbsp; Data as of 2025 &nbsp;|&nbsp;
        Built with Streamlit &amp; Plotly
    </div>
    """, unsafe_allow_html=True)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
