"""Page 5 — Pump Health & Maintenance."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.databricks import gold
from utils.charts import (
    apply_dark, fmt_naira, fmt_liters,
    ORANGE, BLUE, GREEN, RED, AMBER, PURPLE, CYAN,
    PALETTE_ORANGE_BLUE, TEXT_MUTED, COLOR_SCALE_HEAT,
)


def render():
    st.markdown("""
    <div class="page-title">🔧 Pump Health & Maintenance</div>
    <div class="page-subtitle">IoT telemetry — predictive failure detection, health scoring, and maintenance intelligence</div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    with st.spinner("Loading pump data…"):
        try:
            health  = gold("gold_pump_health")
            failure = gold("gold_failure_risk")
            maint   = gold("gold_maintenance_scores")
            exec_df = gold("gold_executive_command_center")
        except Exception as e:
            st.error(f"Connection error: {e}")
            return

    # ── Derive correct KPIs ──────────────────────────────────────────────────
    # Total pumps = sum of pump_count across all stations (from maintenance scores)
    # Failed pumps = sum of failed_pumps from maintenance scores (NOT count of failure_flag rows)
    # Avg health   = mean health_score from gold_pump_health
    # High risk    = count of HIGH failure_risk from gold_failure_risk
    # Uptime       = mean uptime_hours from gold_pump_health
    # failed_pump_count KPI comes from gold_executive_command_center (most accurate)

    total_pumps    = int(maint["pump_count"].sum()) if not maint.empty else 0
    failed_pumps   = int(maint["failed_pumps"].sum()) if not maint.empty else 0
    avg_health     = float(health["health_score"].mean()) if not health.empty else 0.0
    avg_uptime     = float(health["uptime_hours"].mean()) if not health.empty and "uptime_hours" in health.columns else 0.0
    high_risk_ct   = int((failure["failure_risk"] == "HIGH").sum()) if not failure.empty else 0

    # Override failed_pumps from exec table if available (source of truth)
    if not exec_df.empty and "failed_pump_count" in exec_df.columns:
        failed_pumps = int(exec_df.iloc[-1]["failed_pump_count"])

    # ── KPIs ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Fleet Health Summary</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Avg Health Score",  f"{avg_health:.1f}/100")
    c2.metric("Total Pumps",       f"{total_pumps:,}")
    c3.metric("Failed Pumps",      failed_pumps,
              delta=f"{'⚠️' if failed_pumps > 0 else '✅'} {failed_pumps} offline" if failed_pumps else None)
    c4.metric("Avg Uptime (hrs)",  f"{avg_uptime:,.0f}")
    c5.metric("High Failure Risk", high_risk_ct)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Health distribution + failure risk pie ────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-header">📊 Health Score Distribution</div>',
                    unsafe_allow_html=True)
        if not health.empty:
            fig = go.Figure(go.Histogram(
                x=health["health_score"],
                nbinsx=20,
                marker=dict(
                    color=health["health_score"],
                    colorscale=[[0, RED], [0.4, AMBER], [0.7, ORANGE], [1, GREEN]],
                    showscale=False,
                    line=dict(color="#0f172a", width=0.5),
                ),
                opacity=0.9,
            ))
            # Threshold reference lines
            for val, label, color in [(40, "Critical", RED), (60, "Warning", AMBER), (80, "Good", GREEN)]:
                fig.add_vline(x=val, line_dash="dash", line_color=color, opacity=0.8,
                              annotation_text=label, annotation_position="top right",
                              annotation_font=dict(color=color, size=11))
            apply_dark(fig, "Pump Health Score Distribution", height=340)
            fig.update_xaxes(title_text="Health Score (0-100)")
            fig.update_yaxes(title_text="Number of Pumps")
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">⚡ Failure Risk Breakdown</div>',
                    unsafe_allow_html=True)
        if not failure.empty:
            risk_counts = failure["failure_risk"].value_counts().reset_index()
            risk_counts.columns = ["risk", "count"]
            risk_colors = {"HIGH": RED, "MEDIUM": AMBER, "LOW": GREEN, "CRITICAL": PURPLE}
            colors = [risk_colors.get(str(r).upper(), BLUE) for r in risk_counts["risk"]]
            fig2 = go.Figure(go.Pie(
                labels=risk_counts["risk"], values=risk_counts["count"],
                hole=0.55, marker=dict(colors=colors),
                textinfo="label+percent+value", textfont=dict(size=12),
            ))
            apply_dark(fig2, "Pump Failure Risk Classification", height=340)
            st.plotly_chart(fig2, use_container_width=True)

    # ── IoT telemetry scatter ─────────────────────────────────────────────────
    st.markdown('<div class="section-header">🌡️ IoT Telemetry — Temperature, Pressure & Vibration</div>',
                unsafe_allow_html=True)
    if not health.empty:
        telemetry_cols = [c for c in ["temperature", "pressure", "vibration"] if c in health.columns]
        if len(telemetry_cols) >= 2:
            sample = health.sample(min(500, len(health)), random_state=42)
            col_t1, col_t2, col_t3 = st.columns(3)
            pairs = [
                ("temperature", "pressure",  col_t1),
                ("pressure",    "vibration", col_t2),
                ("temperature", "vibration", col_t3),
            ]
            for x_col, y_col, widget_col in pairs:
                if x_col in sample.columns and y_col in sample.columns:
                    with widget_col:
                        fs = px.scatter(
                            sample, x=x_col, y=y_col,
                            color="health_score",
                            color_continuous_scale=[[0, RED], [0.5, AMBER], [1, GREEN]],
                            opacity=0.75,
                            hover_data=["station_id", "pump_id", "health_score"],
                        )
                        apply_dark(fs, f"{x_col.title()} vs {y_col.title()}", height=280)
                        st.plotly_chart(fs, use_container_width=True)

    # ── Maintenance scores by station ─────────────────────────────────────────
    st.markdown('<div class="section-header">🏗️ Maintenance Scores by Station</div>',
                unsafe_allow_html=True)
    if not maint.empty:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            stn_sorted = maint.sort_values("avg_health_score")
            fig3 = go.Figure(go.Bar(
                x=stn_sorted["avg_health_score"],
                y=stn_sorted["station_id"].astype(str),
                orientation="h",
                marker=dict(
                    color=stn_sorted["avg_health_score"],
                    colorscale=[[0, RED], [0.5, AMBER], [1, GREEN]],
                    showscale=True,
                    colorbar=dict(title="Health Score",
                                  tickfont=dict(color=TEXT_MUTED)),
                ),
                text=[f"{v:.1f}" for v in stn_sorted["avg_health_score"]],
                textposition="outside",
            ))
            apply_dark(fig3, "Avg Pump Health Score by Station", height=max(400, len(maint) * 22))
            st.plotly_chart(fig3, use_container_width=True)

        with col_m2:
            # Bubble: pump_count vs avg_health, sized by failed_pumps+1
            maint["bubble_size"] = (maint["failed_pumps"] + 1) * 10
            fig4 = px.scatter(
                maint, x="pump_count", y="avg_health_score",
                size="bubble_size",
                color="failed_pumps",
                color_continuous_scale=[[0, GREEN], [0.5, AMBER], [1, RED]],
                hover_data=["station_id", "state", "failed_pumps"],
                text="station_id",
                labels={"pump_count": "Pump Count",
                        "avg_health_score": "Avg Health Score",
                        "failed_pumps": "Failed Pumps"},
            )
            fig4.update_traces(textposition="top center",
                               textfont=dict(size=9, color="#94a3b8"))
            apply_dark(fig4, "Pump Count vs Avg Health (bubble = failed pumps)", height=max(400, len(maint) * 22))
            st.plotly_chart(fig4, use_container_width=True)

    # ── Failed pump alert table ───────────────────────────────────────────────
    st.markdown('<div class="section-header">🚨 Stations with Failed Pumps</div>',
                unsafe_allow_html=True)
    if not maint.empty:
        failed_stns = maint[maint["failed_pumps"] > 0].sort_values("failed_pumps", ascending=False)
        if not failed_stns.empty:
            disp = failed_stns.copy()
            disp["avg_health_score"] = disp["avg_health_score"].apply(lambda x: f"{x:.1f}")
            disp.columns = [c.replace("_", " ").title() for c in disp.columns]
            st.dataframe(disp.reset_index(drop=True), use_container_width=True, height=280)
        else:
            st.success("✅ No stations with failed pumps at this time.")

    # ── High failure-risk individual pumps ────────────────────────────────────
    st.markdown('<div class="section-header">⚠️ High Failure-Risk Individual Pumps</div>',
                unsafe_allow_html=True)
    if not failure.empty:
        high = failure[failure["failure_risk"] == "HIGH"].sort_values("health_score")
        if not high.empty:
            disp2 = high.reset_index(drop=True).copy()
            disp2.columns = [c.replace("_", " ").title() for c in disp2.columns]
            st.dataframe(disp2, use_container_width=True, height=280)
        else:
            st.success("✅ No high failure-risk pumps detected.")
