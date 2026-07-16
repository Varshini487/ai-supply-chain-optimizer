import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

st.set_page_config(page_title="📦 Supply Chain Optimizer", layout="wide")
st.title("📦 AI Supply Chain Optimizer")
st.markdown("Demand forecasting + smart reorder point calculation")

st.sidebar.header("⚙️ Input Parameters")
avg_daily_demand = st.sidebar.number_input("Avg Daily Demand (units)", value=50, min_value=1)
lead_time_days = st.sidebar.number_input("Supplier Lead Time (days)", value=14, min_value=1)
lead_time_std = st.sidebar.number_input("Lead Time Std Dev (days)", value=3, min_value=1)
service_level = st.sidebar.slider("Service Level (%)", 85, 99, 95)
unit_cost = st.sidebar.number_input("Unit Cost ($)", value=10.0)
holding_cost_pct = st.sidebar.slider("Annual Holding Cost (% of unit value)", 15, 40, 25)

z_score = stats.norm.ppf(service_level / 100)
safety_stock = z_score * lead_time_std * np.sqrt(lead_time_days)
rop = (avg_daily_demand * lead_time_days) + safety_stock
eoq = np.sqrt((2 * avg_daily_demand * 365 * 5) / (holding_cost_pct / 100 * unit_cost))

col1, col2, col3, col4 = st.columns(4)
col1.metric("Reorder Point (ROP)", f"{rop:.0f} units")
col2.metric("Safety Stock", f"{safety_stock:.0f} units")
col3.metric("Economic Order Qty (EOQ)", f"{eoq:.0f} units")
col4.metric("Holding Cost/year", f"${eoq/2 * holding_cost_pct/100 * unit_cost:.0f}")

st.markdown("### 📊 Reorder Logic")
st.write(f"""
**When inventory falls to {rop:.0f} units → Place order for {eoq:.0f} units**

- Current stock includes {safety_stock:.0f} units of safety buffer (protects against demand spikes + supplier delays)
- Lead time risk: with {service_level}% service level, you avoid stockouts in {service_level}% of scenarios
- If service level hits 99%: safety stock would be {stats.norm.ppf(0.99) * lead_time_std * np.sqrt(lead_time_days):.0f} units (more buffer, higher cost)
""")

st.markdown("### 📈 Demand Pattern (Simulated 12 months)")
np.random.seed(42)
months = np.arange(12)
trend = np.linspace(0, 500, 12)
seasonal = 200 * np.sin(np.linspace(0, 2*np.pi, 12))
noise = np.random.normal(0, 100, 12)
demand = trend + seasonal + noise
demand = np.maximum(demand, 10)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(months, demand, marker="o", label="Forecasted Demand")
ax.axhline(y=rop, color="red", linestyle="--", label=f"Reorder Point ({rop:.0f})")
ax.axhline(y=safety_stock, color="orange", linestyle="--", label=f"Safety Stock ({safety_stock:.0f})")
ax.fill_between(months, 0, safety_stock, alpha=0.2, color="orange")
ax.set_xlabel("Month")
ax.set_ylabel("Units")
ax.legend()
ax.grid(True, alpha=0.3)
st.pyplot(fig)

st.markdown("---")
st.caption("💡 This is a simplified demo. Production systems integrate real supplier data, seasonal adjustments, and machine learning forecasts.")
