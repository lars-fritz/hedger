import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import math # Keep math for potential other uses, but replace math.sqrt with np.sqrt where arrays are involved

# Set Streamlit page configuration
st.set_page_config(page_title="CL IL Hedge Simulator", layout="centered")
st.title("💧 Concentrated Liquidity Impermanent Loss & Hedge Visualizer")

# --- User Inputs ---
st.sidebar.header("🔧 LP Setup")
p0 = st.sidebar.number_input("Initial Price $p_0$", min_value=0.0001, value=1.0)
pmin = st.sidebar.number_input("Lower Bound $p_{min}$", min_value=0.0001, max_value=p0-0.0001, value=0.8)
pmax = st.sidebar.number_input("Upper Bound $p_{max}$", min_value=p0+0.0001, value=1.2)
L = st.sidebar.number_input("Liquidity $L$", min_value=0.0001, value=1000.0)

# Calculate square roots for efficiency
sqrt_p0 = np.sqrt(p0)
sqrt_pmin = np.sqrt(pmin)
sqrt_pmax = np.sqrt(pmax)

# --- Define price grid for static plot ---
p_grid = np.linspace(pmin, pmax, 500)

# --- Token Holding Functions ---
def calculate_xA(L_val, p, p_max_val):
    """
    Calculates the amount of token A held at price p.
    x_A(p) = L * (1/sqrt(p) - 1/sqrt(p_max))
    Uses np.sqrt to handle both scalar and numpy array inputs for p.
    """
    return L_val * (1 / np.sqrt(p) - 1 / np.sqrt(p_max_val))

def calculate_xB(L_val, p, p_min_val):
    """
    Calculates the amount of token B held at price p.
    x_B(p) = L * (sqrt(p) - sqrt(p_min))
    Uses np.sqrt to handle both scalar and numpy array inputs for p.
    """
    return L_val * (np.sqrt(p) - np.sqrt(p_min_val))

# --- IL Functions ---
def calculate_delta_xA_sell(L_val, p0_val, p):
    """
    Calculates the amount of Token A sold when price increases from p0 to p.
    Delta x_A_sell(p) = L * (1/sqrt(p0) - 1/sqrt(p))
    Uses np.sqrt to handle both scalar and numpy array inputs for p.
    """
    return L_val * (1 / np.sqrt(p0_val) - 1 / np.sqrt(p))

def calculate_delta_xB_sell(L_val, p0_val, p):
    """
    Calculates the amount of Token B sold when price decreases from p0 to p.
    Delta x_B_sell(p) = L * (sqrt(p0) - sqrt(p))
    Uses np.sqrt to handle both scalar and numpy array inputs for p.
    """
    return L_val * (np.sqrt(p0_val) - np.sqrt(p))

def calculate_il_A(p, p0_val, delta_xA_sell_val):
    """
    Calculates Impermanent Loss from selling Token A (price rises).
    IL_A(p) = (p - sqrt(p0 * p)) * Delta x_A_sell(p)
    Uses np.sqrt to handle both scalar and numpy array inputs for p.
    """
    return (p - np.sqrt(p0_val * p)) * delta_xA_sell_val

def calculate_il_B(p, p0_val, delta_xB_sell_val):
    """
    Calculates Impermanent Loss from selling Token B (price falls).
    IL_B(p) = (1/p - 1/sqrt(p0 * p)) * Delta x_B_sell(p)
    Uses np.sqrt to handle both scalar and numpy array inputs for p.
    """
    return (1 / p - 1 / np.sqrt(p0_val * p)) * delta_xB_sell_val

# --- IL Calculation for Static Plot ---
# Using the IL functions from the provided writeup
def IL_A_static(p_val):
    delta_xA = calculate_delta_xA_sell(L, p0, p_val)
    return calculate_il_A(p_val, p0, delta_xA)

def IL_B_static(p_val):
    delta_xB = calculate_delta_xB_sell(L, p0, p_val)
    return calculate_il_B(p_val, p0, delta_xB)

il_vals = np.where(p_grid >= p0, IL_A_static(p_grid), IL_B_static(p_grid))

# --- Hedge Sizes (Static, based on max IL at boundaries) ---
# These are the sizes of the hedge positions if opened at p0 to cover max IL
dxA_max = calculate_delta_xA_sell(L, p0, pmax)
if (pmax - p0) == 0: # Avoid division by zero if pmax == p0 (shouldn't happen with validation)
    xA_hedge = float('inf')
else:
    xA_hedge = ((pmax - np.sqrt(p0 * pmax)) / (pmax - p0)) * dxA_max

dxB_max = calculate_delta_xB_sell(L, p0, pmin)
if (1/pmin - 1/p0) == 0: # Avoid division by zero if pmin == p0 (shouldn't happen)
    xB_hedge = float('inf')
else:
    xB_hedge = ((1/pmin - 1/np.sqrt(p0 * pmin)) / (1/pmin - 1/p0)) * dxB_max

# --- Hedge PnL for Static Plot ---
# PnL of the fixed hedge positions if opened at p0
def hedge_A_pnl_static(p_val): return xA_hedge * (p_val - p0)
def hedge_B_pnl_static(p_val): return xB_hedge * (1/p_val - 1/p0)
hedge_vals = np.where(p_grid >= p0, hedge_A_pnl_static(p_grid), hedge_B_pnl_static(p_grid))

# --- Plot: Static IL vs Hedge PnL ---
st.markdown("## 📊 Static View: IL vs Hedge vs Net PnL")

fig1, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot(p_grid, il_vals, label="Impermanent Loss", color='red', linewidth=2)
ax1.plot(p_grid, hedge_vals, label="Hedge PnL", color='green', linewidth=2)
ax1.plot(p_grid, hedge_vals - il_vals, label="Net PnL (Hedge - IL)", color='blue', linewidth=2, linestyle='--')
ax1.axvline(p0, color='gray', linestyle=':', linewidth=1.5, label="$p_0$")
ax1.set_xlabel("Price $p$", fontsize=12)
ax1.set_ylabel("PnL (Token B or A units)", fontsize=12)
ax1.set_title("Impermanent Loss and Hedge PnL Across Price Range", fontsize=14)
ax1.legend(fontsize=10)
ax1.grid(True, linestyle='--', alpha=0.7)
st.pyplot(fig1)

# --- Hedge Outputs ---
st.markdown("### 📐 Hedge Sizing (Calculated for Max IL at Boundaries)")
st.latex(r"x_A^{\text{hedge}} = %.4f" % xA_hedge)
st.latex(r"x_B^{\text{hedge}} = %.4f" % xB_hedge)

# --- GBM Simulation ---
st.markdown("## 📈 Price Path Simulation (Geometric Brownian Motion)")

# --- Simulation Inputs ---
col_sim_1, col_sim_2 = st.columns(2)
with col_sim_1:
    vol = st.slider("Volatility (σ, annualized)", min_value=0.01, max_value=1.0, value=0.1, step=0.01)
    steps = st.slider("Number of time steps", min_value=10, max_value=500, value=100)
with col_sim_2:
    T = st.number_input("Time Horizon (Years)", min_value=0.1, value=1.0, step=0.1)
    # New input for fee rate
    fee_rate_percent = st.slider("Fee Rate (%) per trade", min_value=0.0, max_value=1.0, value=0.3, step=0.01)
    fee_rate = fee_rate_percent / 100 # Convert to decimal

dt = T / steps
mu = 0  # Drift can be changed later if needed for more complex simulations

# Input validation for price bounds and thresholds
if not (pmin < p0 < pmax):
    st.error("Error: $p_{\\min}$ must be less than $p_0$, and $p_0$ must be less than $p_{\\max}$. Please adjust the price bounds.")
    st.stop() # Stop execution if inputs are invalid

# --- Simulate GBM path (different each run) ---
np.random.seed(int(time.time()))  # Use time to create changing seed for fresh simulations
W = np.random.normal(0, np.sqrt(dt), size=steps)
log_returns = (mu - 0.5 * vol**2) * dt + vol * W
p_path = p0 * np.exp(np.cumsum(log_returns))

# --- IL, Hedge PnL, and Fee calculation over Simulated Path ---
def compute_il_hedge_pnl_and_fees(p_arr, L_val, p0_val, p_min_val, p_max_val, fee_rate_val, xA_hedge_val, xB_hedge_val):
    il_list, hedge_list, net_list = [], [], []
    fees_A_list, fees_B_list = [], []
    accumulated_fees_A = 0.0
    accumulated_fees_B = 0.0

    # Initialize token holdings for fee calculation at p0 (first point in p_path)
    # This assumes p_path[0] is p0, which it is due to p0 * np.exp(np.cumsum(...))
    prev_xA_for_fee_calc = calculate_xA(L_val, p0_val, p_max_val)
    prev_xB_for_fee_calc = calculate_xB(L_val, p0_val, p_min_val)

    for i, p in enumerate(p_arr):
        # Calculate IL and Hedge PnL for the current price point 'p'
        if p >= p0_val:
            il = calculate_il_A(p, p0_val, calculate_delta_xA_sell(L_val, p0_val, p))
            # PnL of the fixed xA_hedge position, opened at p0
            hedge = xA_hedge_val * (p - p0_val)
        else:
            il = calculate_il_B(p, p0_val, calculate_delta_xB_sell(L_val, p0_val, p))
            # PnL of the fixed xB_hedge position, opened at p0
            hedge = xB_hedge_val * (1/p - 1/p0_val)

        il_list.append(il)
        hedge_list.append(hedge)
        net_list.append(hedge - il)

        # Calculate fees for this step (from previous price to current price)
        if i > 0:
            # Get token holdings at current price
            current_xA_for_fee_calc = calculate_xA(L_val, p, p_max_val)
            current_xB_for_fee_calc = calculate_xB(L_val, p, p_min_val)

            # Determine token bought and accrue fees
            # If price increased (p > p_arr[i-1]), LP sold A, bought B
            if p > p_arr[i-1]:
                # delta_xB_traded represents the amount of Token B the LP received (bought)
                delta_xB_traded = current_xB_for_fee_calc - prev_xB_for_fee_calc
                if delta_xB_traded > 0: # Ensure positive change (LP bought B)
                    accumulated_fees_B += delta_xB_traded * fee_rate_val
            # If price decreased (p < p_arr[i-1]), LP sold B, bought A
            elif p < p_arr[i-1]:
                # delta_xA_traded represents the amount of Token A the LP received (bought)
                delta_xA_traded = current_xA_for_fee_calc - prev_xA_for_fee_calc
                if delta_xA_traded > 0: # Ensure positive change (LP bought A)
                    accumulated_fees_A += delta_xA_traded * fee_rate_val

            # Update prev_xA/xB for the next iteration
            prev_xA_for_fee_calc = current_xA_for_fee_calc
            prev_xB_for_fee_calc = current_xB_for_fee_calc
        else:
            # For the very first point (i=0), no trades have occurred yet, so no fees accumulated.
            # prev_xA_for_fee_calc and prev_xB_for_fee_calc are already set to p0 holdings.
            pass

        fees_A_list.append(accumulated_fees_A)
        fees_B_list.append(accumulated_fees_B)

    return np.array(il_list), np.array(hedge_list), np.array(net_list), np.array(fees_A_list), np.array(fees_B_list)

# Execute the calculation function for the simulated path
il_path, hedge_path, net_pnl_path, fees_A_path, fees_B_path = \
    compute_il_hedge_pnl_and_fees(p_path, L, p0, pmin, pmax, fee_rate, xA_hedge, xB_hedge)

# --- Plot: Simulated Price + PnL Tracking + Fees ---
# Create a figure with three subplots stacked vertically
fig2, (ax2, ax3, ax4) = plt.subplots(3, 1, figsize=(10, 9), sharex=True)

time_grid = np.linspace(0, T, steps)

# Subplot 1: Price Path
ax2.plot(time_grid, p_path, label="Simulated Price", color="black", linewidth=2)
ax2.axhline(p0, color="gray", linestyle=":", linewidth=1.5, label="$p_0$")
ax2.set_ylabel("Price $p$", fontsize=12)
ax2.set_title("Simulated Price Path, PnL, and Accumulated Fees Over Time", fontsize=14)
ax2.legend(fontsize=10)
ax2.grid(True, linestyle='--', alpha=0.7)

# Subplot 2: IL, Hedge, Net PnL
ax3.plot(time_grid, il_path, label="Impermanent Loss", color='red', linewidth=2)
ax3.plot(time_grid, hedge_path, label="Hedge PnL", color='green', linewidth=2)
ax3.plot(time_grid, net_pnl_path, label="Net PnL (Hedge - IL)", color='blue', linewidth=2, linestyle='--')
ax3.set_ylabel("PnL", fontsize=12)
ax3.legend(fontsize=10)
ax3.grid(True, linestyle='--', alpha=0.7)

# Subplot 3: Accumulated Fees
ax4.plot(time_grid, fees_A_path, label="Accumulated Fees (Token A)", color='purple', linewidth=2)
ax4.plot(time_grid, fees_B_path, label="Accumulated Fees (Token B)", color='orange', linewidth=2)
ax4.set_xlabel("Time", fontsize=12)
ax4.set_ylabel("Accumulated Fees", fontsize=12)
ax4.legend(fontsize=10)
ax4.grid(True, linestyle='--', alpha=0.7)

# Adjust layout to prevent overlapping titles/labels
plt.tight_layout()
st.pyplot(fig2)
