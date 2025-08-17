import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from mpl_toolkits.mplot3d import Axes3D

# --- Simuler les prix (à remplacer avec API réelle) ---
@st.cache_data
def pcsTokens():
    data = {
        'symbol': ['CAKE', 'WBNB', 'USDT', 'USDC', 'WETH', 'BTCB'],
        'price': [1.5, 300.0, 1.0, 1.0, 1800.0, 29000.0]  # prix simulés
    }
    return pd.DataFrame(data)

# --- Mapping alias symboles ---
def normalize_token_symbol(symbol):
    aliases = {
        'BNB': 'WBNB',
        'ETH': 'WETH',
        'BTC': 'BTCB',
    }
    return aliases.get(symbol.upper(), symbol.upper())

# --- Simulation principale ---
def iloss_simulate(base_token, quote_token, value=100, base_pct_chg=0, quote_pct_chg=0):
    base_token = normalize_token_symbol(base_token)
    quote_token = normalize_token_symbol(quote_token)

    tokens = pcsTokens()

    try:
        px_base = float(tokens.loc[tokens.symbol.str.upper() == base_token].price)
        px_quote = float(tokens.loc[tokens.symbol.str.upper() == quote_token].price)
    except:
        st.error(f"Token introuvable : {base_token} ou {quote_token}")
        return None, None

    q_base, q_quote = (value / 2) / px_base, (value / 2) / px_quote

    pxs_base = [px_base * i / 100 for i in range(1, 301)]
    pxs_quote = [px_quote * i / 100 for i in range(1, 301)]

    rows = []
    for px_b in pxs_base:
        for px_q in pxs_quote:
            ratio = (px_b / px_base) / (px_q / px_quote)
            iloss = 2 * (ratio**0.5 / (1 + ratio)) - 1
            rows.append({'px_base': px_b, 'px_quote': px_q, 'impremante_loss': iloss})

    df = pd.DataFrame(rows).dropna()

    px_base_f = px_base * (1 + base_pct_chg / 100)
    px_quote_f = px_quote * (1 + quote_pct_chg / 100)
    ratio = (px_base_f / px_base) / (px_quote_f / px_quote)
    iloss = 2 * (ratio**0.5 / (1 + ratio)) - 1
    value_f = (px_base_f * q_base + px_quote_f * q_quote) * (1 + iloss)

    # --- Graphique 3D ---
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    x = np.linspace(df['px_base'].min(), df['px_base'].max(), len(df['px_base'].unique()))
    y = np.linspace(df['px_quote'].min(), df['px_quote'].max(), len(df['px_quote'].unique()))
    x2, y2 = np.meshgrid(x, y)

    Z = interpolate.griddata((df['px_base'], df['px_quote']), df['impremante_loss'], (x2, y2), method='linear')
    Z[np.isnan(Z)] = df['impremante_loss'].mean()

    ax.plot_wireframe(x2, y2, Z, color='tab:blue', lw=0.5, alpha=0.6)
    ax.set_title('Impermanent Loss 3D Surface')
    ax.set_xlabel(f'Price {base_token}')
    ax.set_ylabel(f'Price {quote_token}')
    ax.set_zlabel('Impermanent Loss')
    ax.view_init(elev=25, azim=240)

    # Marqueur position finale
    ax.scatter(px_base_f, px_quote_f, iloss, c='red', s=50, marker='o', label='Position finale')
    ax.legend()

    st.pyplot(fig)

    # Résumé des résultats
    st.subheader("📊 Résultats de la simulation")
    st.markdown(f"- **Valeur initiale investie** : `${value:.2f}`")
    st.markdown(f"- **Prix initial** : {base_token} = `${px_base:.2f}`, {quote_token} = `${px_quote:.2f}`")
    st.markdown(f"- **Variation appliquée** : {base_token} = `{base_pct_chg}%`, {quote_token} = `{quote_pct_chg}%`")
    st.markdown(f"- **Valeur finale estimée** : `${value_f:.2f}`")
    st.markdown(f"- **Impermanent Loss estimée** : `{iloss:.2%}`")

    return value_f, iloss

# --- Interface Utilisateur Streamlit ---
st.set_page_config(page_title="Simulation Impermanent Loss", layout="centered")
st.title("📉 Simulation de l'Impermanent Loss")
st.markdown("Simulez la perte impermanente sur une position LP avec une paire de tokens.")

available_tokens = ['CAKE', 'WBNB', 'WETH', 'BTCB', 'USDC', 'USDT']

col1, col2 = st.columns(2)
with col1:
    base_token = st.selectbox("Token de base", options=available_tokens, index=0)
    value = st.number_input("Montant initial investi ($)", value=100.0, step=10.0)
    base_pct_chg = st.number_input("Variation % du token de base", value=0, step=1)

with col2:
    quote_token = st.selectbox("Token de cotation", options=available_tokens, index=1)
    quote_pct_chg = st.number_input("Variation % du token de cotation", value=0, step=1)

if st.button("🚀 Simuler"):
    value_f, iloss = iloss_simulate(base_token, quote_token, value, base_pct_chg, quote_pct_chg)
