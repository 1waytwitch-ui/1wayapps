import streamlit as st
from pycoingecko import CoinGeckoAPI
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date

cg = CoinGeckoAPI()

def get_price_history(coin_id, start_date):
    start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    end_timestamp = int(datetime.now().timestamp())
    data = cg.get_coin_market_chart_range_by_id(
        id=coin_id, vs_currency='usd',
        from_timestamp=start_timestamp, to_timestamp=end_timestamp)
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date
    df = df.groupby('date').last()
    df = df[['price']]
    return df

def calculate_cagr(prices):
    n = len(prices) / 365
    cagr = (prices[-1] / prices[0])**(1 / n) - 1
    return cagr

def calculate_annual_volatility(returns):
    return returns.std() * np.sqrt(365)

def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    excess_returns = returns - risk_free_rate / 365
    return np.sqrt(365) * excess_returns.mean() / excess_returns.std()

def calculate_max_drawdown(prices):
    roll_max = prices.cummax()
    drawdowns = (prices - roll_max) / roll_max
    return drawdowns.min()

default_start_date = date.today().replace(month=1, day=1).strftime("%Y-%m-%d")

st.title("Stratégie de Farming Crypto 🚀")

start_date = st.date_input("Date de début", value=datetime.strptime(default_start_date, "%Y-%m-%d"))

cryptos = {
    'weth': 'Wrapped Ether',
    'usd-coin': 'USDC (Stablecoin)',
    'bitcoin': 'Bitcoin',
    'dai': 'DAI (Stablecoin)',
}

selected_coins = st.multiselect(
    "Choisir les cryptos",
    options=list(cryptos.keys()),
    format_func=lambda x: cryptos[x],
    default=['weth', 'usd-coin']
)

if st.button("Télécharger les prix historiques"):
    dfs = {}
    for coin in selected_coins:
        df = get_price_history(coin, start_date.strftime("%Y-%m-%d"))
        dfs[coin] = df

    prices_df = pd.concat(dfs.values(), axis=1)
    prices_df.columns = [cryptos[c] for c in dfs.keys()]
    prices_df.dropna(inplace=True)

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

    # Calcul des stratégies en partant des prix (normalisés)
    if 'Wrapped Ether' in prices_df.columns:
        buy_hold = prices_df['Wrapped Ether'] / prices_df['Wrapped Ether'].iloc[0]
    else:
        buy_hold = prices_df.iloc[:, 0] / prices_df.iloc[:, 0].iloc[0]

    farming_rewards = (1 + 0.01 / 365) ** np.arange(len(buy_hold))
    farming_strategy = buy_hold * farming_rewards

    if 'USDC (Stablecoin)' in prices_df.columns:
        usdc_hold = prices_df['USDC (Stablecoin)'] / prices_df['USDC (Stablecoin)'].iloc[0]
    else:
        usdc_hold = np.ones(len(buy_hold))

    strategies_df = pd.DataFrame({
        'Buy & Hold': buy_hold,
        'Farming Strategy': farming_strategy,
        'USDC (Stablecoin)': usdc_hold,
    }, index=buy_hold.index)

    fig2, ax2 = plt.subplots(figsize=(12,6))
    for col in strategies_df.columns:
        ax2.plot(strategies_df.index, strategies_df[col], label=col)
    ax2.set_title("Performance des stratégies")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Valeur relative")
    ax2.legend()
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    st.pyplot(fig2)

    # Calcul métriques
    metrics = {}
    for strat in strategies_df.columns:
        prices = strategies_df[strat]
        r = prices.pct_change().dropna()
        metrics[strat] = {
            "CAGR": calculate_cagr(prices.values),
            "Volatilité": calculate_annual_volatility(r),
            "Sharpe Ratio": calculate_sharpe_ratio(r),
            "Max Drawdown": calculate_max_drawdown(prices),
        }
    metrics_df = pd.DataFrame(metrics).T

    st.write("## Métriques des stratégies")
    st.dataframe(metrics_df.style.format("{:.2%}"))

    st.markdown("---")
    st.markdown("<p style='text-align:center;'>Développé par 1way</p>", unsafe_allow_html=True)
