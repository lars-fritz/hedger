import streamlit as st
import numpy as np

st.set_page_config(page_title="Hedging IL in Concentrated Liquidity", layout="wide")

st.title("Hedging Impermanent Loss in Concentrated Liquidity Pools")

st.markdown("""
This interactive app lets you explore impermanent loss (IL) and hedging strategies for liquidity providers in concentrated liquidity pools.
  
Adjust parameters and see the formulas and hedge sizes update in real-time.
  
---
""")

# ---- INPUTS ----
st.header("Parameters")

p0 = st.number_input("Initial Price $p_0$", value=1.0, min_value=0.01, step=0.01, format="%.4f")
p_min = st.number_input("Lower Price Bound $p_{\\min}$ (should be < $p_0$)", value=0.8, min_value=0.001, step=0.01, format="%.4f")
p_max = st.number_input("Upper Price Bound $p_{\\max}$ (should be > $p_0$)", value=1.2, min_value=0.01, step=0.01, format="%.4f")
L = st.number_input("Liquidity Parameter $L$", value=1000.0, min_value=1.0, step=1)

st.markdown("---")

p_up = st.number_input("Activation Threshold Up $p_{\\mathrm{up}}$ (between $p_0$ and $p_{\\max}$)", value=1.05, min_value=0.01, step=0.01, format="%.4f")
p_down = st.number_input("Activation Threshold Down $p_{\\mathrm{down}}$ (between $p_{\\min}$ and $p_0$)", value=0.95, min_value=0.001, step=0.01, format="%.4f")

# ---- VALIDATIONS ----
valid = True
if not (p_min < p0 < p_max):
    st.error("⚠️ Please ensure: Lower Bound $p_{\\min}$ < Initial Price $p_0$ < Upper Bound $p_{\\max}$.")
    valid = False
if not (p0 <= p_up <= p_max):
    st.warning("⚠️ Activation Threshold Up $p_{\\mathrm{up}}$ should be between $p_0$ and $p_{\\max}$.")
if not (p_min <= p_down <= p0):
    st.warning("⚠️ Activation Threshold Down $p_{\\mathrm{down}}$ should be between $p_{\\min}$ and $p_0$.")

if not valid:
    st.stop()

# ---- HELPER FUNCTIONS ----
def sqrt(x):
    return np.sqrt(x)

def compute_delta_xA_sell(L, p0, p_max):
    return L * (1/np.sqrt(p0) - 1/np.sqrt(p_max))

def compute_delta_xB_sell(L, p0, p_min):
    return L * (np.sqrt(p0) - np.sqrt(p_min))

# --- Calculations ---
delta_xA_sell = compute_delta_xA_sell(L, p0, p_max)
delta_xB_sell = compute_delta_xB_sell(L, p0, p_min)

# Max Impermanent Loss from selling A (price rises to p_max)
IL_A_max = (p_max - np.sqrt(p0 * p_max)) * delta_xA_sell

# Max Impermanent Loss from selling B (price falls to p_min)
IL_B_max = (1/p_min - 1/np.sqrt(p0 * p_min)) * delta_xB_sell

# Hedge sizes without activation thresholds
xA_hedge_full = ((p_max - np.sqrt(p0 * p_max)) / (p_max - p0)) * delta_xA_sell
xB_hedge_full = ((1/p_min - 1/np.sqrt(p0 * p_min)) / (1/p_min - 1/p0)) * delta_xB_sell

# Hedge sizes with activation thresholds
if p_up == p_max:
    xA_hedge_threshold = 0.0
else:
    xA_hedge_threshold = ((p_max - np.sqrt(p0 * p_max)) / (p_max - p_up)) * delta_xA_sell

if p_down == p_min:
    xB_hedge_threshold = 0.0
else:
    xB_hedge_threshold = ((1/p_min - 1/np.sqrt(p0 * p_min)) / (1/p_min - 1/p_down)) * delta_xB_sell

# ---- DISPLAY RESULTS ----

st.header("Results")

st.markdown("### Token Holdings at Current Price $p$ within $[p_{\\min}, p_{\\max}]$")

st.latex(r"""
x_A(p) = L \left( \frac{1}{\sqrt{p}} - \frac{1}{\sqrt{p_{\max}}} \right), \quad
x_B(p) = L \left( \sqrt{p} - \sqrt{p_{\min}} \right)
""")

st.markdown(f"At initial price $p_0={p0}$ and liquidity $L={L}$:")

st.latex(r"""
\Delta x_A^{\rm{sell}} = L \left( \frac{1}{\sqrt{p_0}} - \frac{1}{\sqrt{p_{\max}}} \right) = {:.4f}
""".format(delta_xA_sell))

st.latex(r"""
\Delta x_B^{\rm{sell}} = L \left( \sqrt{p_0} - \sqrt{p_{\min}} \right) = {:.4f}
""".format(delta_xB_sell))

st.markdown("### Max Impermanent Loss (IL) at boundaries")

st.latex(r"""
\text{{IL}}_A^{\max} = \left(p_{\max} - \sqrt{p_0 p_{\max}} \right) \Delta x_A^{\rm{sell}} = {:.4f}
""".format(IL_A_max))

st.latex(r"""
\text{{IL}}_B^{\max} = \left(\frac{1}{p_{\min}} - \frac{1}{\sqrt{p_0 p_{\min}}} \right) \Delta x_B^{\rm{sell}} = {:.4f}
""".format(IL_B_max))

st.markdown("### Hedge Sizes WITHOUT Activation Thresholds")

st.latex(r"""
x_A^{\rm{hedge}} = \frac{p_{\max} - \sqrt{p_0 p_{\max}}}{p_{\max} - p_0} \cdot \Delta x_A^{\rm{sell}} = {:.4f}
""".format(xA_hedge_full))

st.latex(r"""
x_B^{\rm{hedge}} = \frac{\frac{1}{p_{\min}} - \frac{1}{\sqrt{p_0 p_{\min}}}}{\frac{1}{p_{\min}} - \frac{1}{p_0}} \cdot \Delta x_B^{\rm{sell}} = {:.4f}
""".format(xB_hedge_full))

st.markdown("### Hedge Sizes WITH Activation Thresholds")

st.latex(r"""
x_A^{\rm{hedge}}(p_{\mathrm{up}}) = \frac{p_{\max} - \sqrt{p_0 p_{\max}}}{p_{\max} - p_{\mathrm{up}}} \cdot \Delta x_A^{\rm{sell}} = {:.4f}
""".format(xA_hedge_threshold))

st.latex(r"""
x_B^{\rm{hedge}}(p_{\mathrm{down}}) = \frac{\frac{1}{p_{\min}} - \frac{1}{\sqrt{p_0 p_{\min}}}}{\frac{1}{p_{\min}} - \frac{1}{p_{\mathrm{down}}}} \cdot \Delta x_B^{\rm{sell}} = {:.4f}
""".format(xB_hedge_threshold))

st.markdown("---")

st.markdown("""
### Notes:

- The formulas are based on the **execution shortfall** from selling tokens via liquidity provision compared to market prices.
- Hedge sizes indicate how much of token A or B you should hold or hedge in to compensate for impermanent loss.
- Activation thresholds allow delaying hedge opening until significant price moves occur, improving capital efficiency.
""")
