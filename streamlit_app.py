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

# --- Define price grid ---
p_grid = np.linspace(pmin, pmax, 500)

# --- Impermanent Loss Calculations ---
def IL_A(p):
    sqrt_p = np.sqrt(p)
    delta_xA = L * (1/np.sqrt(p0) - 1/np.sqrt(p))
    return (p - np.sqrt(p0*p)) * delta_xA

def IL_B(p):
    sqrt_p = np.sqrt(p)
    delta_xB = L * (sqrt_p0 - sqrt_p)
    return (1/p-1/np.sqrt(p0*p)) * delta_xB

il_vals = np.where(p_grid >= p0, IL_A(p_grid), IL_B(p_grid))

# --- Hedge Size Computations ---
dxA_max = L * (1/sqrt_p0 - 1/sqrt_pmax)
xA_hedge = ((pmax - np.sqrt(p0 * pmax)) / (pmax - p0)) * dxA_max


dxB_max = L * (sqrt_p0 - sqrt_pmin)
xB_hedge = ((1/pmin - 1/np.sqrt(p0 * pmin)) / (1/pmin - 1/p0)) * dxB_max

# --- Hedge PnL Tracking ---
def hedge_A_pnl(p):
    return xA_hedge * (p - p0)

def hedge_B_pnl(p):
    return xB_hedge * (1/p - 1/p0)

hedge_vals = np.where(p_grid >= p0, hedge_A_pnl(p_grid), hedge_B_pnl(p_grid))

# --- Plotting ---
fig, ax = plt.subplots()
ax.plot(p_grid, il_vals, label="Impermanent Loss", color='red')
ax.plot(p_grid, hedge_vals, label="Hedge PnL", color='green')
ax.plot(p_grid, hedge_vals - il_vals, label="Net PnL", color='blue')
ax.axvline(p0, color='gray', linestyle='--', linewidth=1, label="$p_0$")
ax.set_xlabel("Price $p$")
ax.set_ylabel("PnL (in Token B units)")
ax.legend()
ax.grid(True)

st.pyplot(fig)

# --- Display Hedge Sizes ---
st.markdown("### 📊 Hedge Sizing Results")
st.latex(r"x_A^{\text{hedge}} = %.4f" % xA_hedge)
st.latex(r"x_B^{\text{hedge}} = %.4f" % xB_hedge)

st.markdown("---")
st.markdown("Net PnL = Hedge PnL - Impermanent Loss")
st.markdown("Token A is sold as price rises, Token B is sold as price falls.")
