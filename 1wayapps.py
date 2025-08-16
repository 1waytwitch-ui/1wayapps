import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import requests

st.set_page_config(page_title="Farming Strategy Simulator", layout="wide")

@st.cache_data
def gecko_historical(ticker, vs_currency='usd', days='max'):
    url = f"https://api.coingecko.com/api/v3/coins/{ticker}/market_chart"
    params = {"vs_currency": vs_currency, "days": days}
    r = requests.get(url, params=params).json()
    prices = pd.DataFrame(r['prices'])
    prices.columns = ['date', 'price']
    prices['date'] = pd.to_datetime(prices['date'], unit='ms')
    prices.set_index('date', inplace=True)
    return prices

def farm_simulate(pair, apr, start='2021-01-01'):
    prices = pd.DataFrame()
    for coin in pair:
        try:
            df = gecko_historical(coin)
            prices[coin] = df['price']
        except:
            st.warning(f"Erreur lors du téléchargement des prix pour {coin}")

    if len(prices.columns) == 2:
        prices.dropna(inplace=True)
        start = pd.to_datetime(start)
        farm = prices.loc[prices.index >= start].copy()
        farm = farm / farm.iloc[0]
        farm['ratio'] = farm.iloc[:, 1] / farm.iloc[:, 0]
        farm['iloss'] = 2 * (farm['ratio']**0.5 / (1 + farm['ratio'])) - 1
        farm['rewards'] = pd.Series(1 * apr / 100 / 365, index=farm.index).cumsum()
        farm['buy_hold'] = (farm.iloc[:, 0] + farm.iloc[:, 1]) / 2
        farm['farm'] = farm.buy_hold * (1 + farm.iloss) * (1 + farm.rewards)

        b_h = farm['buy_hold'].iloc[-1] - 1
        iloss = farm['iloss'].iloc[-1]
        rewards = farm['rewards'].iloc[-1]
        net_farming = b_h * (1 + iloss) * (1 + rewards)

        # Résumé
        results = {
            'Token 1': pair[0],
            'Token 2': pair[1],
            'Date de début': start.date(),
            'APR annuel': f"{apr:.0f}%",
            'Buy & Hold': f"{b_h:.2%}",
            'Impermanent Loss': f"{iloss:.2%}",
            'Farming Rewards': f"{rewards:.2%}",
            'Résultat Farming net': f"{net_farming:.2%}"
        }

        # Graphiques
        fig, ax = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        ax[0].plot(farm.index, farm.iloc[:, :2])
        ax[0].plot(farm.index, farm['buy_hold'], label='Buy & Hold', linestyle='--')
        ax[0].plot(farm.index, farm['farm'], label='Farming Strategy', linestyle='--')
        ax[0].legend()
        ax[0].set_title('Évolution des prix et stratégies')
        ax[0].grid()

        ax[1].plot(farm.index, farm['iloss'], label='Impermanent Loss')
        ax[1].plot(farm.index, farm['rewards'], label='Farming Rewards')
        ax[1].legend()
        ax[1].set_title('Impermanent Loss vs Farming Rewards')
        ax[1].grid()

        return results, fig
    else:
        return "Erreur : Données historiques insuffisantes", None


# UI Streamlit
st.title("📈 Farming Strategy Simulator (DeFi)")

with st.sidebar:
    st.markdown("### Paramètres")
    token1 = st.text_input("Token 1 (ex: bitcoin)", value="bitcoin")
    token2 = st.text_input("Token 2 (ex: tether)", value="tether")
    apr = st.slider("APR annuel (%)", 0, 100, 25)
    start_date = st.date_input("Date de départ", value=datetime.date(2021, 1, 1))
    simulate = st.button("Lancer la simulation")

if simulate:
    with st.spinner("Simulation en cours..."):
        result, chart = farm_simulate([token1, token2], apr, str(start_date))

    if isinstance(result, dict):
        st.subheader("🔍 Résumé des résultats")
        st.json(result)
        st.pyplot(chart)
    else:
        st.error(result)
