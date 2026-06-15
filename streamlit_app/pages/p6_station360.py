"""Page 6 — Station 360° & Nigeria Network Map."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.databricks import gold, silver
from utils.charts import (
    apply_dark, fmt_naira, fmt_liters,
    ORANGE, BLUE, GREEN, RED, AMBER, PURPLE, CYAN,
    PALETTE_ORANGE_BLUE, TEXT_MUTED, COLOR_SCALE_HEAT,
)

# Nigeria state centroids (lat, lon) — used for bubble heatmap
NIGERIA_CENTROIDS = {
    "Abia": (5.4527, 7.5248), "Adamawa": (9.3265, 12.3984),
    "Akwa Ibom": (5.0077, 7.8537), "Anambra": (6.2209, 6.9370),
    "Bauchi": (10.3158, 9.8442), "Bayelsa": (4.7719, 6.0699),
    "Benue": (7.3369, 8.7404), "Borno": (11.8333, 13.1500),
    "Cross River": (5.8702, 8.5988), "Delta": (5.7040, 5.9328),
    "Ebonyi": (6.2649, 8.0137), "Edo": (6.3350, 5.6037),
    "Ekiti": (7.7190, 5.3110), "Enugu": (6.4584, 7.5464),
    "FCT": (8.8940, 7.1858), "Gombe": (10.2791, 11.1670),
    "Imo": (5.4929, 7.0259), "Jigawa": (12.2280, 9.5616),
    "Kaduna": (10.5264, 7.4385), "Kano": (12.0022, 8.5920),
    "Katsina": (12.9816, 7.6183), "Kebbi": (11.4943, 4.2333),
    "Kogi": (7.7337, 6.6906), "Kwara": (8.9669, 4.3874),
    "Lagos": (6.5244, 3.3792), "Nasarawa": (8.5380, 8.3222),
    "Niger": (9.9309, 5.5983), "Ogun": (6.9980, 3.4737),
    "Ondo": (7.2500, 5.2000), "Osun": (7.5629, 4.5200),
    "Oyo": (7.8500, 3.9350), "Plateau": (9.2182, 9.5179),
    "Rivers": (4.8396, 6.9112), "Sokoto": (13.0059, 5.2476),
    "Taraba": (7.9993, 10.7744), "Yobe": (12.2939, 11.4390),
    "Zamfara": (12.1220, 6.2236),
}


def render():
    st.markdown("""
    <div class="page-title">📡 Station 360° & Nigeria Network Map</div>
    <div class="page-subtitle">
        Geospatial intelligence — station density heatmap, individual station deep-dive, and complete operational view
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    with st.spinner("Loading station network data…"):
        try:
            stations  = silver("silver_stations")
            stn_rev   = gold("gold_station_revenue")
            inv       = gold("gold_inventory_position")
            health    = gold("gold_pump_health")
            stn_fraud = gold("gold_fraud_station_ranking")
            maint     = gold("gold_maintenance_scores")
        except Exception as e:
            st.error(f"Connection error: {e}")
            return

    # ── KPIs ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Network Overview</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    total_stn   = len(stations) if not stations.empty else 0
    states_cov  = stations["state"].nunique() if not stations.empty else 0
    total_pumps = int(stations["pump_count"].sum()) if not stations.empty else 0
    total_rev   = stn_rev["total_revenue"].sum() if not stn_rev.empty else 0
    avg_hlth    = health["health_score"].mean() if not health.empty else 0

    c1.metric("Total Stations",    total_stn)
    c2.metric("States Covered",    states_cov)
    c3.metric("Total Pumps",       f"{total_pumps:,}")
    c4.metric("Network Revenue",   fmt_naira(total_rev))
    c5.metric("Avg Pump Health",   f"{avg_hlth:.1f}/100")

    st.markdown("<br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # NIGERIA MAP — 3 tabs
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-header">🇳🇬 Nigeria Station Network Map</div>',
                unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📍 Station Scatter Map", "🔥 State Density Heatmap",
                                  "📊 State-Level Analytics"])

    with tab1:
        if not stations.empty and "latitude" in stations.columns:
            map_df = stations.copy()
            if not stn_rev.empty:
                map_df = map_df.merge(
                    stn_rev[["station_id", "total_revenue", "liters_sold"]],
                    on="station_id", how="left"
                )
            if not stn_fraud.empty:
                map_df = map_df.merge(
                    stn_fraud[["station_id", "fraud_events", "total_fraud_loss"]],
                    on="station_id", how="left"
                )

            color_opts = [c for c in ["fraud_risk", "total_revenue", "fraud_events", "pump_count"]
                          if c in map_df.columns]
            color_by = st.selectbox("Color stations by", color_opts, key="scat_color")

            map_df["_size"] = map_df["pump_count"].fillna(4).clip(lower=2)

            fig_map = px.scatter_mapbox(
                map_df.dropna(subset=["latitude", "longitude"]),
                lat="latitude", lon="longitude",
                color=color_by,
                size="_size",
                size_max=18,
                hover_name="station_id",
                hover_data={"state": True, "pump_count": True,
                            "latitude": False, "longitude": False, "_size": False},
                color_continuous_scale=COLOR_SCALE_HEAT,
                mapbox_style="carto-darkmatter",
                zoom=5.2,
                center={"lat": 8.5, "lon": 8.0},
                opacity=0.9, height=580,
            )
            fig_map.update_layout(
                paper_bgcolor="#0f172a",
                margin=dict(l=0, r=0, t=0, b=0),
                coloraxis_colorbar=dict(
                    title=color_by.replace("_", " ").title(),
                    tickfont=dict(color=TEXT_MUTED),
                    title_font=dict(color=TEXT_MUTED),
                ),
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("Station coordinate data not available in silver layer.")

    with tab2:
        if not stations.empty:
            state_agg = stations.groupby("state").agg(
                station_count=("station_id", "count"),
                pump_count=("pump_count", "sum"),
                avg_fraud_risk=("fraud_risk", "mean"),
                pms_cap=("pms_capacity", "sum"),
                ago_cap=("ago_capacity", "sum"),
            ).reset_index()

            state_agg["lat"] = state_agg["state"].map(
                lambda s: NIGERIA_CENTROIDS.get(s, (9.0820, 8.6753))[0])
            state_agg["lon"] = state_agg["state"].map(
                lambda s: NIGERIA_CENTROIDS.get(s, (9.0820, 8.6753))[1])

            heat_opts = ["station_count", "pump_count", "avg_fraud_risk", "pms_cap", "ago_cap"]
            heat_metric = st.selectbox("Heatmap Metric", heat_opts, key="heat_m")

            fig_heat = px.scatter_mapbox(
                state_agg,
                lat="lat", lon="lon",
                size=heat_metric,
                color=heat_metric,
                hover_name="state",
                hover_data={"station_count": True, "pump_count": True,
                             "lat": False, "lon": False},
                color_continuous_scale=COLOR_SCALE_HEAT,
                size_max=60,
                mapbox_style="carto-darkmatter",
                zoom=4.8,
                center={"lat": 9.5, "lon": 8.4},
                opacity=0.85, height=580,
                text="state",
            )
            fig_heat.update_traces(textposition="top center",
                                   textfont=dict(size=10, color="#f8fafc"))
            fig_heat.update_layout(
                paper_bgcolor="#0f172a",
                margin=dict(l=0, r=0, t=0, b=0),
                coloraxis_colorbar=dict(
                    title=heat_metric.replace("_", " ").title(),
                    tickfont=dict(color=TEXT_MUTED),
                    title_font=dict(color=TEXT_MUTED),
                ),
            )
            st.plotly_chart(fig_heat, use_container_width=True)

    with tab3:
        if not stations.empty:
            state_stats = stations.groupby("state").agg(
                stations=("station_id", "count"),
                pumps=("pump_count", "sum"),
                avg_fraud=("fraud_risk", "mean"),
            ).reset_index().sort_values("stations", ascending=False)

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                fig_sb = go.Figure(go.Bar(
                    x=state_stats["state"], y=state_stats["stations"],
                    marker=dict(color=state_stats["stations"],
                                colorscale=COLOR_SCALE_HEAT, showscale=False),
                    text=state_stats["stations"], textposition="outside",
                ))
                apply_dark(fig_sb, "Station Count by State", height=380)
                fig_sb.update_xaxes(tickangle=-45)
                st.plotly_chart(fig_sb, use_container_width=True)

            with col_s2:
                fig_sb2 = go.Figure(go.Bar(
                    x=state_stats["state"], y=state_stats["pumps"],
                    marker=dict(color=state_stats["pumps"],
                                colorscale=[[0, "#1e3a6e"], [1, ORANGE]], showscale=False),
                    text=state_stats["pumps"], textposition="outside",
                ))
                apply_dark(fig_sb2, "Total Pump Count by State", height=380)
                fig_sb2.update_xaxes(tickangle=-45)
                st.plotly_chart(fig_sb2, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # STATION 360° DEEP-DIVE
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">🔍 Station 360° Deep-Dive</div>',
                unsafe_allow_html=True)

    if not stations.empty:
        all_ids = sorted(stations["station_id"].astype(str).unique().tolist())
        selected = st.selectbox("Select a Station", all_ids)

        info = stations[stations["station_id"].astype(str) == selected]
        row  = info.iloc[0] if not info.empty else {}

        rev_r   = stn_rev[stn_rev["station_id"].astype(str) == selected]   if not stn_rev.empty   else pd.DataFrame()
        fraud_r = stn_fraud[stn_fraud["station_id"].astype(str) == selected] if not stn_fraud.empty else pd.DataFrame()
        maint_r = maint[maint["station_id"].astype(str) == selected]        if not maint.empty     else pd.DataFrame()
        inv_r   = inv[inv["station_id"].astype(str) == selected]            if not inv.empty       else pd.DataFrame()
        pump_r  = health[health["station_id"].astype(str) == selected]      if not health.empty    else pd.DataFrame()

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0f172a,#1e293b);
                    border:1px solid rgba(249,115,22,0.3);border-radius:12px;
                    padding:16px 24px;margin-bottom:1rem;">
            <div style="font-size:1.1rem;font-weight:700;color:#f97316;">
                📍 {selected}
            </div>
            <div style="color:#64748b;font-size:0.82rem;margin-top:6px;">
                State: <b style="color:#94a3b8">{row.get('state','N/A')}</b> &nbsp;|&nbsp;
                Pumps: <b style="color:#94a3b8">{row.get('pump_count','N/A')}</b> &nbsp;|&nbsp;
                Fraud Risk Score: <b style="color:#94a3b8">{float(row.get('fraud_risk',0)):.2f}</b> &nbsp;|&nbsp;
                Lat: <b style="color:#94a3b8">{float(row.get('latitude',0)):.4f}</b> &nbsp;|&nbsp;
                Lon: <b style="color:#94a3b8">{float(row.get('longitude',0)):.4f}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        d1, d2, d3, d4, d5 = st.columns(5)
        d1.metric("Revenue",      fmt_naira(float(rev_r["total_revenue"].values[0]))   if not rev_r.empty   else "N/A")
        d2.metric("Liters Sold",  fmt_liters(float(rev_r["liters_sold"].values[0]))    if not rev_r.empty   else "N/A")
        d3.metric("Fraud Loss",   fmt_naira(float(fraud_r["total_fraud_loss"].values[0])) if not fraud_r.empty else "₦0")
        d4.metric("Fraud Events", int(fraud_r["fraud_events"].values[0])               if not fraud_r.empty else 0)
        d5.metric("Avg Health",   f"{float(maint_r['avg_health_score'].values[0]):.1f}/100" if not maint_r.empty else "N/A")

        col_inv, col_pump = st.columns(2)

        with col_inv:
            st.markdown("**🛢️ Tank Inventory by Fuel Type**")
            if not inv_r.empty:
                fig_inv = go.Figure()
                for _, r in inv_r.iterrows():
                    pct   = float(r["utilization_pct"])
                    color = GREEN if pct > 50 else (AMBER if pct > 20 else RED)
                    fig_inv.add_trace(go.Bar(
                        name=r["fuel_type"], x=[r["fuel_type"]], y=[r["current_volume"]],
                        marker_color=color,
                        text=[f"{pct:.1f}%"], textposition="inside",
                    ))
                apply_dark(fig_inv, "Current Volume by Fuel Type (% = utilisation)", height=300)
                st.plotly_chart(fig_inv, use_container_width=True)
            else:
                st.info("No inventory data for this station.")

        with col_pump:
            st.markdown("**⚙️ Individual Pump Health Scores**")
            if not pump_r.empty:
                fig_pump = go.Figure(go.Bar(
                    x=pump_r["pump_id"].astype(str),
                    y=pump_r["health_score"],
                    marker=dict(
                        color=pump_r["health_score"],
                        colorscale=[[0, RED], [0.4, AMBER], [0.7, ORANGE], [1, GREEN]],
                        showscale=False,
                    ),
                    text=[f"{v:.0f}" for v in pump_r["health_score"]],
                    textposition="outside",
                ))
                # Mark failed pumps with X
                if "failure_flag" in pump_r.columns:
                    failed = pump_r[pump_r["failure_flag"] == True]
                    if not failed.empty:
                        fig_pump.add_trace(go.Scatter(
                            x=failed["pump_id"].astype(str),
                            y=failed["health_score"] + 3,
                            mode="markers",
                            marker=dict(symbol="x", size=14, color=RED, line=dict(width=2)),
                            name="Failed",
                        ))
                apply_dark(fig_pump, "Pump Health Score per Unit", height=300)
                fig_pump.update_yaxes(range=[0, 115])
                st.plotly_chart(fig_pump, use_container_width=True)
            else:
                st.info("No pump data for this station.")
