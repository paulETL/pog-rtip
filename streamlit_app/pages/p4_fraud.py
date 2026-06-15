"""Page 4 — Fraud & Loss Monitoring."""
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
    <div class="page-title">🚨 Fraud & Loss Monitoring</div>
    <div class="page-subtitle">
        AI-powered fraud detection — variance analysis, attendant flagging, and station risk ranking
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    with st.spinner("Loading fraud data…"):
        try:
            events   = gold("gold_fraud_events")
            losses   = gold("gold_fraud_losses")
            stn_rank = gold("gold_fraud_station_ranking")
            att_fr   = gold("gold_fraud_attendants")
        except Exception as e:
            st.error(f"Connection error: {e}")
            return

    # ── Parse dates properly ──────────────────────────────────────────────────
    if not losses.empty:
        losses["fraud_date"] = pd.to_datetime(
            losses["fraud_date"].astype(str).str[:10], format="%Y-%m-%d"
        )
        losses = losses.sort_values("fraud_date")

    if not events.empty:
        # event_time has microsecond timestamps — truncate to date for grouping
        events["event_time"] = pd.to_datetime(events["event_time"], errors="coerce")
        events["event_date"] = events["event_time"].dt.date

    # ── KPIs ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🔍 Fraud Intelligence Summary</div>',
                unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)

    if not losses.empty:
        c1.metric("Total Fraud Events",   f"{int(losses['fraud_events'].sum()):,}")
        c2.metric("Total Fraud Loss",     fmt_naira(losses["total_fraud_loss"].sum()))
        c3.metric("Under-Dispensed (L)",  fmt_liters(losses["total_under_dispensed_liters"].sum()))

    if not events.empty:
        fraud_only = events[events["fraud_flag"] == True]
        c4.metric("Stations w/ Fraud",   fraud_only["station_id"].nunique())
        c5.metric("Flagged Attendants",  fraud_only["attendant_id"].nunique())

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Daily fraud trend (from gold_fraud_losses — clean aggregated table) ──
    st.markdown('<div class="section-header">📅 Daily Fraud Trend</div>', unsafe_allow_html=True)
    if not losses.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=losses["fraud_date"], y=losses["fraud_events"],
            name="Fraud Events", marker_color=RED, opacity=0.8,
        ))
        fig.add_trace(go.Scatter(
            x=losses["fraud_date"], y=losses["total_fraud_loss"],
            name="Total Loss (₦)", line=dict(color=AMBER, width=2.5),
            mode="lines+markers", marker=dict(size=7),
            yaxis="y2",
        ))
        fig.add_trace(go.Scatter(
            x=losses["fraud_date"], y=losses["total_under_dispensed_liters"],
            name="Under-Dispensed (L)", line=dict(color=PURPLE, width=2, dash="dot"),
            mode="lines+markers", marker=dict(size=5),
            yaxis="y2",
        ))
        fig.update_layout(
            yaxis2=dict(overlaying="y", side="right", showgrid=False,
                        tickfont=dict(color=TEXT_MUTED, size=11)),
            xaxis=dict(type="date", tickformat="%d %b %Y"),
        )
        apply_dark(fig, "Daily Fraud Events, Financial Loss & Under-Dispensed Volume", height=340)
        st.plotly_chart(fig, use_container_width=True)

    # ── State × Fuel heatmap + Variance violin ────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-header">🗺️ Fraud Loss by State & Fuel Type</div>',
                    unsafe_allow_html=True)
        if not events.empty:
            fraud_ev = events[events["fraud_flag"] == True].copy()
            if not fraud_ev.empty:
                hm = (fraud_ev.groupby(["state", "fuel_type"])["estimated_loss"]
                      .sum().reset_index()
                      .pivot(index="state", columns="fuel_type", values="estimated_loss")
                      .fillna(0))
                fig2 = go.Figure(go.Heatmap(
                    z=hm.values,
                    x=hm.columns.tolist(),
                    y=hm.index.tolist(),
                    colorscale=[[0, "#0c1a3d"], [0.5, "#7c2d12"], [1, RED]],
                    text=[[fmt_naira(v) for v in row] for row in hm.values],
                    texttemplate="%{text}",
                    textfont=dict(size=10),
                    colorbar=dict(title="Est. Loss", tickfont=dict(color=TEXT_MUTED)),
                    hoverongaps=False,
                ))
                apply_dark(fig2, "Estimated Fraud Loss — State × Fuel Type", height=380)
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No confirmed fraud events in current dataset.")

    with col_b:
        st.markdown('<div class="section-header">⚖️ Variance Distribution by Severity</div>',
                    unsafe_allow_html=True)
        if not events.empty and "variance_liters" in events.columns:
            fraud_ev2 = events[events["fraud_flag"] == True].copy()
            if not fraud_ev2.empty:
                fig3 = go.Figure()
                for sev, color in [("LOW", GREEN), ("MEDIUM", AMBER), ("HIGH", RED), ("CRITICAL", PURPLE)]:
                    sub = fraud_ev2[fraud_ev2["fraud_severity"] == sev]
                    if not sub.empty:
                        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                        fig3.add_trace(go.Violin(
                            y=sub["variance_liters"], name=sev,
                            box_visible=True, meanline_visible=True,
                            line_color=color,
                            fillcolor=f"rgba({r},{g},{b},0.2)",
                        ))
                apply_dark(fig3, "Variance (Litres) by Fraud Severity", height=380)
                fig3.update_yaxes(title_text="Variance Litres")
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No confirmed fraud events in current dataset.")

    # ── Station & Attendant rankings ─────────────────────────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown('<div class="section-header">🏪 Most Fraudulent Stations</div>',
                    unsafe_allow_html=True)
        if not stn_rank.empty:
            top_stn = stn_rank.nlargest(15, "total_fraud_loss")
            fig4 = go.Figure(go.Bar(
                x=top_stn["total_fraud_loss"],
                y=top_stn["station_id"].astype(str),
                orientation="h",
                marker=dict(color=top_stn["total_fraud_loss"],
                            colorscale=[[0, AMBER], [1, RED]], showscale=False),
                text=[fmt_naira(v) for v in top_stn["total_fraud_loss"]],
                textposition="outside",
            ))
            apply_dark(fig4, "Top 15 Stations by Fraud Loss", height=400)
            fig4.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig4, use_container_width=True)

    with col_d:
        st.markdown('<div class="section-header">👷 High-Risk Attendants</div>',
                    unsafe_allow_html=True)
        if not att_fr.empty:
            top_att = att_fr.nlargest(15, "total_fraud_loss")
            fig5 = go.Figure(go.Bar(
                x=top_att["total_fraud_loss"],
                y=top_att["attendant_id"].astype(str),
                orientation="h",
                marker=dict(color=top_att["total_fraud_loss"],
                            colorscale=[[0, "#7c2d12"], [1, RED]], showscale=False),
                text=[fmt_naira(v) for v in top_att["total_fraud_loss"]],
                textposition="outside",
            ))
            apply_dark(fig5, "Top 15 Attendants by Fraud Loss", height=400)
            fig5.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig5, use_container_width=True)

    # ── Recent fraud events feed ──────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 Recent Fraud Event Feed</div>',
                unsafe_allow_html=True)
    if not events.empty:
        display_cols = ["event_time", "station_id", "state", "attendant_id",
                        "pump_id", "fuel_type", "fraud_severity",
                        "variance_liters", "under_dispensed_liters", "estimated_loss"]
        display_cols = [c for c in display_cols if c in events.columns]
        recent = (events[events["fraud_flag"] == True]
                  .sort_values("event_time", ascending=False)
                  .head(50)[display_cols]
                  .copy())
        if not recent.empty:
            recent["estimated_loss"] = recent["estimated_loss"].apply(fmt_naira)
            recent.columns = [c.replace("_", " ").title() for c in recent.columns]
            st.dataframe(recent, use_container_width=True, height=350)
        else:
            st.info("No confirmed fraud events in current data window.")
