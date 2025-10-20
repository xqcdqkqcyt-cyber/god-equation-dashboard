import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Construct: God Equation Tuner — Scientific Mode")

# Sidebar controls
st.sidebar.header("Parameters (scientific)")
a = st.sidebar.slider("a (self-feedback)", -1.5, 1.5, 0.6, 0.01)
b = st.sidebar.slider("b (baseline bias)", -1.0, 1.0, -0.1, 0.01)
rho = st.sidebar.slider("rho (ergodic coupling)", 0.0, 1.0, 0.4, 0.01)
mu = st.sidebar.slider("mu (ensemble mean)", -2.0, 2.0, 0.0, 0.01)
show_time = st.sidebar.checkbox("Show time-series simulation", True)
reset_strength = st.sidebar.slider("Reset strength (s)", 0.0, 1.0, 0.8, 0.01)
reset_times = st.sidebar.multiselect("Reset iterations", [50,100,150,200,300], default=[100,250])

# Compute fixed point
denom = 1 - (1-rho)*a
if abs(denom) < 1e-6:
    x_star = float('nan')
    stability = False
else:
    x_star = ((1-rho)*b + rho*mu) / denom
    stability = abs((1-rho)*a) < 1

col1, col2 = st.columns([1,1])

with col1:
    st.subheader("Analytic fixed point")
    st.write("x* = ((1-rho)*b + rho*mu) / (1 - (1-rho)*a)")
    st.metric("x*", f"{x_star:.6f}" if (not np.isnan(x_star)) else "undefined")
    st.write("Stability (| (1-rho)*a | < 1):", "✅ Stable" if stability else "🔴 Unstable / Near singular")

    # Phase portrait slice
    xs = np.linspace(-2,2,400)
    map_vals = (1-rho)* (a*xs + b) + rho*mu
    fig, ax = plt.subplots(figsize=(5,4))
    ax.plot(xs, map_vals, label='map: x_{n+1}')
    ax.plot(xs, xs, '--', label='identity line')
    ax.set_xlim(-2,2); ax.set_ylim(-2,2)
    ax.set_title(f"Phase slice (a={{a:.2f}}, rho={{rho:.2f}})")
    ax.legend()
    st.pyplot(fig)

with col2:
    st.subheader("Parameter impacts (slices)")
    rhos = np.linspace(0,1,201)
    denom_s = 1 - (1-rhos)*0.5
    xs = ((1-rhos)*b + rhos*mu) / np.where(np.abs(denom_s)>1e-6, denom_s, np.nan)
    fig2, ax2 = plt.subplots(figsize=(6,2))
    ax2.plot(rhos, xs, label='a=0.5 example')
    ax2.set_xlabel('rho'); ax2.set_ylabel('x*')
    ax2.grid(True, linestyle='--', linewidth=0.4)
    st.pyplot(fig2)

# Time-series simulation
if show_time:
    T = 400
    x = np.zeros(T)
    x[0] = -0.8
    sigma = 0.02
    for n in range(T-1):
        x[n+1] = (1-rho)*(a*x[n] + b) + rho*mu + sigma*np.random.randn()
        if (n+1) in reset_times:
            s = reset_strength
            x[n+1] = (1-s)*x[n+1] + s*mu
    st.subheader("Time-series simulation (linear local map)")
    figt, axt = plt.subplots(figsize=(8,3))
    axt.plot(x); axt.set_xlabel("iteration n"); axt.set_ylabel("x_n")
    for rt in reset_times:
        axt.axvline(rt, linestyle='--', alpha=0.7)
    st.pyplot(figt)

st.sidebar.markdown("---")
st.sidebar.markdown("Export config: use the 'Share' button or copy parameter values.")
st.write("Notes: This is a scientific reduction (linear local map). For the full operator model see the technical manual.")