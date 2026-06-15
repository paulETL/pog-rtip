"""Page 3 — Inventory & Tank Monitoring."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.databricks import gold
from utils.charts import (
    apply_dark, fmt_liters,
    ORANGE, BLUE, GREEN, RED, AMBER, PURPLE, CYAN,
    TEXT_MUTED, COLOR_SCALE_HEAT,
)


def render():
    st.markdown("""
    <div class="page-title">🛢️ Inventory & Tank Monitoring</div>
    <div class="page-subtitle">Live tank levels, stockout risk intelligence, and utilisation analytics</div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    with st.spinner("Loading inventory data…"):
        try:
            inv  = gold("gold_inventory_position")
            tank = gold("gold_tank_utilization")
            risk = gold("gold_stockout_risk")
        except Exception as e:
            st.error(f"Connection error: {e}")
            return

    # Normalise low_tank_flag — may come in as bool True/False or int 1/0 or string
    if not inv.empty and "low_tank_flag" in inv.columns:
        inv["low_tank_flag"] = inv["low_tank_flag"].map(
            lambda x: 1 if str(x).strip().lower() in ("true", "1", "yes") else 0
        )

    # ── KPIs ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Inventory Snapshot</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    if not inv.empty:
        total_vol = inv["current_volume"].sum()
        total_cap = inv["tank_capacity"].sum()
        avg_util  = inv["utilization_pct"].mean()
        low_tanks = int(inv["low_tank_flag"].sum())
        at_risk   = int((risk["stockout_risk"] == "HIGH").sum()) if not risk.empty else 0

        c1.metric("Total Volume",      fmt_liters(total_vol))
        c2.metric("Total Capacity",    fmt_liters(total_cap))
        c3.metric("Avg Utilisation",   f"{avg_util:.1f}%")
        c4.metric("Low Tank Alerts",   low_tanks)
        c5.metric("High Stockout Risk",at_risk)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Network gauge + risk donut ────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-header">⛽ Network Fuel Level Gauge</div>',
                    unsafe_allow_html=True)
        if not inv.empty:
            pct = (inv["current_volume"].sum() / inv["tank_capacity"].sum() * 100)
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=round(pct, 1),
                delta={"reference": 50, "valueformat": ".1f",
                       "increasing": {"color": GREEN}, "decreasing": {"color": RED}},
                gauge={
                    "axis": {"range": [0, 100], "ticksuffix": "%",
                              "tickfont": dict(color=TEXT_MUTED)},
                    "bar":  {"color": ORANGE, "thickness": 0.25},
                    "bgcolor": "#0f172a",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0,  20], "color": "rgba(239,68,68,0.2)"},
                        {"range": [20, 50], "color": "rgba(245,158,11,0.1)"},
                        {"range": [50,100], "color": "rgba(34,197,94,0.08)"},
                    ],
                    "threshold": {"line": {"color": RED, "width": 4},
                                  "thickness": 0.75, "value": 20},
                },
                number={"suffix": "%", "font": {"color": "#f8fafc", "size": 56}},
                title={"text": "Network-wide Tank Fill Level", "font": {"color": TEXT_MUTED}},
            ))
            fig_g.update_layout(paper_bgcolor="#0f172a", height=320,
                                 margin=dict(l=30, r=30, t=60, b=10))
            st.plotly_chart(fig_g, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">⚠️ Stockout Risk Distribution</div>',
                    unsafe_allow_html=True)
        if not risk.empty:
            rc = risk["stockout_risk"].value_counts().reset_index()
            rc.columns = ["risk", "count"]
            rcolors = {"HIGH": RED, "MEDIUM": AMBER, "LOW": GREEN, "CRITICAL": PURPLE}
            fig_r = go.Figure(go.Pie(
                labels=rc["risk"], values=rc["count"],
                hole=0.55,
                marker=dict(colors=[rcolors.get(str(r).upper(), BLUE) for r in rc["risk"]]),
                textinfo="label+percent+value", textfont=dict(size=12),
            ))
            apply_dark(fig_r, "Stockout Risk Level Distribution", height=320)
            st.plotly_chart(fig_r, use_container_width=True)

    # ── Utilisation heatmap by state & fuel ──────────────────────────────────
    st.markdown('<div class="section-header">🗺️ Tank Utilisation by State & Fuel Type</div>',
                unsafe_allow_html=True)
    if not tank.empty:
        pv = (tank.groupby(["state", "fuel_type"])["utilization_pct"]
              .mean().reset_index()
              .pivot(index="state", columns="fuel_type", values="utilization_pct")
              .fillna(0))
        fig_hm = go.Figure(go.Heatmap(
            z=pv.values,
            x=pv.columns.tolist(),
            y=pv.index.tolist(),
            colorscale=COLOR_SCALE_HEAT,
            text=[[f"{v:.1f}%" for v in row] for row in pv.values],
            texttemplate="%{text}", textfont=dict(size=11),
            colorbar=dict(title="Utilisation %", ticksuffix="%",
                          tickfont=dict(color=TEXT_MUTED)),
            hoverongaps=False,
        ))
        apply_dark(fig_hm, "Average Tank Utilisation % — State (rows) × Fuel Type (cols)", height=420)
        st.plotly_chart(fig_hm, use_container_width=True)

    # ── Low tank alerts + volume by fuel ─────────────────────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown('<div class="section-header">🔴 Low Tank Alerts</div>', unsafe_allow_html=True)
        if not inv.empty and "low_tank_flag" in inv.columns:
            low_df = (inv[inv["low_tank_flag"] == 1]
                      .sort_values("utilization_pct")
                      [["station_id", "state", "fuel_type",
                         "current_volume", "tank_capacity", "utilization_pct"]]
                      .copy())
            if not low_df.empty:
                low_df["utilization_pct"]  = low_df["utilization_pct"].apply(lambda x: f"{x:.1f}%")
                low_df["current_volume"]   = low_df["current_volume"].apply(fmt_liters)
                low_df["tank_capacity"]    = low_df["tank_capacity"].apply(fmt_liters)
                low_df.columns = [c.replace("_", " ").title() for c in low_df.columns]
                st.dataframe(low_df.reset_index(drop=True), use_container_width=True, height=300)
            else:
                st.success("✅ No low-tank alerts at this time.")

    with col_d:
        st.markdown('<div class="section-header">📦 Volume vs Capacity by Fuel Type</div>',
                    unsafe_allow_html=True)
        if not inv.empty:
            fv = inv.groupby("fuel_type").agg(
                current=("current_volume", "sum"),
                capacity=("tank_capacity", "sum"),
            ).reset_index()
            fv["available"] = fv["capacity"] - fv["current"]

            fig_stack = go.Figure()
            fig_stack.add_trace(go.Bar(
                name="Current Volume", x=fv["fuel_type"], y=fv["current"],
                marker_color=GREEN, opacity=0.85,
                text=[fmt_liters(v) for v in fv["current"]],
                textposition="inside",
            ))
            fig_stack.add_trace(go.Bar(
                name="Available Capacity", x=fv["fuel_type"], y=fv["available"],
                marker_color="rgba(255,255,255,0.08)",
                text=[fmt_liters(v) for v in fv["available"]],
                textposition="inside",
            ))
            fig_stack.update_layout(barmode="stack")
            apply_dark(fig_stack, "Current Volume vs Available Capacity by Fuel Type", height=300)
            st.plotly_chart(fig_stack, use_container_width=True)

    # ── High stockout risk stations ───────────────────────────────────────────
    st.markdown('<div class="section-header">🚨 High Stockout Risk Stations</div>',
                unsafe_allow_html=True)
    if not risk.empty:
        high = (risk[risk["stockout_risk"] == "HIGH"]
                .sort_values("utilization_pct")
                [["station_id", "state", "fuel_type",
                   "current_volume", "tank_capacity",
                   "utilization_pct", "stockout_risk"]]
                .copy())
        if not high.empty:
            high["utilization_pct"] = high["utilization_pct"].apply(lambda x: f"{x:.1f}%")
            high["current_volume"]  = high["current_volume"].apply(fmt_liters)
            high["tank_capacity"]   = high["tank_capacity"].apply(fmt_liters)
            high.columns = [c.replace("_", " ").title() for c in high.columns]
            st.dataframe(high.reset_index(drop=True), use_container_width=True, height=280)
        else:
            st.success("✅ No high stockout-risk stations at this time.")
