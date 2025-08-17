import streamlit as st
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Appliquer un thème sombre et flashy avec CSS
st.markdown(
    """
    <style>
    /* Fond sombre */
    .main {
        background-color: #0e0b16;
        color: #f0f0f0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Titres flashy */
    h1 {
        color: #00ffea;
        text-shadow: 0 0 10px #00ffea;
    }

    label, .css-1aumxhk {
        color: #39ff14;
    }

    /* Input & bouton */
    .stButton>button {
        background-color: #39ff14;
        color: #0e0b16;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00ffea;
        color: #0e0b16;
    }

    /* Multiselect tags color */
    .css-1n76uvr {
        background-color: #00ffea !important;
        color: #0e0b16 !important;
        font-weight: bold !important;
    }

    /* Date input */
    .css-1t34s6h, .css-1vencpc {
        background-color: #222020;
        color: #00ffea;
        border-radius: 5px;
    }

    /* Erreur */
    .stError {
        background-color: #ff073a !important;
        color: white !important;
        border-radius: 10px;
        padding: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

def geckoHistorical(coin_id):
    dates = pd.date_range(start="2021-01-01", end=datetime.date.today())
    prices = pd.Series(100 + np.cumsum(np.random.randn(len(dates))), index=dates).abs()
    df = pd.DataFrame({"price": prices})
    df.index.name = "date"
    return df

def farmSimulate(pair, apr, start, end):
    prices = pd.DataFrame()
    for coin in pair:
        try:
            st.write(f"Downloading {coin} prices...")
            df = geckoHistorical(coin)
            prices[coin] = df['price']
        except Exception as e:
            st.error(f"Error fetching prices for {coin}: {e}")
            return None

    prices = prices.dropna()
    farm = prices.loc[(prices.index >= start) & (prices.index <= end)]

    if farm.empty:
        st.error("Aucune donnée disponible pour la plage de dates sélectionnée.")
        return None

    farm = farm.divide(farm.iloc[0])
    farm['ratio'] = farm.iloc[:,1].divide(farm.iloc[:,0])
    farm['iloss'] = 2 * (farm['ratio']**0.5 / (1 + farm['ratio'])) - 1
    farm['rewards'] = pd.Series(apr/100/365, index=farm.index).cumsum()
    farm['buy_hold'] = (farm.iloc[:,0] + farm.iloc[:,1])/2 
    farm['farm'] =  farm.buy_hold * (1 + farm.iloss) * (1 + farm.rewards) 

    cagrs = farm.iloc[-1]**(1/(len(farm)/365))-1
    sigmas = farm.pct_change().std() * np.sqrt(365)
    sharpes = cagrs.divide(sigmas).round(2)
    dd = farm/farm.cummax() - 1

    # Couleurs flashy néon pour les plots
    neon_colors = ['#00ffea', '#39ff14', '#ff073a', '#ff61f6']

    fig = plt.figure(figsize=(15,8))
    gs = GridSpec(nrows=2,ncols=4, figure=fig, height_ratios=[2,1], hspace=0.45, wspace=0.35, top=.9)
    ax_upleft = fig.add_subplot(gs[0,0:2])
    ax_upright = fig.add_subplot(gs[0,2:])
    ax_down = [fig.add_subplot(gs[1,i]) for i in range(4)]

    ax_upleft.plot(farm.iloss.abs(), label='Impermanent Loss', color=neon_colors[0], linewidth=2)
    ax_upleft.plot(farm.rewards, label='Farming Rewards', color=neon_colors[1], linewidth=2)
    ax_upleft.legend()
    ax_upleft.grid(color='#222222')
    ax_upleft.set_facecolor('#0e0b16')
    ax_upleft.set_title('Impermanent Loss vs Farming Rewards', color='#00ffea')
    ax_upleft.tick_params(axis='x', rotation=45, colors='#00ffea')
    ax_upleft.tick_params(axis='y', colors='#00ffea')

    ax_upright.plot(farm.iloc[:,0], color=neon_colors[0], linewidth=2)
    ax_upright.plot(farm.iloc[:,1], color=neon_colors[1], linewidth=2)
    ax_upright.plot(farm.buy_hold, color=neon_colors[2], linewidth=2)
    ax_upright.plot(farm.farm, color=neon_colors[3], linewidth=2)
    ax_upright.grid(color='#222222')
    ax_upright.legend([pair[0], pair[1], 'Buy & Hold', 'Farming Strategy'], facecolor='#0e0b16', edgecolor='none')
    ax_upright.set_title(f'{pair[0]} vs {pair[1]} vs Buy & Hold vs Farming Strategy Payoff', color='#00ffea')
    ax_upright.tick_params(axis='x', rotation=45, colors='#00ffea')
    ax_upright.tick_params(axis='y', colors='#00ffea')
    ax_upright.set_facecolor('#0e0b16')

    # Bar plots flashy
    bar_colors = ['#00ffea', '#39ff14', '#ff073a', '#ff61f6']
    cagrs[[pair[0], pair[1], 'buy_hold', 'farm']].plot(kind='bar', ax=ax_down[0], color=bar_colors)
    sigmas[[pair[0], pair[1], 'buy_hold', 'farm']].plot(kind='bar', ax=ax_down[1], color=bar_colors)
    sharpes[[pair[0], pair[1], 'buy_hold', 'farm']].plot(kind='bar', ax=ax_down[2], color=bar_colors)
    dd[[pair[0], pair[1], 'buy_hold', 'farm']].min().plot(kind='bar', ax=ax_down[3], color=bar_colors)

    titles = ['CAGR', 'Annualized Volatility', 'Sharpe Ratio', 'Max DrawDowns']
    for i in range(4):
        ax_down[i].set_title(titles[i], fontsize=12, color='#00ffea')
        ax_down[i].grid(alpha=0.4, color='#222222')
        ax_down[i].set_facecolor('#0e0b16')
        ax_down[i].tick_params(axis='x', colors='#00ffea')
        ax_down[i].tick_params(axis='y', colors='#00ffea')

    st.pyplot(fig)

def main():
    st.title("Simulation de Farming LP vs Performance")

    tokens = ['weth', 'eth', 'usdc', 'cbbtc', 'usdt', 'bitcoin', 'tether']
    pair = st.multiselect("Choisir la paire de tokens (exactement 2):", tokens)

    if len(pair) != 2:
        st.warning("Veuillez sélectionner exactement 2 tokens.")
        return

    df_prices = geckoHistorical(pair[0])
    min_date = df_prices.index.min().date()
    max_date = df_prices.index.max().date()

    start_date = st.date_input("Date de début", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("Date de fin", value=max_date, min_value=min_date, max_value=max_date)

    if start_date > end_date:
        st.error("La date de début doit être antérieure ou égale à la date de fin.")
        return

    apr = st.number_input("APR en %", min_value=0.0, value=25.0, format="%.2f")

    if st.button("Simuler"):
        farmSimulate(pair, apr, pd.Timestamp(start_date), pd.Timestamp(end_date))

if __name__ == "__main__":
    main()
