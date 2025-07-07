import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="CL IL Hedge Simulator", layout="centered")
st.title("💧 Concentrated Liquidity IL & Hedge Visualizer")

# --- User Inputs ---
p0 = st.number_input("Initial Price $p_0$", min_value=0.0001, value=1.0)
pmin = st.number_input("Lower Bound $p_{min}$", min_value=0.0001, max_value=p0-0.0001, value=0.8)
pmax = st.number_input("Upper Bound $p_{max}$", min_value=p0+0.0001, value=1.2)
L = st.number_input("Liquidity $L$", min_value=0.0001, value=1000.0)

# --- Square roots of key prices ---
sqrt_p0 = np.sqrt(p0)
sqrt_pmin = np.sqrt(pmin)
sqrt_pmax = np.sqrt(pmax)

# --- Define static price grid for visualization ---
p_grid = np.linspace(pmin, pmax, 500)

# --- IL functions ---
def IL_A(p):
    delta_xA = L * (1/np.sqrt(p0) - 1/np.sqrt(p))
    return (p - np.sqrt(p0*p)) * delta_xA

def IL_B(p):
    delta_xB = L * (sqrt_p0 - np.sqrt(p))
    return (1/p - 1/np.sqrt(p0*p)) * delta_xB

il_vals = np.where(p_grid >= p0, IL_A(p_grid), IL_B(p_grid))

# --- Hedge sizing ---
dxA_max = L * (1/sqrt_p0 - 1/sqrt_pmax)
xA_hedge = ((pmax - np.sqrt(p0 * pmax)) / (pmax - p0)) * dxA_max

dxB_max = L * (sqrt_p0 - sqrt_pmin)
xB_hedge = ((1/pmin - 1/np.sqrt(p0 * pmin)) / (1/pmin - 1/p0)) * dxB_max

# --- Hedge PnL functions ---
def hedge_A_pnl(p): return xA_hedge * (p - p0)
def hedge_B_pnl(p): return xB_hedge * (1/p - 1/p0)

hedge_vals = np.where(p_grid >= p0, hedge_A_pnl(p_grid), hedge_B_pnl(p_grid))

# --- Plot IL and Hedge over price ---
fig1, ax1 = plt.subplots()
ax1.plot(p_grid, il_vals, label="Impermanent Loss", color='red')
ax1.plot(p_grid, hedge_vals, label="Hedge PnL", color='green')
ax1.plot(p_grid, hedge_vals - il_vals, label="Net PnL", color='blue')
ax1.axvline(p0, color='gray', linestyle='--', linewidth=1, label="$p_0$")
ax1.set_xlabel("Price $p$")
ax1.set_ylabel("PnL (in token units)")
ax1.legend()
ax1.grid(True)
st.pyplot(fig1)

# --- Hedge Sizing Output ---
st.markdown("### 📊 Hedge Sizing Results")
st.latex(r"x_A^{\text{hedge}} = %.4f" % xA_hedge)
st.latex(r"x_B^{\text{hedge}} = %.4f" % xB_hedge)

# --- GBM Simulation Controls ---
st.markdown("---")
st.markdown("## 📈 Price Path Simulation (Geometric Brownian Motion)")

col1, col2, col3 = st.columns(3)
with col1:
    sigma = st.number_input("Volatility $\\sigma$", min_value=0.0001, value=0.2)
with col2:
    T = st.number_input("Time Steps", min_value=10, value=100)
with col3:
    seed = st.number_input("Random Seed", min_value=0, value=42)

np.random.seed(seed)

dt = 1 / T
dW = np.random.normal(0, np.sqrt(dt), size=T)
log_returns = (-(sigma**2)/2) * dt + sigma * dW
price_path = p0 * np.exp(np.cumsum(log_returns))
time_axis = np.linspace(0, 1, T)

# --- IL and Hedge on Simulated Path ---
il_path = np.where(price_path >= p0, IL_A(price_path), IL_B(price_path))
hedge_path = np.where(price_path >= p0, hedge_A_pnl(price_path), hedge_B_pnl(price_path))
net_pnl_path = hedge_path - il_path

# --- Plot GBM and IL/Hedge ---
fig2, (ax2, ax3) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

# Price path
ax2.plot(time_axis, price_path, label="Price $p(t)$", color='black')
ax2.axhline(p0, color='gray', linestyle='--', label="$p_0$")
ax2.set_ylabel("Price")
ax2.legend()
ax2.grid(True)

# IL and Hedge
ax3.plot(time_axis, il_path, label="Impermanent Loss", color='red')
ax3.plot(time_axis, hedge_path, label="Hedge PnL", color='green')
ax3.plot(time_axis, net_pnl_path, label="Net PnL", color='blue')
ax3.set_xlabel("Time")
ax3.set_ylabel("PnL")
ax3.legend()
ax3.grid(True)

st.pyplot(fig2)

