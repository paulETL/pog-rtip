"""Page 1 — Executive Command Center."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.databricks import gold
from utils.charts import (
    apply_dark, fmt_naira, fmt_liters,
    ORANGE, BLUE, GREEN, RED, AMBER, PURPLE, CYAN,
    TEXT_MUTED,
)


def render():
    st.markdown("""
    <div class="page-title">🏠 Executive Command Center</div>
    <div class="page-subtitle">Real-time operational overview across all stations — refreshes every 60 seconds</div>
    """, unsafe_allow_html=True)

    col_refresh, _ = st.columns([1, 9])
    with col_refresh:
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Load data ────────────────────────────────────────────────────────────
    with st.spinner("Loading executive metrics…"):
        try:
            exec_df     = gold("gold_executive_command_center")
            sales_d     = gold("gold_sales_daily")
            sales_h     = gold("gold_sales_hourly")
            station_rev = gold("gold_station_revenue")
            fraud_ev    = gold("gold_fraud_events")
            fraud_losses = gold("gold_fraud_losses")
        except Exception as e:
            st.error(f"Databricks connection error: {e}")
            st.info("Ensure your `.streamlit/secrets.toml` is configured.")
            return

    # ── KPI cards ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Key Performance Indicators — Today</div>',
                unsafe_allow_html=True)

    row = exec_df.iloc[-1] if not exec_df.empty else {}

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("💰 Revenue Today",       fmt_naira(float(row.get("revenue_today", 0))))
    c2.metric("🛢️ Liters Sold Today",   fmt_liters(float(row.get("liters_sold_today", 0))))
    c3.metric("🏪 Active Stations",      int(row.get("active_stations", 0)))
    c4.metric("🚨 Fraud Loss Est.",      fmt_naira(float(row.get("fraud_loss_estimate", 0))))
    c5.metric("⚠️ Low Tank Count",       int(row.get("low_tank_count", 0)))
    c6.metric("🔧 Failed Pumps",         int(row.get("failed_pump_count", 0)))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Sales trend + hourly bar ─────────────────────────────────────────────
    st.markdown('<div class="section-header">📈 Sales Trends</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 2])

    with col_a:
        if not sales_d.empty:
            # Parse date properly — just date, not datetime
            sales_d["sales_date"] = pd.to_datetime(
                sales_d["sales_date"].astype(str).str[:10], format="%Y-%m-%d"
            )
            daily = (sales_d.groupby("sales_date")
                     .agg(total_revenue=("total_revenue", "sum"),
                          liters_sold=("liters_sold", "sum"))
                     .reset_index().sort_values("sales_date"))

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily["sales_date"], y=daily["total_revenue"],
                mode="lines+markers", name="Revenue (₦)",
                line=dict(color=ORANGE, width=2.5),
                marker=dict(size=6, color=ORANGE),
                fill="tozeroy", fillcolor="rgba(249,115,22,0.08)",
            ))
            fig.add_trace(go.Scatter(
                x=daily["sales_date"], y=daily["liters_sold"],
                mode="lines+markers", name="Liters Sold",
                line=dict(color=BLUE, width=2, dash="dot"),
                marker=dict(size=5, color=BLUE),
                yaxis="y2",
            ))
            fig.update_layout(
                yaxis2=dict(overlaying="y", side="right",
                            tickfont=dict(color=TEXT_MUTED, size=11), showgrid=False),
                xaxis=dict(type="date", tickformat="%d %b"),
            )
            apply_dark(fig, "Daily Revenue vs Liters Sold", height=320)
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        if not sales_h.empty:
            sales_h["sales_hour"] = pd.to_numeric(sales_h["sales_hour"], errors="coerce")
            hourly = (sales_h.groupby("sales_hour")["total_revenue"]
                      .mean().reset_index().sort_values("sales_hour"))

            fig2 = go.Figure(go.Bar(
                x=hourly["sales_hour"],
                y=hourly["total_revenue"],
                marker=dict(
                    color=hourly["total_revenue"],
                    colorscale=[[0, "#1e293b"], [0.4, "#c2410c"], [1, ORANGE]],
                    showscale=False,
                ),
                text=[fmt_naira(v) for v in hourly["total_revenue"]],
                textposition="outside", textfont=dict(size=9),
            ))
            apply_dark(fig2, "Avg Revenue by Hour of Day", height=320)
            fig2.update_xaxes(title_text="Hour", dtick=2)
            fig2.update_yaxes(title_text="Avg Revenue (₦)")
            st.plotly_chart(fig2, use_container_width=True)

    # ── Top/Bottom stations ──────────────────────────────────────────────────
    st.markdown('<div class="section-header">🏆 Station Performance League Table</div>',
                unsafe_allow_html=True)
    col_t, col_b2 = st.columns(2)

    with col_t:
        st.markdown("**🥇 Top 10 Stations by Revenue**")
        if not station_rev.empty:
            top10 = station_rev.nlargest(10, "total_revenue")
            fig3 = go.Figure(go.Bar(
                x=top10["total_revenue"],
                y=top10["station_id"].astype(str),
                orientation="h",
                marker=dict(color=GREEN,
                            line=dict(color="rgba(34,197,94,0.3)", width=1)),
                text=[fmt_naira(v) for v in top10["total_revenue"]],
                textposition="outside",
            ))
            apply_dark(fig3, "", height=360)
            fig3.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig3, use_container_width=True)

    with col_b2:
        st.markdown("**⛔ Bottom 10 Stations by Revenue**")
        if not station_rev.empty:
            bot10 = station_rev.nsmallest(10, "total_revenue")
            fig4 = go.Figure(go.Bar(
                x=bot10["total_revenue"],
                y=bot10["station_id"].astype(str),
                orientation="h",
                marker=dict(color=RED,
                            line=dict(color="rgba(239,68,68,0.3)", width=1)),
                text=[fmt_naira(v) for v in bot10["total_revenue"]],
                textposition="outside",
            ))
            apply_dark(fig4, "", height=360)
            fig4.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig4, use_container_width=True)

    # ── Fraud pulse ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🚨 Fraud Activity Pulse</div>',
                unsafe_allow_html=True)
    col_f1, col_f2 = st.columns([2, 1])

    with col_f1:
        # Use gold_fraud_losses for clean daily aggregation (avoids timestamp issues)
        if not fraud_losses.empty:
            fraud_losses["fraud_date"] = pd.to_datetime(
                fraud_losses["fraud_date"].astype(str).str[:10], format="%Y-%m-%d"
            )
            fraud_losses = fraud_losses.sort_values("fraud_date")

            fig5 = go.Figure()
            fig5.add_trace(go.Bar(
                x=fraud_losses["fraud_date"], y=fraud_losses["fraud_events"],
                name="Fraud Events", marker_color=RED, opacity=0.85,
            ))
            fig5.add_trace(go.Scatter(
                x=fraud_losses["fraud_date"], y=fraud_losses["total_fraud_loss"],
                name="Estimated Loss (₦)", line=dict(color=AMBER, width=2.5),
                mode="lines+markers", marker=dict(size=6),
                yaxis="y2",
            ))
            fig5.update_layout(
                yaxis2=dict(overlaying="y", side="right", showgrid=False,
                            tickfont=dict(color=TEXT_MUTED, size=11)),
                xaxis=dict(type="date", tickformat="%d %b"),
            )
            apply_dark(fig5, "Daily Fraud Events & Estimated Loss", height=300)
            st.plotly_chart(fig5, use_container_width=True)
        elif not fraud_ev.empty:
            # Fallback: parse event_time to date
            fraud_ev["event_time"] = pd.to_datetime(fraud_ev["event_time"], errors="coerce")
            fraud_ev["date"] = fraud_ev["event_time"].dt.date
            daily_fraud = (fraud_ev[fraud_ev["fraud_flag"] == True]
                           .groupby("date")
                           .agg(events=("fraud_flag", "count"),
                                loss=("estimated_loss", "sum"))
                           .reset_index())
            if not daily_fraud.empty:
                fig5b = go.Figure()
                fig5b.add_trace(go.Bar(x=daily_fraud["date"], y=daily_fraud["events"],
                                       name="Fraud Events", marker_color=RED, opacity=0.85))
                fig5b.add_trace(go.Scatter(x=daily_fraud["date"], y=daily_fraud["loss"],
                                           name="Loss (₦)", line=dict(color=AMBER, width=2),
                                           mode="lines+markers", yaxis="y2"))
                fig5b.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False,
                                                tickfont=dict(color=TEXT_MUTED, size=11)))
                apply_dark(fig5b, "Daily Fraud Events & Estimated Loss", height=300)
                st.plotly_chart(fig5b, use_container_width=True)

    with col_f2:
        if not fraud_ev.empty:
            sev_counts = fraud_ev["fraud_severity"].value_counts().reset_index()
            sev_counts.columns = ["severity", "count"]
            sev_colors = {"LOW": GREEN, "MEDIUM": AMBER, "HIGH": RED, "CRITICAL": PURPLE}
            colors = [sev_colors.get(str(s).upper(), ORANGE) for s in sev_counts["severity"]]
            fig6 = go.Figure(go.Pie(
                labels=sev_counts["severity"], values=sev_counts["count"],
                hole=0.55, marker=dict(colors=colors),
                textinfo="label+percent", textfont=dict(size=12),
            ))
            apply_dark(fig6, "Fraud Severity Breakdown", height=300)
            st.plotly_chart(fig6, use_container_width=True)
