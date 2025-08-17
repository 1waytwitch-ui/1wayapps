import streamlit as st
from pycoingecko import CoinGeckoAPI
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date

# Initialiser CoinGecko
cg = CoinGeckoAPI()

# Récupérer prix historique réel (USD) pour un coin sur une période donnée
def get_historical_prices(coin_id, start_date):
    days = (date.today() - start_date).days
    data = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency='usd', days=days)
    prices = data['prices']  # list [timestamp, price]
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date
    df = df.set_index('date')
    df = df.loc[start_date:]  # filtrer à partir de la date choisie
    return df['price']

# Paramètres du thème flashy crypto
def set_plot_style():
    plt.style.use('dark_background')
    plt.rcParams.update({
        'axes.facecolor': '#1a1a1a',
        'axes.edgecolor': '#00ffcc',
        'axes.labelcolor': '#00ffcc',
        'xtick.color': '#00ffff',
        'ytick.color': '#00ffff',
        'grid.color': '#333333',
        'grid.linestyle': '--',
        'text.color': '#00ffcc',
        'legend.facecolor': '#222222',
        'legend.edgecolor': '#00ffcc',
    })

def main():
    st.title("Stratégie de Farming Crypto 🚀")

    # Date de début par défaut : 1er janvier de l'année en cours
    default_start = date(datetime.today().year, 1, 1)
    start_date = st.date_input("Date de début", value=default_start)

    coins = {
        "weth": "Wrapped Ether",
        "usd-coin": "USDC (Stablecoin)",
        "tether": "USDT (Stablecoin)",
        "bitcoin": "Bitcoin (BTC)",
    }

    selected_coins = st.multiselect("Choisir les cryptos", options=list(coins.keys()), format_func=lambda x: coins[x], default=["weth", "usd-coin"])

    if st.button("Télécharger les prix historiques"):
        with st.spinner("Récupération des données..."):
            price_data = {}
            for coin in selected_coins:
                prices = get_historical_prices(coin, start_date)
                price_data[coin] = prices

            df_prices = pd.DataFrame(price_data)
            df_prices = df_prices.fillna(method='ffill').fillna(method='bfill')

            set_plot_style()
            fig, ax = plt.subplots(figsize=(12, 6))
            for coin in selected_coins:
                ax.plot(df_prices.index, df_prices[coin], label=coins[coin])

            ax.set_title("Evolution des prix historiques")
            ax.set_xlabel("Date")
            ax.set_ylabel("Prix en USD")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

    st.markdown("---")
    st.markdown("<center>Développé par <b>1way</b></center>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
