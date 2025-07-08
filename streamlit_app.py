import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="CL IL Hedge Simulator", layout="centered")
st.title("💧 Concentrated Liquidity Impermanent Loss & Hedge Visualizer")

# --- User Inputs ---
st.sidebar.header("🔧 LP Setup")
p0 = st.sidebar.number_input("Initial Price $p_0$", min_value=0.0001, value=1.0)
pmin = st.sidebar.number_input("Lower Bound $p_{min}$", min_value=0.0001, max_value=p0-0.0001, value=0.8)
pmax = st.sidebar.number_input("Upper Bound $p_{max}$", min_value=p0+0.0001, value=1.2)
L = st.sidebar.number_input("Liquidity $L$", min_value=0.0001, value=1000.0)

sqrt_p0 = np.sqrt(p0)
sqrt_pmin = np.sqrt(pmin)
sqrt_pmax = np.sqrt(pmax)

# --- Define price grid ---
p_grid = np.linspace(pmin, pmax, 500)

# --- IL Functions ---
def IL_A(p):
    delta_xA = L * (1/np.sqrt(p0) - 1/np.sqrt(p))
    return (p - np.sqrt(p0 * p)) * delta_xA

def IL_B(p):
    delta_xB = L * (np.sqrt(p0) - np.sqrt(p))
    return (1/p - 1/np.sqrt(p0 * p)) * delta_xB

il_vals = np.where(p_grid >= p0, IL_A(p_grid), IL_B(p_grid))

# --- Hedge Sizes ---
dxA_max = L * (1/sqrt_p0 - 1/sqrt_pmax)
xA_hedge = ((pmax - np.sqrt(p0 * pmax)) / (pmax - p0)) * dxA_max

dxB_max = L * (sqrt_p0 - sqrt_pmin)
xB_hedge = ((1/pmin - 1/np.sqrt(p0 * pmin)) / (1/pmin - 1/p0)) * dxB_max

# --- Hedge PnL ---
def hedge_A_pnl(p): return xA_hedge * (p - p0)
def hedge_B_pnl(p): return xB_hedge * (1/p - 1/p0)
hedge_vals = np.where(p_grid >= p0, hedge_A_pnl(p_grid), hedge_B_pnl(p_grid))

# --- Plot: Static IL vs Hedge PnL ---
st.markdown("## 📊 Static View: IL vs Hedge vs Net PnL")

fig1, ax1 = plt.subplots()
ax1.plot(p_grid, il_vals, label="Impermanent Loss", color='red')
ax1.plot(p_grid, hedge_vals, label="Hedge PnL", color='green')
ax1.plot(p_grid, hedge_vals - il_vals, label="Net PnL", color='blue')
ax1.axvline(p0, color='gray', linestyle='--', linewidth=1, label="$p_0$")
ax1.set_xlabel("Price $p$")
ax1.set_ylabel("PnL (Token B or A units)")
ax1.legend()
ax1.grid(True)
st.pyplot(fig1)

# --- Hedge Outputs ---
st.markdown("### 📐 Hedge Sizing")
st.latex(r"x_A^{\text{hedge}} = %.4f" % xA_hedge)
st.latex(r"x_B^{\text{hedge}} = %.4f" % xB_hedge)

# --- GBM Simulation ---
st.markdown("## 📈 Price Path Simulation (Geometric Brownian Motion)")

# --- Simulation Inputs ---
vol = st.slider("Volatility (σ, annualized)", min_value=0.01, max_value=1.0, value=0.1, step=0.01)
steps = st.slider("Number of time steps", min_value=10, max_value=500, value=100)
T = 1.0  # 1 year horizon
dt = T / steps
mu = 0  # Drift can be changed later if needed

# --- Simulate GBM path (different each run) ---
np.random.seed(int(time.time()))  # Use time to create changing seed
W = np.random.normal(0, np.sqrt(dt), size=steps)
log_returns = (mu - 0.5 * vol**2) * dt + vol * W
p_path = p0 * np.exp(np.cumsum(log_returns))

# --- IL and Hedge over Simulated Path ---
def compute_il_hedge_pnl(p_arr):
    il_list, hedge_list, net_list = [], [], []
    for p in p_arr:
        if p >= p0:
            il = IL_A(p)
            hedge = hedge_A_pnl(p)
        else:
            il = IL_B(p)
            hedge = hedge_B_pnl(p)
        il_list.append(il)
        hedge_list.append(hedge)
        net_list.append(hedge - il)
    return np.array(il_list), np.array(hedge_list), np.array(net_list)

il_path, hedge_path, net_pnl_path = compute_il_hedge_pnl(p_path)

# --- Plot: Simulated Price + PnL Tracking ---
fig2, (ax2, ax3) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

time_grid = np.linspace(0, T, steps)

# Price Path
ax2.plot(time_grid, p_path, label="Simulated Price", color="black")
ax2.axhline(p0, color="gray", linestyle="--", label="$p_0$")
ax2.set_ylabel("Price $p$")
ax2.legend()
ax2.grid(True)

# IL, Hedge, Net PnL
ax3.plot(time_grid, il_path, label="Impermanent Loss", color='red')
ax3.plot(time_grid, hedge_path, label="Hedge PnL", color='green')
ax3.plot(time_grid, net_pnl_path, label="Net PnL", color='blue')
ax3.set_xlabel("Time")
ax3.set_ylabel("PnL")
ax3.legend()
ax3.grid(True)

st.pyplot(fig2)
