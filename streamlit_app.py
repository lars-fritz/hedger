import streamlit as st

st.set_page_config(
    page_title="Hedging Impermanent Loss in Concentrated Liquidity",
    layout="wide"
)

st.title("Hedging Impermanent Loss (IL) in Concentrated Liquidity")

st.markdown(
    """
    ## Setup

    Consider an initial liquidity position consisting of tokens $A$ and $B$ in a concentrated liquidity (CL) pool centered at price $p_0$. The liquidity range is bounded by:

    $$
    p_{\\min} \\leq p \\leq p_{\\max}
    $$

    At initialization, the liquidity provider (LP) sets the price bounds $p_{\\min}$ and $p_{\\max}$ and deposits a corresponding amount of tokens $A$ and $B$.

    Let $L$ be the liquidity parameter of the position. Then, for any current price $p$ within the range, the token holdings are given by:

    $$
    x_A(p) = L\\left( \\frac{1}{\\sqrt{p}} - \\frac{1}{\\sqrt{p_{\\max}}} \\right), \\quad x_B(p) = L \\left( \\sqrt{p} - \\sqrt{p_{\\min}} \\right)
    $$

    ---

    ## Token Trades and Net Flows

    The LP initialized the position at $p_0$. As price moves within the range, the LP trades tokens against the pool:

    ### If price increases from $p_0$ to $p$ ($p_0 < p \\leq p_{\\max}$):

    - Token $A$ is **sold**: 

    $$
    \\Delta x_A^{\\rm{sell}} = L \\left( \\frac{1}{\\sqrt{p_0}} - \\frac{1}{\\sqrt{p}} \\right)
    $$

    - Token $B$ is **bought**: 

    $$
    \\Delta x_B^{\\rm{buy}} = L \\left( \\sqrt{p} - \\sqrt{p_0} \\right)
    $$

    - Effective execution price:

    $$
    p^{\\rm{true}}_{\\rm{sellA}} = \\frac{\\Delta x_B^{\\rm{buy}}}{\\Delta x_A^{\\rm{sell}}} = \\sqrt{p_0 p}
    $$

    ### If price decreases from $p_0$ to $p$ ($p_{\\min} \\leq p < p_0$):

    - Token $B$ is **sold**: 

    $$
    \\Delta x_B^{\\rm{sell}} = L \\left( \\sqrt{p_0} - \\sqrt{p} \\right)
    $$

    - Token $A$ is **bought**: 

    $$
    \\Delta x_A^{\\rm{buy}} = L \\left( \\frac{1}{\\sqrt{p}} - \\frac{1}{\\sqrt{p_0}} \\right)
    $$

    - Effective execution price:

    $$
    p^{\\rm{true}}_{\\rm{sellB}} = \\frac{\\Delta x_B^{\\rm{sell}}}{\\Delta x_A^{\\rm{buy}}} = \\sqrt{p_0 p}
    $$

    ---

    ## Impermanent Loss (IL) — Sell Token Formulation

    We define IL as the **shortfall in proceeds** from having sold a token via liquidity provision compared to selling at the final market price.

    This formulation expresses IL entirely in terms of the **token sold**, making it **operationally superior for practitioners**. Unlike the standard IL formula (which compares total portfolio value to HODLing), this version reflects the **execution price difference** and helps determine how much needs to be hedged or recovered.

    ### IL from Selling Token A (price rises to $p$):

    $$
    \\text{IL}_A(p) = \\left(p - \\sqrt{p_0 p} \\right) \\Delta x_A^{\\rm{sell}}
    $$

    ### IL from Selling Token B (price falls to $p$):

    $$
    \\text{IL}_B(p) = \\left( \\frac{1}{\\sqrt{p_0 p}} - \\frac{1}{p} \\right) \\Delta x_B^{\\rm{sell}}
    $$

    Note: in the second case, the loss is expressed using **inverse price** since $B$ is sold as price decreases.

    ---

    ## Worst-Case IL Scenarios

    To understand the risk bounds of LPing, we evaluate IL at the boundaries:

    ### Max Loss from Selling Token A:

    $$
    \\text{IL}_A^{\\max} = \\left(p_{\\max} - \\sqrt{p_0 p_{\\max}} \\right) \\Delta x_A^{\\rm{sell}}
    $$

    ### Max Loss from Selling Token B:

    $$
    \\text{IL}_B^{\\max} = \\left(\\frac{1}{p_{\\min}}- \\frac{1}{\\sqrt{p_0 p_{\\min}}}  \\right) \\Delta x_B^{\\rm{sell}}
    $$

    ---

    ## Hedging Strategy

    Having expressed impermanent loss (IL) in terms of **tokens sold**, a **natural and precise hedging strategy** emerges.

    ### Hedging Objective

    The aim is to fully compensate for the IL incurred if the price moves to either boundary of the LP's liquidity range. We accomplish this by **holding a quantity of the token sold** such that its profit at the new price offsets the realized shortfall in the LP.

    Importantly, we do not need to hedge value drift — only the **execution shortfall** from passive liquidity provision.

    ---

    ### Hedging Token A (Price Rises from $p_0$ to $p$)

    - We focus on the **worst-case IL**, which occurs when price reaches $p_{\\max}$.
    - At that point, the LP will have sold:

    $$
    \\Delta x_A^{\\rm{sell}} = L \\left( \\frac{1}{\\sqrt{p_0}} - \\frac{1}{\\sqrt{p_{\\max}}} \\right)
    $$

    - The realized execution price was $\\sqrt{p_0 p_{\\max}}$, but the market is now at $p_{\\max}$.
    - The LP thus suffers:

    $$
    \\text{IL}_A^{\\max} = \\left(p_{\\max} - \\sqrt{p_0 p_{\\max}} \\right) \\Delta x_A^{\\rm{sell}}
    $$

    To hedge this, the LP buys and **holds** a quantity $x_A^{\\rm{hedge}}$ of token $A$ such that its profit at $p_{\\max}$ matches the IL:

    $$
    x_A^{\\rm{hedge}} \\cdot (p_{\\max} - p_0) = \\left(p_{\\max} - \\sqrt{p_0 p_{\\max}} \\right) \\Delta x_A^{\\rm{sell}}
    $$

    Solving for $x_A^{\\rm{hedge}}$, we obtain:

    $$
    \\boxed{
    x_A^{\\rm{hedge}} = \\frac{p_{\\max} - \\sqrt{p_0 p_{\\max}}}{p_{\\max} - p_0} \\cdot \\Delta x_A^{\\rm{sell}}
    }
    $$

    ---

    ### Hedging Token B (Price Falls from $p_0$ to $p$)

    Symmetrically, the LP sells token B as price falls from $p_0$ to $p_{\\min}$, incurring:

    $$
    \\text{IL}_B^{\\max} = \\left(\\frac{1}{p_{\\min}} - \\frac{1}{\\sqrt{p_0 p_{\\min}}} \\right) \\cdot \\Delta x_B^{\\rm{sell}}
    $$

    To hedge this, we take a **long position in token B**, with size $x_B^{\\rm{hedge}}$ satisfying:

    $$
    x_B^{\\rm{hedge}} \\cdot \\left(\\frac{1}{p_{\\min}} - \\frac{1}{p_0} \\right) = \\text{IL}_B^{\\max}
    $$

    Solving:

    $$
    \\boxed{
    x_B^{\\rm{hedge}} = \\frac{\\frac{1}{p_{\\min}} - \\frac{1}{\\sqrt{p_0 p_{\\min}}}}{\\frac{1}{p_{\\min}} - \\frac{1}{p_0}} \\cdot \\Delta x_B^{\\rm{sell}}
    }
    $$

    ---

    ### Leveraged Implementation

    Holding these hedges in full would require idle capital, which is often impractical. Instead, the LP can open a **leveraged long** position in the relevant asset:

    - Use **margin or derivatives** to size the position with minimal capital.
    - Hedge is **directional and delta-efficient** — no unnecessary overhedging.

    This makes the strategy **capital-efficient and scalable** for professional LPs or funds.

    ---

    ### Summary of Hedge Sizes

    | Price Move            | Token Sold | Hedge Token | Hedge Size                                                                                   |
    |----------------------|------------|-------------|---------------------------------------------------------------------------------------------|
    | $p_0 \\to p_{\\max}$    | $A$        | $A$         | $\\frac{p_{\\max} - \\sqrt{p_0 p_{\\max}}}{p_{\\max} - p_0} \\Delta x_A^{\\rm{sell}}$             |
    | $p_0 \\to p_{\\min}$    | $B$        | $B$         | $\\frac{1/p_{\\min} - 1/\\sqrt{p_0 p_{\\min}}}{1/p_{\\min} - 1/p_0} \\Delta x_B^{\\rm{sell}}$     |

    ---

    ## Dynamic Hedge Activation and Closing

    While the simplest hedging strategy activates the hedge immediately at the LP initialization price $p_0$, a more practical and capital-efficient approach is to **delay opening hedge positions until the price crosses certain activation thresholds**.

    ### Motivation

    - Opening hedges immediately at $p_0$ may tie up capital unnecessarily if the price remains stable.
    - Waiting until the price moves beyond a threshold $p_{\\rm{up}} > p_0$ (for upward moves) or $p_{\\rm{down}} < p_0$ (for downward moves) focuses hedging efforts on significant price movements that actually incur impermanent loss.
    - Similarly, closing the hedge quickly when the price reverts below (or above) the threshold reduces capital costs and risk.

    ### Hedge Size Computation with Thresholds

    The hedge size scales the **total impermanent loss amount** (computed from $p_0$ to the boundary) over the **remaining price interval** from threshold to boundary. The total amount of tokens sold $\\Delta x^{\\rm{sell}}$ remains as initially defined:

    - **For price rising beyond $p_{\\rm{up}}$:**

    $$
    x_A^{\\rm{hedge}} = \\frac{p_{\\max} - \\sqrt{p_0 p_{\\max}}}{p_{\\max} - p_{\\rm{up}}} \\cdot \\Delta x_A^{\\rm{sell}}
    $$

    where

    $$
    \\Delta x_A^{\\rm{sell}} = L \\left( \\frac{1}{\\sqrt{p_0}} - \\frac{1}{\\sqrt{p_{\\max}}} \\right)
    $$

    - **For price falling below $p_{\\rm{down}}$:**

    $$
    x_B^{\\rm{hedge}} = \\frac{\\frac{1}{\\sqrt{p_0 p_{\\min}}} - \\frac{1}{p_{\\min}}}{\\frac{1}{p_{\\rm{down}}} - \\frac{1}{p_0}} \\cdot \\Delta x_B^{\\rm{sell}}
    $$

    where

    $$
    \\Delta x_B^{\\rm{sell}} = L \\left( \\sqrt{p_0} - \\sqrt{p_{\\min}} \\right)
    $$

    ### Interpretation

    - The numerator terms quantify the total impermanent loss if the price reaches the boundary.
    - The denominator terms scale the hedge according to the price interval between the activation threshold and the boundary.
    - This method **activates the hedge only when the price crosses the threshold**, scaling the hedge size proportionally to the price interval still exposed to IL.
    - It avoids tying up capital prematurely or overhedging when price moves are limited.

    ---

    ### Summary Table: Hedge Sizes with Activation Thresholds

    | Price Move           | Token Sold | Hedge Token | Hedge Size                                                                                   |
    |----------------------|------------|-------------|---------------------------------------------------------------------------------------------|
    | $p_{\\rm{up}} \\to p_{\\max}$     | $A$        | $A$         | $\\frac{p_{\\max} - \\sqrt{p_0 p_{\\max}}}{p_{\\max} - p_{\\rm{up}}} \\cdot \\Delta x_A^{\\rm{sell}}$  |
    | $p_{\\min} \\to p_{\\rm{down}}$   | $B$        | $B$         | $\\frac{\\frac{1}{p_{\\min}} - \\frac{1}{\\sqrt{p_0 p_{\\min}}}}{\\frac{1}{p_{\\min}} - \\frac{1}{p_{\\rm{down}}}} \\cdot \\Delta x_B^{\\rm{sell}}$ |

    ---

    This dynamic threshold approach improves capital efficiency and aligns hedge size with actual impermanent loss risk as price evolves.

    ### 📌 Note on IL Behavior

    While our formulation of impermanent loss appears *linear* in small price shifts, this is due to its grounding in **execution shortfall** rather than total portfolio revaluation. The traditional IL definition — which compares the LP’s portfolio value to HODLing — is quadratic in price movements.

    Our execution-based definition focuses on the **token sold** and computes the shortfall compared to the final market price. This view aligns more closely with an **order book or execution price** perspective, which is especially practical for hedging and trade planning.

    Importantly, both formulations are **mathematically equivalent** — they just differ in interpretation and utility.
    """
)


