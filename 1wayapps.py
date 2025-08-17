import streamlit as st
import requests
import pandas as pd
import datetime
from functools import lru_cache

# -----------------------------------------
# UTILITY FUNCTIONS
# -----------------------------------------

def toFloatPartial(df):
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
    return df

# -----------------------------------------
# FETCH FUNCTIONS FOR EACH PLATFORM
# -----------------------------------------

@lru_cache(maxsize=3)
def fetch_pancake_pairs():
    url = "https://api.pancakeswap.info/api/v2/pairs"
    r = requests.get(url).json()
    data = r.get('data', {})
    upd = r.get('updated_at', 0) / 1000
    upd_dt = datetime.datetime.fromtimestamp(upd)
    df = pd.DataFrame.from_dict(data, orient='index')
    df = toFloatPartial(df)
    df['platform'] = 'PancakeSwap'
    df['fetched_at'] = upd_dt
    return df

@lru_cache(maxsize=3)
def fetch_uniswap_pairs():
    url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
    query = """
    {
      pairs(first: 1000, orderBy: reserveUSD, orderDirection: desc) {
        id
        token0 { id symbol name }
        token1 { id symbol name }
        reserve0
        reserve1
        reserveUSD
      }
    }
    """
    r = requests.post(url, json={'query': query})
    if r.status_code != 200:
        return pd.DataFrame()
    result = r.json().get('data', {}).get('pairs', [])
    if not result:
        return pd.DataFrame()
    df = pd.json_normalize(result)
    df = toFloatPartial(df)
    df['platform'] = 'Uniswap'
    df['fetched_at'] = datetime.datetime.utcnow()
    return df

@lru_cache(maxsize=3)
def fetch_aerodrome_pairs(moralis_key: str):
    api = "https://deep-index.moralis.io/api/v2/dex/pairs"
    params = {'chain': '0x2105', 'dex': 'aerodrome', 'limit': 1000}
    headers = {'X-API-Key': moralis_key}
    r = requests.get(api, params=params, headers=headers)
    if r.status_code != 200:
        return pd.DataFrame()
    result = r.json().get('result', [])
    if not result:
        return pd.DataFrame()
    df = pd.DataFrame(result)
    df = toFloatPartial(df)
    df['platform'] = 'Aerodrome'
    df['fetched_at'] = datetime.datetime.utcnow()
    return df

# -----------------------------------------
# MAIN UNIFIED FETCH FUNCTION
# -----------------------------------------

def get_pairs(platform: str, moralis_key: str = None):
    if platform == 'pancake':
        return fetch_pancake_pairs()
    elif platform == 'uniswap':
        return fetch_uniswap_pairs()
    elif platform == 'aerodrome':
        if not moralis_key:
            raise ValueError("Clé Moralis requise pour Aerodrome.")
        return fetch_aerodrome_pairs(moralis_key)
    else:
        raise ValueError("Plateforme invalide.")

# -----------------------------------------
# STREAMLIT APP
# -----------------------------------------

st.set_page_config(page_title="DEX Top LP Pairs", layout="wide")
st.title("DEX : Top LP Pairs – PancakeSwap · Uniswap · Aerodrome")

platform = st.selectbox("Choisir la plateforme :", ["pancake", "uniswap", "aerodrome"])

moralis_key = None
if platform == 'aerodrome':
    moralis_key = st.text_input("Clé API Moralis (requis pour Aerodrome)", type="password")

if st.button("Charger les données"):
    try:
        df = get_pairs(platform, moralis_key)

        if df.empty:
            st.warning("⚠️ Aucune donnée reçue depuis la plateforme sélectionnée.")
        else:
            fetched = df['fetched_at'].iloc[0]
            st.success(f"Données de **{platform.capitalize()}** récupérées le {fetched.strftime('%Y‑%m‑%d %H:%M:%S')} UTC")

            # --- Filtrage symboles dynamiques ---
            if platform == 'uniswap':
                symbols = sorted(set(
                    df.get("token0.symbol", pd.Series([])).dropna().astype(str).tolist() +
                    df.get("token1.symbol", pd.Series([])).dropna().astype(str).tolist()
                ))
            elif platform == 'aerodrome':
                symbols = sorted(set(
                    df.get("token0_symbol", pd.Series([])).dropna().astype(str).tolist() +
                    df.get("token1_symbol", pd.Series([])).dropna().astype(str).tolist()
                ))
            else:
                symbols = sorted(set(
                    df.get("base_symbol", pd.Series([])).dropna().astype(str).tolist() +
                    df.get("quote_symbol", pd.Series([])).dropna().astype(str).tolist()
                ))

            token_filter = st.multiselect("Filtrer par symboles", symbols)
            if token_filter:
                df = df[df.apply(lambda row: any(sym in str(row).upper() for sym in token_filter), axis=1)]
                st.info(f"{len(df)} paires affichées après filtrage.")

            st.dataframe(df)

    except Exception as e:
        st.error(f"❌ Erreur : {e}")
else:
    st.info("Sélectionne une plateforme, puis clique sur *Charger les données*.")
