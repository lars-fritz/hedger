import streamlit as st
import numpy as np

st.title("Hedging Impermanent Loss in Concentrated Liquidity Pools")

# --- Inputs ---
p0 = st.number_input("Initial Price $p_0$", value=1.0, min_value=0.01, step=0.01)
p_min = st.number_input("Lower Price Bound $p_{min}$ (less than $p_0$)", value=0.8, min_value=0.001, max_value=0.99, step=0.01)
p_max = st.number_input("Upper Price Bound $p_{max}$ (greater than $p_0$)", value=1.2, min_value=1.01, max_value=100.0, step=0.01)
L = st.number_input("Liquidity $L$", value=1000.0, min_value=1.0)

p_up = st.number_input("Activation Threshold Up $p_{up}$ (between $p_0$ and $p_{max}$)", value=1.05, min_value=p0, max_value=p_max, step=0.01)
p_down = st.number_input("Activation Threshold Down $p_{down}$ (between $p_{min}$ and $p_0$)", value=0.95, min_value=p_min, max_value=p0, step=0.01)

# --- Validation ---
if not (p_min < p0 < p_max):
    st.error("Ensure: $p_{min} < p_0 < p_{max}$")
    st.stop()

# --- Core Calculations ---
sqrt_p0 = np.sqrt(p0)
sqrt_pmax = np.sqrt(p_max)
sqrt_pmin = np.sqrt(p_min)

delta_xA_sell = L * (1/np.sqrt(p0) - 1/np.sqrt(p_max))
delta_xB_sell = L * (np.sqrt(p0) - np.sqrt(p_min))

# IL at boundaries
IL_A_max = (p_max - np.sqrt(p0 * p_max)) * delta_xA_sell
IL_B_max = (1/p_min - 1/np.sqrt(p0 * p_min)) * delta_xB_sell

# Hedge sizes with activation thresholds
xA_hedge = ((p_max - np.sqrt(p0 * p_max)) / (p_max - p_up)) * delta_xA_sell if p_up < p_max else 0
xB_hedge = ((1/p_min - 1/np.sqrt(p0 * p_min)) / (1/p_min - 1/p_down)) * delta_xB_sell if p_down > p_min else 0

# --- Output ---
st.markdown("### 📊 Results", unsafe_allow_html=True)

st.latex(r"\Delta x_A^{\rm sell} = %.4f" % delta_xA_sell)
st.latex(r"\Delta x_B^{\rm sell} = %.4f" % delta_xB_sell)

st.markdown("---")
st.markdown("**Impermanent Loss at Range Boundaries**:")
st.latex(r"\text{IL}_A^{\max} = \left(p_{\max} - \sqrt{p_0 p_{\max}}\right) \cdot \Delta x_A^{\rm sell} = %.4f" % IL_A_max)
st.latex(r"\text{IL}_B^{\max} = \left(\frac{1}{p_{\min}} - \frac{1}{\sqrt{p_0 p_{\min}}} \right) \cdot \Delta x_B^{\rm sell} = %.4f" % IL_B_max)

st.markdown("---")
st.markdown("**Hedge Sizes** (with thresholds):")
st.latex(r"x_A^{\rm hedge} = %.4f" % xA_hedge)
st.latex(r"x_B^{\rm hedge} = %.4f" % xB_hedge)
