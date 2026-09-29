import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from engine import calculate_surge_and_depletion
from inventory_db import INITIAL_INVENTORY

# Configure broad, responsive layout
st.set_page_config(
    page_title="Retail Surge & Inventory Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header styling
st.title("⚡ Dynamic Inventory & Surge Arbitrage Engine")
st.markdown("##### Real-Time Operational Decision Support for Quick-Commerce Dark Stores")
st.write("---")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🕹️ Simulation Parameters")
st.sidebar.markdown("Use these controls to simulate external market shocks:")

event_type = st.sidebar.selectbox(
    "External Demand Event",
    ["Clear Skies (Normal)", "Sudden Heavy Downpour / Storm", "IPL Cricket Match Rush", "Festival / Late Night Peak"]
)

event_surge = st.sidebar.slider("Order Velocity Spike (%)", min_value=0, max_value=400, value=150, step=25)

# Calculate demand factor based on selections
weather_multipliers = {
    "Clear Skies (Normal)": 1.0,
    "Sudden Heavy Downpour / Storm": 2.5,
    "IPL Cricket Match Rush": 2.0,
    "Festival / Late Night Peak": 3.0
}
demand_factor = (1 + (event_surge / 100)) * weather_multipliers[event_type]

st.sidebar.info(f"**Current System Load:** {demand_factor:.1f}x baseline order velocity")

# --- ENGINE CALCULATION ---
results = []
for _, row in INITIAL_INVENTORY.iterrows():
    # If it's raining, umbrellas spike even harder; drinks spike in match/festival
    product_bias = 1.0
    if "Downpour" in event_type and "Umbrella" in row["name"]:
        product_bias = 2.0
    elif ("IPL" in event_type or "Festival" in event_type) and ("Drinks" in row["name"] or "Noodles" in row["name"]):
        product_bias = 1.8
        
    simulated_demand = round(0.5 * demand_factor * product_bias, 2)
    
    metrics = calculate_surge_and_depletion(
        current_stock=row["current_stock"],
        safety_stock=row["safety_stock"],
        orders_per_min=simulated_demand,
        base_price=row["base_price"],
        lead_time_min=row["restock_lead_time_min"]
    )
    
    results.append({
        "Product": row["name"],
        "Units Left": row["current_stock"],
        "Demand (orders/min)": simulated_demand,
        "Min to Stockout": metrics["time_to_exhaust_min"],
        "Restock Time (Min)": row["restock_lead_time_min"],
        "Status": metrics["risk_level"],
        "Base Price": row["base_price"],
        "Dynamic Price": metrics["dynamic_price"],
        "Surge Multiplier": f"{metrics['surge_multiplier']}x",
        "Arbitrage Margin/Unit": metrics["arbitrage_margin"]
    })

df_results = pd.DataFrame(results)

# --- TOP METRIC TILES ---
critical_count = len(df_results[df_results["Status"] == "CRITICAL"])
total_margin_boost = round(df_results["ArbitrageMargin" if "ArbitrageMargin" in df_results else "Arbitrage Margin/Unit"].sum(), 2)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Demand Velocity", f"{demand_factor:.1f}x Normal", delta=f"{event_surge}% Spike")
col2.metric("Critical SKUs", f"{critical_count} Items", delta="High Risk" if critical_count > 0 else "Optimal", delta_color="inverse")
col3.metric("Peak Surge Multiplier", df_results["Surge Multiplier"].max())
col4.metric("Avg Added Margin / Unit", f"+₹{round(df_results['Arbitrage Margin/Unit'].mean(), 1)}")

st.write("---")

# --- INTERACTIVE VISUALIZATION ---
st.subheader("📊 Stockout Exhaustion vs. Supplier Restock Lead Time")

# Create a clean side-by-side comparative bar chart using Plotly
fig = go.Figure()
fig.add_trace(go.Bar(
    x=df_results["Product"],
    y=df_results["Min to Stockout"],
    name="Time until Zero Stock (Min)",
    marker_color=['#FF4B4B' if status == 'CRITICAL' else '#00CC96' for status in df_results["Status"]]
))
fig.add_trace(go.Bar(
    x=df_results["Product"],
    y=df_results["Restock Time (Min)"],
    name="Supplier Restock Time (Min)",
    marker_color='#636EFA'
))

fig.update_layout(
    barmode='group',
    yaxis_title="Minutes",
    xaxis_title="",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    template="plotly_dark",
    height=380
)
st.plotly_chart(fig, use_container_width=True)

# --- INTERACTIVE SPREADSHEET (DATA EDITOR) ---
st.subheader("📋 Operational Inventory & Dynamic Pricing Grid")
st.caption("💡 Tap any cell in the table below to edit stock counts or base prices manually.")

# Using st.data_editor so visitors can edit values directly on screen
edited_df = st.data_editor(
    df_results,
    use_container_width=True,
    hide_index=True
)

st.success("✅ **Algorithmic Logic Summary:** Products showing red bars indicate the shelf will hit 0 before supply replenishment arrives. Dynamic surge pricing throttles excess order rate and locks in inventory for high-urgency buyers.")

