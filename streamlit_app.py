import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="CL IL Hedge Simulator", layout="centered")
st.title("💧 Concentrated Liquidity Impermanent Loss & Hedge Visualizer")

# --- User Inputs ---
p0 = st.number_input("Initial Price $p_0$", min_value=0.0001, value=1.0)
pmin = st.number_input("Lower Bound $p_{min}$", min_value=0.0001, max_value=p0-0.0001, value=0.8)
pmax = st.number_input("Upper Bound $p_{max}$", min_value=p0+0.0001, value=1.2)
L = st.number_input("Liquidity $L$", min_value=0.0001, value=1000.0)

sqrt_p0 = np.sqrt(p0)
sqrt_pmin = np.sqrt(pmin)
sqrt_pmax = np.sqrt(pmax)

# --- Define price grids ---
p_grid_up = np.linspace(p0, pmax, 300)
p_grid_down = np.linspace(pmin, p0, 300)

# --- Impermanent Loss Calculations ---
def IL_A(p):
    delta_xA = L * (1/np.sqrt(p0) - 1/np.sqrt(p))
    return (p - np.sqrt(p0*p)) * delta_xA  # units: token B

def IL_B(p):
    sqrt_p = np.sqrt(p)
    delta_xB = L * (sqrt_p0 - sqrt_p)
    return (1/p - 1/np.sqrt(p0*p)) * delta_xB  # units: token A

il_up = IL_A(p_grid_up)
il_down = IL_B(p_grid_down)

# --- Hedge Size Computations ---
dxA_max = L * (1/sqrt_p0 - 1/sqrt_pmax)
xA_hedge = ((pmax - np.sqrt(p0 * pmax)) / (pmax - p0)) * dxA_max

dxB_max = L * (sqrt_p0 - sqrt_pmin)
xB_hedge = ((1/pmin - 1/np.sqrt(p0 * pmin)) / (1/pmin - 1/p0)) * dxB_max

# --- Hedge PnL Functions ---
def hedge_A_pnl(p):  # p > p0
    return xA_hedge * (p - p0)  # token B

def hedge_B_pnl(p):  # p < p0
    return xB_hedge * (1/p - 1/p0)  # token A

hedge_up = hedge_A_pnl(p_grid_up)
hedge_down = hedge_B_pnl(p_grid_down)

# --- Plot for p > p0 (Token B units) ---
fig1, ax1 = plt.subplots()
ax1.plot(p_grid_up, il_up, label="Impermanent Loss", color='red')
ax1.plot(p_grid_up, hedge_up, label="Hedge PnL", color='green')
ax1.plot(p_grid_up, hedge_up - il_up, label="Net PnL", color='blue')
ax1.axvline(p0, color='gray', linestyle='--', linewidth=1, label="$p_0$")
ax1.set_xlabel("Price $p$")
ax1.set_ylabel("PnL (in Token B)")
ax1.set_title("Price Increase Region ($p > p_0$)")
ax1.legend()
ax1.grid(True)
st.pyplot(fig1)

# --- Plot for p < p0 (Token A units) ---
fig2, ax2 = plt.subplots()
ax2.plot(p_grid_down, il_down, label="Impermanent Loss", color='red')
ax2.plot(p_grid_down, hedge_down, label="Hedge PnL", color='green')
ax2.plot(p_grid_down, hedge_down - il_down, label="Net PnL", color='blue')
ax2.axvline(p0, color='gray', linestyle='--', linewidth=1, label="$p_0$")
ax2.set_xlabel("Price $p$")
ax2.set_ylabel("PnL (in Token A)")
ax2.set_title("Price Decrease Region ($p < p_0$)")
ax2.legend()
ax2.grid(True)
st.pyplot(fig2)

# --- Display Hedge Sizes ---
st.markdown("### 📊 Hedge Sizing Results")
st.latex(r"x_A^{\text{hedge}} = %.4f" % xA_hedge)
st.latex(r"x_B^{\text{hedge}} = %.4f" % xB_hedge)

st.markdown("---")
st.markdown("Net PnL = Hedge PnL − Impermanent Loss")
st.markdown("Token A is sold as price rises, Token B is sold as price falls.")

