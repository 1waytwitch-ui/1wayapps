import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import datetime

# Exemple fictif de fonction geckoHistorical pour rappel (à remplacer par ta vraie fonction)
def geckoHistorical(token):
    # Simuler récupération des prix (remplacer par vraie API)
    dates = pd.date_range(start="2021-01-01", periods=500, freq='D')
    prices = pd.Series(100 + pd.np.cumsum(pd.np.random.randn(500)), index=dates).abs()
    return pd.DataFrame({'price': prices})

def farmSimulate(pair, apr, start_date, end_date):
    prices = pd.DataFrame()
    for coin in pair:
        st.write(f'Downloading {coin} prices...')
        try:
            df = geckoHistorical(coin)
            prices[coin] = df['price']
        except Exception as e:
            st.error(f'Error fetching prices for {coin}: {e}')
            return None

    if len(prices.columns) == 2:
        prices = prices.dropna()
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        farm = prices.loc[(prices.index >= start) & (prices.index <= end)]
        farm = farm.divide(farm.iloc[0])
        farm['ratio'] = farm.iloc[:, 1].divide(farm.iloc[:, 0])

        farm['iloss'] = 2 * (farm['ratio'] ** 0.5 / (1 + farm['ratio'])) - 1
        farm['rewards'] = pd.Series(1 * apr / 100 / 365, index=farm.index).cumsum()
        farm['buy_hold'] = (farm.iloc[:, 0] + farm.iloc[:, 1]) / 2
        farm['farm'] = farm.buy_hold * (1 + farm.iloss) * (1 + farm.rewards)

        cagrs = farm.iloc[-1] ** (1 / (365 / len(farm))) - 1
        sigmas = farm.pct_change().std() * (365 ** 0.5)
        sharpes = cagrs.divide(sigmas).round(2)
        dd = farm / farm.cummax() - 1

        fig = plt.figure(figsize=(15, 8))
        gs = GridSpec(nrows=2, ncols=4, figure=fig, height_ratios=[2, 1], hspace=0.45, wspace=0.35, top=.9)
        ax_upleft = fig.add_subplot(gs[0, 0:2])
        ax_upright = fig.add_subplot(gs[0, 2:])
        cols = 4
        ax_down = [fig.add_subplot(gs[1, i]) for i in range(cols)]

        ax_upleft.plot(farm.iloss.abs(), label='Impermanent Loss')
        ax_upleft.plot(farm.rewards, label='Farming Rewards')
        ax_upleft.legend()
        ax_upleft.grid()
        ax_upleft.set_title('Impermanent Loss vs Farming Rewards')
        ax_upleft.tick_params(axis='x', rotation=45)

        ax_upright.plot(farm.iloc[:, :2])
        ax_upright.plot(farm.buy_hold)
        ax_upright.plot(farm.farm)
        ax_upright.grid()
        ax_upright.legend([pair[0], pair[1], 'Buy & Hold', 'Farming Strategy'])
        ax_upright.set_title(f'{pair[0]} vs {pair[1]} vs Buy & Hold vs Farming strategy payoff')
        ax_upright.tick_params(axis='x', rotation=45)

        cagrs[[pair[0], pair[1], 'buy_hold', 'farm']].plot(kind='bar', ax=ax_down[0])
        sigmas[[pair[0], pair[1], 'buy_hold', 'farm']].plot(kind='bar', ax=ax_down[1])
        sharpes[[pair[0], pair[1], 'buy_hold', 'farm']].plot(kind='bar', ax=ax_down[2])
        dd[[pair[0], pair[1], 'buy_hold', 'farm']].min().plot(kind='bar', ax=ax_down[3])

        ax_down[0].set_title('CAGR', fontsize=12)
        ax_down[1].set_title('Annualized Volatility', fontsize=12)
        ax_down[2].set_title('Sharpe Ratio', fontsize=12)
        ax_down[3].set_title('Max DrawDowns', fontsize=12)
        [ax_down[i].grid(alpha=0.4) for i in range(cols)]

        st.pyplot(fig)
        return farm, cagrs, sigmas, sharpes, dd
    else:
        st.error("Les données téléchargées ne contiennent pas 2 colonnes nécessaires.")
        return None

st.title("Simulation de Farming LP vs Performance")

# Liste tokens élargie
tokens_available = [
    "bitcoin", "ethereum", "weth", "usdc", "usdt", "tether",
    "cbbtc", "dogecoin", "litecoin", "binancecoin", "matic-network"
]

pair = st.multiselect("Choisir la paire de tokens (exactement 2):", tokens_available, default=["weth", "usdc"])
apr = st.number_input("APR en %", min_value=0.0, max_value=100.0, value=25.0, step=0.1)
start_date = st.date_input("Date de début", value=datetime.date(2021, 1, 1))
end_date = st.date_input("Date de fin", value=datetime.date.today())

if st.button("Simuler"):
    if len(pair) != 2:
        st.error("Veuillez sélectionner exactement 2 tokens pour la paire.")
    elif start_date >= end_date:
        st.error("La date de début doit être antérieure à la date de fin.")
    else:
        farmSimulate(pair, apr, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
