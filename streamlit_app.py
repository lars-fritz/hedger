import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="CL IL Hedge Simulator", layout="wide")
st.title("💧 Concentrated Liquidity IL, Hedge & Fee Simulator")

# --- User Inputs ---
p0 = st.number_input("Initial Price $p_0$", min_value=0.0001, value=1.0)
pmin = st.number_input("Lower Bound $p_{min}$", min_value=0.0001, max_value=p0 - 0.0001, value=0.8)
pmax = st.number_input("Upper Bound $p_{max}$", min_value=p0 + 0.0001, value=1.2)
L = st.number_input("Liquidity $L$", min_value=0.0001, value=1000.0)
vol = st.number_input("Volatility (annualized, e.g. 0.1 = 10%)", min_value=0.0001, value=0.1)
steps = st.slider("Number of time steps", min_value=10, max_value=500, value=100)
fee_rate = st.number_input("Fee rate (e.g. 0.003 = 0.3%)", min_value=0.0, max_value=0.1, value=0.003)

# --- Static View (IL vs Hedge) ---
sqrt_p0 = np.sqrt(p0)
sqrt_pmin = np.sqrt(pmin)
sqrt_pmax = np.sqrt(pmax)
p_grid = np.linspace(pmin, pmax, 500)

def IL_A(p):
    delta_xA = L * (1/np.sqrt(p0) - 1/np.sqrt(p))
    return (p - np.sqrt(p0 * p)) * delta_xA

def IL_B(p):
    delta_xB = L * (np.sqrt(p0) - np.sqrt(p))
    return (1/p - 1/np.sqrt(p0 * p)) * delta_xB

il_vals = np.where(p_grid >= p0, IL_A(p_grid), IL_B(p_grid))

dxA_max = L * (1/sqrt_p0 - 1/sqrt_pmax)
xA_hedge = ((pmax - np.sqrt(p0 * pmax)) / (pmax - p0)) * dxA_max

dxB_max = L * (sqrt_p0 - sqrt_pmin)
xB_hedge = ((1/pmin - 1/np.sqrt(p0 * pmin)) / (1/pmin - 1/p0)) * dxB_max

def hedge_A_pnl(p): return xA_hedge * (p - p0)
def hedge_B_pnl(p): return xB_hedge * (1/p - 1/p0)
hedge_vals = np.where(p_grid >= p0, hedge_A_pnl(p_grid), hedge_B_pnl(p_grid))

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

st.markdown("### 🖐️ Hedge Sizing")
st.latex(r"x_A^{\text{hedge}} = %.4f" % xA_hedge)
st.latex(r"x_B^{\text{hedge}} = %.4f" % xB_hedge)

# --- Pre-computations ---
dt = 1 / steps

# --- Price Path Simulation ---
np.random.seed()  # ensure randomness without fixed seed
price_path = [p0]
for _ in range(steps):
    drift = -0.5 * vol ** 2 * dt
    shock = np.random.normal(0, vol * np.sqrt(dt))
    new_price = price_path[-1] * np.exp(drift + shock)
    price_path.append(new_price)

price_path = np.array(price_path)

# --- CL math ---
def get_token_amounts(p, L, pmin, pmax):
    sqrt_p = np.sqrt(p)
    if p <= pmin:
        x = L * (1 / np.sqrt(pmin) - 1 / np.sqrt(pmax))
        y = 0
    elif p >= pmax:
        x = 0
        y = L * (np.sqrt(pmax) - np.sqrt(pmin))
    else:
        x = L * (1 / sqrt_p - 1 / np.sqrt(pmax))
        y = L * (sqrt_p - np.sqrt(pmin))
    return x, y

# --- Hedge sizing functions ---
def hedge_A(p):
    sqrt_p = np.sqrt(p)
    dxA = L * (1 / sqrt_p0 - 1 / sqrt_p)
    IL = (p - np.sqrt(p0 * p)) * dxA
    return dxA, IL

def hedge_B(p):
    sqrt_p = np.sqrt(p)
    dxB = L * (sqrt_p0 - sqrt_p)
    IL = (1 / p - 1 / np.sqrt(p0 * p)) * dxB
    return dxB, IL

# --- Simulation Loop ---
xA_prev, xB_prev = get_token_amounts(p0, L, pmin, pmax)
hedge_position = 0
hedge_token = None
realized_pnl = [0.0]
unrealized_pnl = [0.0]
il_history = [0.0]
fee_history = [0.0]

cum_fee = 0.0
cum_pnl = 0.0

for i in range(1, len(price_path)):
    p = price_path[i]
    prev_p = price_path[i - 1]
    xA, xB = get_token_amounts(p, L, pmin, pmax)
    dxA = xA - xA_prev
    dxB = xB - xB_prev
    fee = 0.0
    if dxA > 0:
        fee += fee_rate * dxA
    if dxB > 0:
        fee += fee_rate * dxB
    cum_fee += fee

    if p >= p0:
        xA_target, IL = hedge_A(p)
        token = "A"
    else:
        xB_target, IL = hedge_B(p)
        token = "B"

    if hedge_token != token:
        if hedge_token == "A":
            cum_pnl += hedge_position * (p - prev_p)
        elif hedge_token == "B":
            cum_pnl += -hedge_position * (1 / p - 1 / prev_p)
        hedge_position = 0

    hedge_token = token

    if token == "A":
        cum_pnl += hedge_position * (p - prev_p)
    else:
        cum_pnl += -hedge_position * (1 / p - 1 / prev_p)

    xA_prev, xB_prev = xA, xB
    il_history.append(IL)
    realized_pnl.append(cum_pnl)
    fee_history.append(cum_fee)
    unrealized_pnl.append(cum_pnl - IL)

# --- Plotting ---
fig, axs = plt.subplots(2, 2, figsize=(14, 8))
axs[0, 0].plot(price_path, label="Price")
axs[0, 0].axhline(p0, color='gray', linestyle='--', label="$p_0$")
axs[0, 0].set_title("Simulated Price Path")
axs[0, 0].legend()
axs[0, 0].grid(True)

axs[0, 1].plot(il_history, label="Impermanent Loss", color="red")
axs[0, 1].plot(realized_pnl, label="Hedge PnL", color="green")
axs[0, 1].plot(unrealized_pnl, label="Net PnL", color="blue")
axs[0, 1].set_title("PnL vs IL")
axs[0, 1].legend()
axs[0, 1].grid(True)

axs[1, 0].plot(fee_history, label="Cumulative Fees", color="purple")
axs[1, 0].set_title("Fees Collected Over Time")
axs[1, 0].legend()
axs[1, 0].grid(True)

net_plus_fees = np.array(unrealized_pnl) + np.array(fee_history)
axs[1, 1].plot(net_plus_fees, label="Net PnL incl. Fees", color="darkorange")
axs[1, 1].set_title("Net PnL Including Fees")
axs[1, 1].legend()
axs[1, 1].grid(True)

st.pyplot(fig)

st.markdown("### 📊 Final Summary")
st.write(f"Final Price: **{price_path[-1]:.4f}**")
st.write(f"Impermanent Loss: **{il_history[-1]:.4f}**")
st.write(f"Hedge PnL: **{realized_pnl[-1]:.4f}**")
st.write(f"Cumulative Fees: **{fee_history[-1]:.4f}**")
st.write(f"Net PnL (w/o fees): **{unrealized_pnl[-1]:.4f}**")
st.write(f"Net PnL (incl. fees): **{net_plus_fees[-1]:.4f}**")
