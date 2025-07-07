import streamlit as st
import numpy as np

st.set_page_config(page_title="Interactive Hedging IL in Concentrated Liquidity", layout="wide")

st.title("Interactive Hedging of Impermanent Loss in Concentrated Liquidity")

st.markdown("Adjust the parameters below and observe the calculated impermanent loss and hedge sizes.")


# --- Input parameters ---

col1, col2, col3 = st.columns(3)

with col1:
    p0 = st.number_input("Initial Price $p_0$", value=100.0, min_value=0.01, step=0.1, format="%.4f")
    p_min = st.number_input("Lower Price Bound $p_{\\min}$", value=80.0, min_value=0.001, max_value=p0 - 0.01, step=0.1, format="%.4f")

with col2:
    p_max = st.number_input("Upper Price Bound $p_{\\max}$", value=120.0, min_value=p0 + 0.01, step=0.1, format="%.4f")
    L = st.number_input("Liquidity Parameter $L$", value=1000.0, min_value=1.0, step=1.0, format="%.0f")

with col3:
    p_up = st.number_input("Activation Threshold Up $p_{\\mathrm{up}}$", value=105.0, min_value=p0, max_value=p_max, step=0.1, format="%.4f")
    p_down = st.number_input("Activation Threshold Down $p_{\\mathrm{down}}$", value=95.0, min_value=p_min, max_value=p0, step=0.1, format="%.4f")


# --- Calculate token amounts sold ---

def delta_xA_sell(L, p0, p_max):
    return L * (1/np.sqrt(p0) - 1/np.sqrt(p_max))

def delta_xB_sell(L, p0, p_min):
    return L * (np.sqrt(p0) - np.sqrt(p_min))

delta_xA = delta_xA_sell(L, p0, p_max)
delta_xB = delta_xB_sell(L, p0, p_min)


# --- Impermanent Loss max ---

IL_A_max = (p_max - np.sqrt(p0 * p_max)) * delta_xA
IL_B_max = (1/p_min - 1/np.sqrt(p0 * p_min)) * delta_xB


# --- Hedge sizes without activation threshold ---

def hedge_A_no_threshold(p0, p_max, delta_xA):
    return ((p_max - np.sqrt(p0 * p_max)) / (p_max - p0)) * delta_xA

def hedge_B_no_threshold(p0, p_min, delta_xB):
    numerator = (1/p_min - 1/np.sqrt(p0 * p_min))
    denominator = (1/p_min - 1/p0)
    return (numerator / denominator) * delta_xB


hedge_A_nt = hedge_A_no_threshold(p0, p_max, delta_xA)
hedge_B_nt = hedge_B_no_threshold(p0, p_min, delta_xB)


# --- Hedge sizes WITH activation thresholds ---

def hedge_A_threshold(p0, p_max, p_up, delta_xA):
    if p_up >= p_max:
        return 0.0
    return ((p_max - np.sqrt(p0 * p_max)) / (p_max - p_up)) * delta_xA

def hedge_B_threshold(p0, p_min, p_down, delta_xB):
    if p_down <= p_min:
        return 0.0
    numerator = (1/p_min - 1/np.sqrt(p0 * p_min))
    denominator = (1/p_min - 1/p_down)
    return (numerator / denominator) * delta_xB


hedge_A_t = hedge_A_threshold(p0, p_max, p_up, delta_xA)
hedge_B_t = hedge_B_threshold(p0, p_min, p_down, delta_xB)


# --- Display results ---

st.markdown("---")
st.subheader("Token Amounts Sold in Price Moves")

st.markdown(f"""
- Token A sold as price rises to $p_{{\\max}}$:  
$$\\Delta x_A^{{\\mathrm{{sell}}}} = {delta_xA:.4f}$$

- Token B sold as price falls to $p_{{\\min}}$:  
$$\\Delta x_B^{{\\mathrm{{sell}}}} = {delta_xB:.4f}$$
""")

st.subheader("Maximum Impermanent Loss (IL)")

st.markdown(f"""
- Max IL from selling Token A (price to $p_{{\\max}}$):  
$$\\mathrm{{IL}}_A^{{\\max}} = {IL_A_max:.4f}$$

- Max IL from selling Token B (price to $p_{{\\min}}$):  
$$\\mathrm{{IL}}_B^{{\\max}} = {IL_B_max:.4f}$$
""")

st.subheader("Hedge Sizes WITHOUT Activation Threshold")

st.markdown(f"""
- Hedge Token A size:  
$$x_A^{{\\mathrm{{hedge}}}} = {hedge_A_nt:.4f}$$

- Hedge Token B size:  
$$x_B^{{\\mathrm{{hedge}}}} = {hedge_B_nt:.4f}$$
""")

st.subheader("Hedge Sizes WITH Activation Threshold")

st.markdown(f"""
- Hedge Token A size (activates at $p_{{\\mathrm{{up}}}} = {p_up:.4f}$):  
$$x_A^{{\\mathrm{{hedge}}}} = {hedge_A_t:.4f}$$

- Hedge Token B size (activates at $p_{{\\mathrm{{down}}}} = {p_down:.4f}$):  
$$x_B^{{\\mathrm{{hedge}}}} = {hedge_B_t:.4f}$$
""")

st.markdown(
    """
    ---
    *Adjust the parameters above to see how the hedge sizes and impermanent loss change dynamically.*

    This interactive tool helps visualize the impact of your liquidity range and activation thresholds on your hedge strategy.
    """
)
