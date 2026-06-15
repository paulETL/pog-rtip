"""Page 2 — Revenue & Sales Analytics."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.databricks import gold
from utils.charts import (
    apply_dark, fmt_naira, fmt_liters,
    ORANGE, BLUE, GREEN, RED, AMBER, PURPLE, CYAN,
    PALETTE_ORANGE_BLUE, TEXT_MUTED,
)


def render():
    st.markdown("""
    <div class="page-title">💰 Revenue & Sales Analytics</div>
    <div class="page-subtitle">Deep-dive into revenue trends, fuel-type breakdown, and attendant performance</div>
    """, unsafe_allow_html=True)

    with st.expander("🔍 Filters", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            fuel_filter = st.multiselect("Fuel Type", ["PMS", "AGO", "LPG", "ATK"],
                                         default=["PMS", "AGO", "LPG", "ATK"])

    st.markdown("<hr>", unsafe_allow_html=True)

    with st.spinner("Loading sales data…"):
        try:
            sales_d  = gold("gold_sales_daily")
            sales_h  = gold("gold_sales_hourly")
            stn_rev  = gold("gold_station_revenue")
            att_perf = gold("gold_attendant_performance")
        except Exception as e:
            st.error(f"Connection error: {e}")
            return

    # Parse dates safely — strip to YYYY-MM-DD before parsing
    if not sales_d.empty:
        sales_d["sales_date"] = pd.to_datetime(
            sales_d["sales_date"].astype(str).str[:10], format="%Y-%m-%d"
        )
        if "fuel_type" in sales_d.columns:
            sales_d = sales_d[sales_d["fuel_type"].isin(fuel_filter)]

    if not sales_h.empty:
        sales_h["sales_hour"] = pd.to_numeric(sales_h["sales_hour"], errors="coerce")

    # ── KPIs ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Period Summary</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    if not sales_d.empty:
        total_rev = sales_d["total_revenue"].sum()
        total_lit = sales_d["liters_sold"].sum()
        total_txn = int(sales_d["transaction_count"].sum())
        avg_txn   = total_rev / total_txn if total_txn else 0
        c1.metric("Total Revenue",         fmt_naira(total_rev))
        c2.metric("Total Liters Sold",     fmt_liters(total_lit))
        c3.metric("Total Transactions",    f"{total_txn:,}")
        c4.metric("Avg Transaction Value", fmt_naira(avg_txn))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Daily revenue by fuel type ────────────────────────────────────────────
    st.markdown('<div class="section-header">📅 Daily Revenue by Fuel Type</div>',
                unsafe_allow_html=True)
    if not sales_d.empty:
        pivot = (sales_d.groupby(["sales_date", "fuel_type"])["total_revenue"]
                 .sum().reset_index())
        fig = px.bar(pivot, x="sales_date", y="total_revenue", color="fuel_type",
                     barmode="stack",
                     color_discrete_sequence=PALETTE_ORANGE_BLUE,
                     labels={"sales_date": "Date", "total_revenue": "Revenue (₦)",
                             "fuel_type": "Fuel Type"})
        apply_dark(fig, "", height=340)
        fig.update_xaxes(type="date", tickformat="%d %b %Y")
        st.plotly_chart(fig, use_container_width=True)

    # ── Hourly pattern + fuel share ──────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-header">⏰ Hourly Sales Pattern</div>',
                    unsafe_allow_html=True)
        if not sales_h.empty:
            hourly = (sales_h.groupby("sales_hour")
                      .agg(avg_rev=("total_revenue", "mean"),
                           avg_vol=("liters_sold", "mean"))
                      .reset_index().sort_values("sales_hour"))

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=hourly["sales_hour"], y=hourly["avg_rev"],
                mode="lines+markers", name="Avg Revenue (₦)",
                line=dict(color=ORANGE, width=2.5),
                marker=dict(size=7, color=ORANGE),
                fill="tozeroy", fillcolor="rgba(249,115,22,0.1)",
            ))
            fig2.add_trace(go.Scatter(
                x=hourly["sales_hour"], y=hourly["avg_vol"],
                mode="lines+markers", name="Avg Liters",
                line=dict(color=CYAN, width=2, dash="dot"),
                marker=dict(size=5, color=CYAN),
                yaxis="y2",
            ))
            fig2.update_layout(
                yaxis2=dict(overlaying="y", side="right", showgrid=False,
                            tickfont=dict(color=TEXT_MUTED, size=11)),
            )
            apply_dark(fig2, "Average Hourly Revenue vs Volume", height=340)
            fig2.update_xaxes(title_text="Hour of Day", dtick=2)
            st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">🛢️ Fuel Mix — Revenue Share</div>',
                    unsafe_allow_html=True)
        if not sales_d.empty:
            fuel_share = sales_d.groupby("fuel_type")["total_revenue"].sum().reset_index()
            fig3 = go.Figure(go.Pie(
                labels=fuel_share["fuel_type"],
                values=fuel_share["total_revenue"],
                hole=0.5,
                marker=dict(colors=PALETTE_ORANGE_BLUE),
                textinfo="label+percent",
                textfont=dict(size=13),
                hovertemplate="<b>%{label}</b><br>₦%{value:,.0f}<br>%{percent}<extra></extra>",
            ))
            apply_dark(fig3, "Revenue Share by Fuel Type", height=340)
            st.plotly_chart(fig3, use_container_width=True)

    # ── Station revenue ranking ───────────────────────────────────────────────
    st.markdown('<div class="section-header">🏪 Station Revenue Ranking</div>',
                unsafe_allow_html=True)
    if not stn_rev.empty:
        disp = stn_rev.sort_values("total_revenue", ascending=False).reset_index(drop=True).copy()
        disp.index += 1
        disp["total_revenue"]         = disp["total_revenue"].apply(fmt_naira)
        disp["liters_sold"]           = disp["liters_sold"].apply(fmt_liters)
        disp["avg_transaction_value"] = disp["avg_transaction_value"].apply(fmt_naira)
        disp.columns = [c.replace("_", " ").title() for c in disp.columns]
        st.dataframe(disp, use_container_width=True, height=300)

    # ── Attendant performance ────────────────────────────────────────────────
    st.markdown('<div class="section-header">👷 Attendant Performance Overview</div>',
                unsafe_allow_html=True)
    if not att_perf.empty:
        col_c, col_d = st.columns(2)
        with col_c:
            fig4 = px.scatter(
                att_perf,
                x="liters_sold", y="total_revenue",
                size="transaction_count",
                color="total_revenue",
                color_continuous_scale=[[0, "#0c1a3d"], [0.5, "#c2410c"], [1, ORANGE]],
                hover_data=["attendant_id", "station_id", "transaction_count"],
                labels={"liters_sold": "Liters Sold", "total_revenue": "Revenue (₦)"},
            )
            apply_dark(fig4, "Revenue vs Liters Sold (bubble = transaction count)", height=340)
            st.plotly_chart(fig4, use_container_width=True)

        with col_d:
            top_att = att_perf.nlargest(15, "total_revenue")
            fig5 = go.Figure(go.Bar(
                x=top_att["total_revenue"],
                y=top_att["attendant_id"].astype(str),
                orientation="h",
                marker=dict(color=top_att["total_revenue"],
                            colorscale=[[0, "#1e3a6e"], [1, ORANGE]], showscale=False),
                text=[fmt_naira(v) for v in top_att["total_revenue"]],
                textposition="outside",
            ))
            apply_dark(fig5, "Top 15 Attendants by Revenue", height=340)
            fig5.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig5, use_container_width=True)
