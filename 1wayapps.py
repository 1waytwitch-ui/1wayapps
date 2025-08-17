import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from mpl_toolkits.mplot3d import Axes3D

# Fonction fictive pour obtenir les prix — à remplacer avec l'API réelle
@st.cache_data
def pcsTokens():
    # Exemple fictif — à remplacer avec une vraie API ou dataframe
    data = {
        'symbol': ['CAKE', 'WBNB', 'USDT'],
        'price': [1.5, 300.0, 1.0]  # prix simulés
    }
    return pd.DataFrame(data)

def iloss_simulate(base_token, quote_token, value=100, base_pct_chg=0, quote_pct_chg=0):
    base_token = 'WBNB' if base_token.upper() == 'BNB' else base_token
    quote_token = 'WBNB' if quote_token.upper() == 'BNB' else quote_token

    tokens = pcsTokens()
    px_base = float(tokens.loc[tokens.symbol.str.upper() == base_token.upper()].price)
    px_quote = float(tokens.loc[tokens.symbol.str.upper() == quote_token.upper()].price)

    q_base, q_quote = (value / 2) / px_base, (value / 2) / px_quote

    pxs_base = [px_base * i / 100 for i in range(1, 301)]
    pxs_quote = [px_quote * i / 100 for i in range(1, 301)]

    rows = []
    for px_b in pxs_base:
        for px_q in pxs_quote:
            ratio = (px_b / px_base) / (px_q / px_quote)
            iloss = 2 * (ratio**0.5 / (1 + ratio)) - 1
            rows.append({'px_base': px_b, 'px_quote': px_q, 'impremante_loss': iloss})

    df = pd.DataFrame(rows)
    df_ok = df.dropna()

    if all(isinstance(i, (int, float)) for i in (value, base_pct_chg, quote_pct_chg)):
        px_base_f = px_base * (1 + base_pct_chg / 100)
        px_quote_f = px_quote * (1 + quote_pct_chg / 100)
        ratio = (px_base_f / px_base) / (px_quote_f / px_quote)
        iloss = 2 * (ratio**0.5 / (1 + ratio)) - 1
        value_f = (px_base_f * q_base + px_quote_f * q_quote) * (iloss + 1)
    else:
        px_base_f, px_quote_f = px_base, px_quote
        iloss = 0
        value_f = None

    # Plotting
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    x1 = np.linspace(df_ok['px_base'].min(), df_ok['px_base'].max(), len(df_ok['px_base'].unique()))
    y1 = np.linspace(df_ok['px_quote'].min(), df_ok['px_quote'].max(), len(df_ok['px_quote'].unique()))
    x2, y2 = np.meshgrid(x1, y1)
    Z = interpolate.griddata((df_ok['px_base'], df_ok['px_quote']), df_ok['impremante_loss'], (x2, y2), method='linear')
    Z[np.isnan(Z)] = df_ok.impremante_loss.mean()

    ax.plot_wireframe(x2, y2, Z, color='tab:blue', lw=0.6, alpha=0.6)
    ax.set_title('Impermanent Loss 3D Surface')
    ax.set_xlabel(f'Price {base_token}')
    ax.set_ylabel(f'Price {quote_token}')
    ax.set_zlabel('Impermanent Loss')
    ax.view_init(elev=25, azim=240)

    # Affichage final
    st.pyplot(fig)

    # Résumé
    st.subheader("Résultats")
    st.markdown(f"**Valeur initiale investie** : ${value:.2f}")
    st.markdown(f"**Prix initial de {base_token}** : ${px_base:.2f}")
    st.markdown(f"**Prix initial de {quote_token}** : ${px_quote:.2f}")
    st.markdown(f"**Changement estimé :** {base_token} {base_pct_chg}%, {quote_token} {quote_pct_chg}%")
    st.markdown(f"**Valeur finale estimée** : ${value_f:.2f}")
    st.markdown(f"**Impermanent Loss estimée** : {iloss:.2%}")

    return value_f, iloss


# Interface Streamlit
st.title("Simulation de l'Impermanent Loss")
st.markdown("Entrez les détails pour simuler la perte impermanente sur une paire de tokens.")

col1, col2 = st.columns(2)

with col1:
    base_token = st.text_input("Token de base (ex: CAKE)", value="CAKE")
    value = st.number_input("Montant initial investi ($)", value=100.0, step=10.0)
    base_pct_chg = st.number_input("Variation % du token de base", value=0)

with col2:
    quote_token = st.text_input("Token de cotation (ex: BNB)", value="BNB")
    quote_pct_chg = st.number_input("Variation % du token de cotation", value=0)

if st.button("Simuler"):
    try:
        value_f, iloss = iloss_simulate(base_token, quote_token, value, base_pct_chg, quote_pct_chg)
    except Exception as e:
        st.error(f"Erreur lors du calcul : {e}")
