import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Impermanent Loss (IL) Simulator with Hedge")

# Input parameters
p0 = st.number_input("Initial price $p_0$", value=1.0, min_value=0.0001)
L = st.number_input("Liquidity $L$", value=10.0, min_value=0.0)
p_min = st.number_input("Lower price bound $p_{\\min}$", value=0.5, min_value=0.0001, max_value=p0 - 0.0001)
p_max = st.number_input("Upper price bound $p_{\\max}$", value=2.0, min_value=p0 + 0.0001)

# Price range for plotting
prices_below = np.linspace(p_min, p0, 200, endpoint=False)
prices_above = np.linspace(p0, p_max, 200)
prices_full = np.concatenate([prices_below, [p0], prices_above])

# Functions
def delta_xA_sell(p):
    return L * (1 / np.sqrt(p0) - 1 / np.sqrt(p))

def delta_xB_sell(p):
    return L * (np.sqrt(p0) - np.sqrt(p))

def IL_A(p):  # p > p0
    dx_A = delta_xA_sell(p)
    return (p - np.sqrt(p0 * p)) * dx_A  # units: token B

def IL_B(p):  # p < p0
    dx_B = delta_xB_sell(p)
    return (1 / p - 1 / np.sqrt(p0 * p)) * dx_B  # units: token A

# Compute IL
il_values = []
unit_labels = []
for p in prices_full:
    if p < p0:
        il = IL_B(p)
        il_in_B = il * p  # Convert token A to token B
        il_values.append(il_in_B)
        unit_labels.append("A")
    elif p > p0:
        il = IL_A(p)
        il_values.append(il)
        unit_labels.append("B")
    else:
        il_values.append(0.0)
        unit_labels.append("-")

# Plotting
fig, ax = plt.subplots()
ax.plot(prices_full, il_values, label="Impermanent Loss (converted to token B units)", color="darkred")
ax.axvline(p0, color='gray', linestyle='--', label="$p_0$")
ax.axhline(0, color='black', linewidth=0.5)

ax.set_xlabel("Price $p$")
ax.set_ylabel("IL (in token B units)")
ax.set_title("Impermanent Loss vs. Price")
ax.legend()
st.pyplot(fig)
