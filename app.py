import streamlit as st
import pandas as pd
from engine import calculate_surge_and_depletion
from inventory_db import INITIAL_INVENTORY

st.set_page_config(page_title="Dynamic Retail Arbitrage Engine", layout="wide")

st.title("⚡ Dynamic Inventory & Surge Arbitrage Engine")
st.caption("Applied Algorithmic Pricing Simulation for Quick-Commerce Dark Stores")

st.sidebar.header("🕹️ Simulation Controls")
weather_condition = st.sidebar.selectbox("External Weather Event", ["Clear Skies", "Heavy Downpour / Rain", "Extreme Heatwave"])
event_surge = st.sidebar.slider("Order Velocity Spike (%)", min_value=0, max_value=400, value=150, step=25)

demand_factor = (1 + (event_surge / 100)) * (2.2 if "Rain" in weather_condition else 1.0)

results = []
for _, row in INITIAL_INVENTORY.iterrows():
    simulated_demand = round(0.5 * demand_factor, 2)
    metrics = calculate_surge_and_depletion(
        current_stock=row["current_stock"],
        safety_stock=row["safety_stock"],
        orders_per_min=simulated_demand,
        base_price=row["base_price"],
        lead_time_min=row["restock_lead_time_min"]
    )
    results.append({
        "Product": row["name"],
        "Stock Left": row["current_stock"],
        "Current Velocity (orders/min)": simulated_demand,
        "Est. Stockout (Minutes)": metrics["time_to_exhaust_min"],
        "Restock Time (Min)": row["restock_lead_time_min"],
        "Status": metrics["risk_level"],
        "Base Price": f"₹{row['base_price']}",
        "Dynamic Price": f"₹{metrics['dynamic_price']}",
        "Surge": f"{metrics['surge_multiplier']}x",
        "Added Margin/Unit": f"+₹{metrics['arbitrage_margin']}"
    })

df_results = pd.DataFrame(results)

col1, col2, col3 = st.columns(3)
col1.metric("Demand Multiplier", f"{demand_factor:.1f}x")
col2.metric("Critical Stockouts", len(df_results[df_results["Status"] == "CRITICAL"]))
col3.metric("Peak Surge Active", df_results["Surge"].max())

st.subheader("Live Operational Heatmap")
st.dataframe(df_results, use_container_width=True)

st.info("💡 **Decision Logic:** When demand velocity cuts stockout time below supplier lead time, the engine ratchets up price elasticity to throttle depletion and lock in arbitrage margins.")
