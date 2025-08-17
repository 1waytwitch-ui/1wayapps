import streamlit as st
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Exemple d'implémentation fictive de geckoHistorical à remplacer par ta vraie fonction
def geckoHistorical(coin_id):
    # Simule un DataFrame de prix historiques sur 2 ans pour l'exemple
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

    # Filtrer selon les dates sélectionnées
    prices = prices.dropna()
    farm = prices.loc[(prices.index >= start) & (prices.index <= end)]

    if farm.empty:
        st.error("Aucune donnée disponible pour la plage de dates sélectionnée.")
        return None

    # Normaliser par la première valeur
    farm = farm.divide(farm.iloc[0])

    # Calcul ratio pour impermanent loss
    farm['ratio'] = farm.iloc[:,1].divide(farm.iloc[:,0])

    # Impermanent Loss
    farm['iloss'] = 2 * (farm['ratio']**0.5 / (1 + farm['ratio'])) - 1
    # Récompenses cumulées
    farm['rewards'] = pd.Series(apr/100/365, index=farm.index).cumsum()
    # Buy & hold moyenne
    farm['buy_hold'] = (farm.iloc[:,0] + farm.iloc[:,1])/2 
    # Farm final
    farm['farm'] =  farm.buy_hold * (1 + farm.iloss) * (1 + farm.rewards) 

    # Metrics
    cagrs = farm.iloc[-1]**(1/(len(farm)/365))-1
    sigmas = farm.pct_change().std() * np.sqrt(365)
    sharpes = cagrs.divide(sigmas).round(2)
    dd = farm/farm.cummax() - 1

    # Plot
    fig = plt.figure(figsize=(15,8))
    gs = GridSpec(nrows=2,ncols=4, figure=fig, height_ratios=[2,1], hspace=0.45, wspace=0.35, top=.9)
    ax_upleft = fig.add_subplot(gs[0,0:2])
    ax_upright = fig.add_subplot(gs[0,2:])
    ax_down = [fig.add_subplot(gs[1,i]) for i in range(4)]
    
    ax_upleft.plot(farm.iloss.abs(), label='Impermanent Loss')
    ax_upleft.plot(farm.rewards, label='Farming Rewards')
    ax_upleft.legend()
    ax_upleft.grid()
    ax_upleft.set_title('Impermanent Loss vs Farming Rewards')
    ax_upleft.tick_params(axis='x', rotation=45)
    
    ax_upright.plot(farm.iloc[:,:2])
    ax_upright.plot(farm.buy_hold)
    ax_upright.plot(farm.farm)
    ax_upright.grid()
    ax_upright.legend([pair[0],pair[1],'Buy & Hold','Farming Strategy'])
    ax_upright.set_title(f'{pair[0]} vs {pair[1]} vs Buy & Hold vs Farming Strategy Payoff')
    ax_upright.tick_params(axis='x', rotation=45)
    
    cagrs[[pair[0],pair[1],'buy_hold','farm']].plot(kind='bar', ax=ax_down[0])
    sigmas[[pair[0],pair[1],'buy_hold','farm']].plot(kind='bar', ax=ax_down[1])
    sharpes[[pair[0],pair[1],'buy_hold','farm']].plot(kind='bar', ax=ax_down[2])
    dd[[pair[0],pair[1],'buy_hold','farm']].min().plot(kind='bar', ax=ax_down[3])

    ax_down[0].set_title('CAGR', fontsize=12)
    ax_down[1].set_title('Annualized Volatility', fontsize=12)
    ax_down[2].set_title('Sharpe Ratio', fontsize=12)
    ax_down[3].set_title('Max DrawDowns', fontsize=12)
    for ax in ax_down:
        ax.grid(alpha=0.4)

    st.pyplot(fig)

def main():
    st.title("Simulation de Farming LP vs Performance")

    # Liste des tokens disponibles (ajoute/enlève selon ton besoin)
    tokens = ['weth', 'eth', 'usdc', 'cbbtc', 'usdt', 'bitcoin', 'tether']

    pair = st.multiselect("Choisir la paire de tokens (exactement 2):", tokens)

    if len(pair) != 2:
        st.warning("Veuillez sélectionner exactement 2 tokens.")
        return

    # Récupérer les dates disponibles du premier token pour limiter les dates
    df_prices = geckoHistorical(pair[0])
    min_date = df_prices.index.min().date()
    max_date = df_prices.index.max().date()

    # Date inputs avec limites
    start_date = st.date_input("Date de début", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("Date de fin", value=max_date, min_value=min_date, max_value=max_date)

    # Vérifier que start_date <= end_date
    if start_date > end_date:
        st.error("La date de début doit être antérieure ou égale à la date de fin.")
        return

    apr = st.number_input("APR en %", min_value=0.0, value=25.0, format="%.2f")

    if st.button("Simuler"):
        farmSimulate(pair, apr, pd.Timestamp(start_date), pd.Timestamp(end_date))

if __name__ == "__main__":
    main()
