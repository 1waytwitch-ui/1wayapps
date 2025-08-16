import streamlit as st
from PIL import Image

st.set_page_config(page_title="Crypto Dashboard", layout="centered")

st.title("🚀 Crypto Dashboard")
st.markdown("Bienvenue ! Choisissez une application ci-dessous pour explorer vos données crypto.")

st.divider()

# Boutons avec icônes et liens vers d'autres apps (pages)
col1, col2 = st.columns(2)

with col1:
    if st.button("📈 Analyse DEFI wallet"):
        st.switch_page("https://defisplit.streamlit.app/")

    if st.button("📊 ETH TP"):
        st.switch_page("https://eth-tp-app.streamlit.app/")

    if st.button("🧮 Rebalances cost"):
        st.switch_page("pages/🧮 https://rebalancecost.streamlit.app/")

with col2:
    if st.button("📉 Alertes marché"):
        st.switch_page("pages/📉 App4.py")

    if st.button("💹 Portefeuille"):
        st.switch_page("pages/💹 App5.py")

st.divider()
st.markdown("👨‍💻 _Développé par 1way – mise à jour temps réel des données crypto._")
