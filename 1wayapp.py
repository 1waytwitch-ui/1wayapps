import streamlit as st
import pandas as pd
import requests
import time
import plotly.graph_objs as go

st.set_page_config(page_title="Crypto Charts", layout="wide")

# === Fonction pour récupérer les données de prix (CoinGecko) ===
@st.cache_data(ttl=60)
def get_crypto_data(coin_id, days=1, interval="minute"):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": interval
    }
    response = requests.get(url, params=params)
    data = response.json()

    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

# === Mapping simple nom → ID CoinGecko ===
crypto_map = {
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum",
    "USD Coin (USDC)": "usd-coin"
}

# === Sidebar navigation ===
st.sidebar.title("Navigation")
selected_coin_name = st.sidebar.selectbox("Choisissez une crypto", list(crypto_map.keys()))
coin_id = crypto_map[selected_coin_name]

# === Titre principal ===
st.title(f"Chart temps réel : {selected_coin_name}")

# === Chargement des données ===
with st.spinner("Chargement des données en temps réel..."):
    df = get_crypto_data(coin_id)

# === Affichage du graphique ===
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df["timestamp"],
    y=df["price"],
    mode="lines",
    name=selected_coin_name
))

fig.update_layout(
    title=f"Prix de {selected_coin_name} (USD)",
    xaxis_title="Temps",
    yaxis_title="Prix en USD",
    template="plotly_dark",
    autosize=True
)

st.plotly_chart(fig, use_container_width=True)

# === Dernier prix ===
st.metric("Dernier prix", f"${df['price'].iloc[-1]:,.2f}")
