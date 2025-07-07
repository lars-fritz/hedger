import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="CL IL Hedge Simulator", layout="centered")
st.title("💹 Impermanent Loss Hedging Simulator for Concentrated Liquidity")

# --- Inputs ---
p0 = st.number_input("Initial Price $p_0$", value=1.0, min_value=0.01, step=0.01)
p_min = st.number_input("Lower Price Bound $p_{min}$", value=0.8, min_value=0.001, max_value=p0 - 0.01, step=0.01)
p_max = st.number_input("Upper Price Bound $p_{max}$", value=1.2, min_value=p0 + 0.01, step=0.01)
L = st.number_input("Liquidity $L$", value=1000.0, min_value=1.0)

p_up = st.number_input("Activation Threshold Up $p_{up}$", value=1.05, min_value=p0, max_value=p_max, step=0.01)
p_down = st.number_input("Activation Threshold Down $p_{down}$", value=0.95, min_value=p_min, max_value=p0, step=0.01)

# --- Core ---
sqrt_p0 = np.sqrt(p0)
sqrt_pmax = np.sqrt(p_max)
sqrt_pmin = np.sqrt(p_min)

delta_xA_sell = L * (1/np.sqrt(p0) - 1/np.sqrt(p_max))
delta_xB_sell = L * (np.sqrt(p0) - np.sqrt(p_min))

IL_A_max = (p_max - np.sqrt(p0 * p_max)) * delta_xA_sell
IL_B_max = (1/p_min - 1/np.sqrt(p0 * p_min)) * delta_xB_sell

xA_hedge = ((p_max - np.sqrt(p0 * p_max)) / (p_max - p_up)) * delta_xA_sell if p_up < p_max else 0
xB_hedge = ((1/p_min - 1/np.sqrt(p0 * p_min)) / (1/p_min - 1/p_down)) * delta_xB_sell if p_down > p_min else 0

# --- Price Scenario Slider ---
st.markdown("### 📈 Price Scenario")
p_scenario = st.slider("Simulate market price", min_value=float(p_min), max_value=float(p_max), value=float(p0), step=0.001, format="%.3f")

# --- IL Calculation ---
if p_scenario > p0:
    IL = (p_scenario - np.sqrt(p0 * p_scenario)) * delta_xA_sell
    hedge_pnl = xA_hedge * (p_scenario - p0) if p_scenario >= p_up else 0
elif p_scenario < p0:
    IL = (1/np.sqrt(p0 * p_scenario) - 1/p_scenario) * delta_xB_sell
    hedge_pnl = xB_hedge * (1/p_scenario - 1/p0) if p_scenario <= p_down else 0
else:
    IL = 0
    hedge_pnl = 0

net_pnl = hedge_pnl - IL

# --- Display Results ---
st.markdown("### 📊 Simulation Result")
st.latex(r"\text{Simulated Price: } p = %.3f" % p_scenario)
st.latex(r"\text{Impermanent Loss: } IL = %.4f" % IL)
st.latex(r"\text{Hedge PnL: } = %.4f" % hedge_pnl)
st.latex(r"\text{Net PnL: } = %.4f" % net_pnl)

# --- Chart ---
st.markdown("### 📉 PnL Chart Over Price Range")
prices = np.linspace(p_min, p_max, 300)
ILs = []
hedges = []
nets = []

for p in prices:
    if p > p0:
        il = (p - np.sqrt(p0 * p)) * delta_xA_sell
        h = xA_hedge * (p - p0) if p >= p_up else 0
    elif p < p0:
        il = (1/np.sqrt(p0 * p) - 1/p) * delta_xB_sell
        h = xB_hedge * (1/p - 1/p0) if p <= p_down else 0
    else:
        il, h = 0, 0
    ILs.append(il)
    hedges.append(h)
    nets.append(h - il)

# Plot
fig, ax = plt.subplots()
ax.plot(prices, ILs, label="Impermanent Loss", color="red")
ax.plot(prices, hedges, label="Hedge PnL", color="green")
ax.plot(prices, nets, label="Net PnL", color="blue")
ax.axvline(p0, color='gray', linestyle='--', linewidth=1, label="p₀")
ax.axvline(p_up, color='purple', linestyle=':', linewidth=1, label="p_up")
ax.axvline(p_down, color='purple', linestyle=':', linewidth=1, label="p_down")
ax.set_xlabel("Price")
ax.set_ylabel("PnL")
ax.legend()
st.pyplot(fig)
