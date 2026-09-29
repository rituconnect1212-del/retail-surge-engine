import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from engine import calculate_surge_and_depletion
from inventory_db import INITIAL_INVENTORY

# Page Setup: Wide mode and clean dark terminal aesthetic
st.set_page_config(
    page_title="NEXUS // Dark-Store Algorithmic Command",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;800&family=Plus+Jakarta+Sans:wght@300;500;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stMetric {
        background: rgba(18, 24, 38, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(4px);
    }
    
    .status-badge-crit {
        background: linear-gradient(135deg, #ff4b4b22, #ff4b4b44);
        border: 1px solid #ff4b4b;
        color: #ff4b4b;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.8rem;
        display: inline-block;
        animation: pulse 1.8s infinite;
    }
    
    .status-badge-norm {
        background: linear-gradient(135deg, #00cc9622, #00cc9644);
        border: 1px solid #00cc96;
        color: #00cc96;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.8rem;
        display: inline-block;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.6); }
        70% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
    }
</style>
""", unsafe_allow_html=True)

# Top Bar / Branding
top_col1, top_col2 = st.columns([3, 1])
with top_col1:
    st.markdown("### ⚡ **NEXUS // REAL-TIME DARK-STORE ARBITRAGE SYSTEM**")
    st.caption("Algorithmic Surge Engine • Dynamic Stockout Prevention • High-Frequency Retail Margin Arbitrage")
with top_col2:
    st.markdown("""
        <div style='text-align: right; padding-top: 10px;'>
            <span style='color: #00CC96; font-weight: 700;'>● LIVE TELEMETRY</span><br>
            <span style='font-family: monospace; color: #888;'>NODE: HYD-WEST-04</span>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- SIDEBAR INTERACTIVE ENGINE ---
st.sidebar.markdown("### 🎛️ **CRISIS SIMULATION CONTROLLER**")
st.sidebar.caption("Trigger macro-demand shocks to test real-time elasticity response.")

event_type = st.sidebar.selectbox(
    "Select Trigger Event",
    [
        "🟢 Normal Baseline Operations",
        "⛈️ Flash Monsoon Downpour (Hitec City)",
        "🏏 IPL Final Super-Over Spike",
        "🎉 Diwali / New Year Eve Peak Midnight"
    ]
)

velocity_slider = st.sidebar.slider("Synthetic Demand Surge Factor (%)", 0, 500, 180, 20)
elasticity_sensitivity = st.sidebar.slider("Surge Aggressiveness Index (α)", 0.2, 1.0, 0.6, 0.05)

# Multiplier Logic
scenario_weights = {
    "🟢 Normal Baseline Operations": 1.0,
    "⛈️ Flash Monsoon Downpour (Hitec City)": 3.2,
    "🏏 IPL Final Super-Over Spike": 2.4,
    "🎉 Diwali / New Year Eve Peak Midnight": 3.8
}
active_demand_mult = round((1 + (velocity_slider / 100)) * scenario_weights[event_type], 2)

st.sidebar.divider()
st.sidebar.markdown(f"""
**System State:**
- Active Demand Velocity: `{active_demand_mult}x`
- Surge Alpha: `{elasticity_sensitivity}`
- Dark Store Capacity: `88.4%`
""")

# --- RUN CALCULATION ---
results = []
for _, row in INITIAL_INVENTORY.iterrows():
    # Category bias
    bias = 1.0
    if "Monsoon" in event_type and "Umbrella" in row["name"]:
        bias = 2.4
    elif ("IPL" in event_type or "Diwali" in event_type) and ("Drinks" in row["name"] or "Noodles" in row["name"]):
        bias = 2.1
        
    current_velocity = round(0.6 * active_demand_mult * bias, 2)
    
    # Calculate metrics with custom sensitivity
    metrics = calculate_surge_and_depletion(
        current_stock=row["current_stock"],
        safety_stock=row["safety_stock"],
        orders_per_min=current_velocity,
        base_price=row["base_price"],
        lead_time_min=row["restock_lead_time_min"]
    )
    
    # Adjust dynamic surge based on custom elasticity index
    scarcity_ratio = max(0.0, (row["restock_lead_time_min"] - metrics["time_to_exhaust_min"]) / row["restock_lead_time_min"]) if metrics["time_to_exhaust_min"] < row["restock_lead_time_min"] else 0.0
    custom_surge = round(1.0 + (elasticity_sensitivity * scarcity_ratio), 2) if metrics["risk_level"] == "CRITICAL" else metrics["surge_multiplier"]
    custom_price = round(row["base_price"] * custom_surge, 1)
    custom_margin = round(custom_price - row["base_price"], 1)

    results.append({
        "Product": row["name"],
        "Stock Left": row["current_stock"],
        "Order Rate (req/min)": current_velocity,
        "Min to Depletion": metrics["time_to_exhaust_min"],
        "Restock Window (Min)": row["restock_lead_time_min"],
        "Risk Status": metrics["risk_level"],
        "Base (₹)": row["base_price"],
        "Surge Multiplier": custom_surge,
        "Dynamic Price (₹)": custom_price,
        "Net Arbitrage (₹)": custom_margin
    })

df = pd.DataFrame(results)

# --- 4 TOP EXECUTIVE METRICS ---
critical_skus = len(df[df["Risk Status"] == "CRITICAL"])
total_margin_unlocked = round(df["Net Arbitrage (₹)"].sum() * 12, 0) # Estimated hourly delta

m1, m2, m3, m4 = st.columns(4)
m1.metric("Current Demand Intensity", f"{active_demand_mult}x", delta=f"{velocity_slider}% Influx")
m2.metric("Critical Stockout Alerts", f"{critical_skus} SKUs", delta="Immediate Action" if critical_skus > 0 else "Nominal", delta_color="inverse")
m3.metric("Peak Surge Applied", f"{df['Surge Multiplier'].max()}x", delta="Elastic Throttling Active")
m4.metric("Est. Margin Capture / Hr", f"+₹{total_margin_unlocked:,.0f}", delta="Pure Bottomline Boost")

st.write("")

# --- TABS FOR WORKFLOW NAVIGATION ---
tab_ops, tab_geo, tab_editor = st.tabs(["⚡ REAL-TIME MONITOR", "🗺️ HYPER-LOCAL SURGE MAP", "🛠️ LIVE INVENTORY ADJUSTER"])

with tab_ops:
    c1, c2 = st.columns([3, 2])
    
    with c1:
        st.markdown("##### **Depletion Velocity vs. Restock Lead Time**")
        fig_bar = go.Figure()
        
        fig_bar.add_trace(go.Bar(
            x=df["Product"],
            y=df["Min to Depletion"],
            name="Minutes to Zero Inventory",
            marker=dict(color=['#FF4B4B' if s == 'CRITICAL' else '#00CC96' for s in df["Risk Status"]]),
            text=df["Min to Depletion"],
            textposition='auto'
        ))
        
        fig_bar.add_trace(go.Scatter(
            x=df["Product"],
            y=df["Restock Window (Min)"],
            name="Supplier Delivery Threshold",
            mode='lines+markers',
            line=dict(color='#FFAA00', width=3, dash='dash')
        ))
        
        fig_bar.update_layout(
            template="plotly_dark",
            height=340,
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with c2:
        st.markdown("##### **Dynamic Price Elasticity Breakdown**")
        fig_scatter = px.scatter(
            df,
            x="Order Rate (req/min)",
            y="Dynamic Price (₹)",
            size="Net Arbitrage (₹)",
            color="Risk Status",
            hover_name="Product",
            color_discrete_map={"CRITICAL": "#FF4B4B", "MODERATE": "#FFAA00", "NORMAL": "#00CC96"},
            template="plotly_dark"
        )
        fig_scatter.update_layout(height=340, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab_geo:
    st.markdown("##### **Hyper-Local Delivery Radius & Surge Heatmap (Dark Store #104)**")
    
    # Mock Dark Store coordinates centered in Hyderabad (Hitec City / Madhapur)
    map_data = pd.DataFrame({
        'lat': [17.4435, 17.4485, 17.4380, 17.4520, 17.4350],
        'lon': [78.3772, 78.3840, 78.3710, 78.3900, 78.3650],
        'Zone': ["Dark Store Hub", "Zone Alpha (High Surge)", "Zone Beta (Medium)", "Zone Gamma (Critical)", "Zone Delta"],
        'Surge': [1.0, df['Surge Multiplier'].max(), 1.2, df['Surge Multiplier'].max(), 1.1]
    })
    
    st.map(map_data, latitude=17.4435, longitude=78.3772, zoom=13)
    st.caption("📍 Geofenced micro-zones dynamically adjust delivery surge fees based on rider availability and local order velocity.")

with tab_editor:
    st.markdown("##### **Direct Warehouse SKU Overrides**")
    st.caption("Change stock levels or base prices directly in the grid below to stress-test custom scenarios:")
    
    edited_data = st.data_editor(
        df[["Product", "Stock Left", "Order Rate (req/min)", "Base (₹)", "Dynamic Price (₹)", "Surge Multiplier", "Risk Status"]],
        use_container_width=True,
        hide_index=True
    )

# Bottom Explainer Banner
st.divider()
st.markdown("""
<div style='background: rgba(255, 255, 255, 0.03); padding: 15px; border-radius: 8px; border-left: 4px solid #636EFA;'>
    <b>🧠 Algorithmic Thesis:</b> When demand velocity shrinks depletion time below restock lead time, linear pricing leads to guaranteed stockouts. 
    By introducing real-time dynamic pricing elasticity, low-urgency buyers naturally postpone purchases, buffering stock for mission-critical orders while capturing peak unit margin.
</div>
""", unsafe_allow_html=True)
