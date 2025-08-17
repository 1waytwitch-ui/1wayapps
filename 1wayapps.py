import streamlit as st
from pycoingecko import CoinGeckoAPI
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date

cg = CoinGeckoAPI()

# Fonction pour récupérer prix historique en USD depuis CoinGecko
def get_price_history(coin_id, start_date):
    start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    end_timestamp = int(datetime.now().timestamp())
    data = cg.get_coin_market_chart_range_by_id(id=coin_id, vs_currency='usd',
                                               from_timestamp=start_timestamp, to_timestamp=end_timestamp)
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date
    df = df.groupby('date').last()
    df = df[['price']]
    return df

# Date début par défaut : 1er janvier année courante
default_start_date = date.today().replace(month=1, day=1).strftime("%Y-%m-%d")

st.title("Stratégie de Farming Crypto 🚀")

start_date = st.date_input("Date de début", value=datetime.strptime(default_start_date, "%Y-%m-%d"))

# Liste des cryptos avec les bons IDs CoinGecko
cryptos = {
    'weth': 'Wrapped Ether',
    'usd-coin': 'USDC (Stablecoin)',
    'bitcoin': 'Bitcoin',
    'dai': 'DAI (Stablecoin)',
}

selected_coins = st.multiselect(
    "Choisir les cryptos", options=list(cryptos.keys()),
    format_func=lambda x: cryptos[x],
    default=['weth', 'usd-coin']
)

if st.button("Télécharger les prix historiques"):
    # Récupération des données prix
    dfs = {}
    for coin in selected_coins:
        df = get_price_history(coin, start_date.strftime("%Y-%m-%d"))
        dfs[coin] = df

    # Merge sur la date
    prices_df = pd.concat(dfs.values(), axis=1)
    prices_df.columns = [cryptos[c] for c in dfs.keys()]
    prices_df.dropna(inplace=True)

    # Affichage prix historiques
    plt.style.use('dark_background' if st.get_option("theme.base") == "dark" else 'default')
    fig, ax = plt.subplots(figsize=(12,6))
    for col in prices_df.columns:
        ax.plot(prices_df.index, prices_df[col], label=col)
    ax.set_title("Evolution des prix historiques")
    ax.set_xlabel("Date")
    ax.set_ylabel("Prix en USD")
    ax.legend()
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    st.pyplot(fig)
