import streamlit as st
from PIL import Image

st.set_page_config(page_title="Crypto Dashboard", layout="centered")

st.title("🚀 Crypto Dashboard")
st.markdown("Bienvenue ! Choisissez une application ci-dessous pour explorer vos données crypto.")

st.divider()

# Boutons avec icônes et liens vers d'autres apps (pages)
col1, col2 = st.columns(2)

with col1:
    if st.button("📈 Analyse BTC"):
        st.switch_page("pages/📈 App1.py")

    if st.button("📊 Analyse ETH"):
        st.switch_page("pages/📊 App2.py")

    if st.button("🧮 Comparateur"):
        st.switch_page("pages/🧮 App3.py")

with col2:
    if st.button("📉 Alertes marché"):
        st.switch_page("pages/📉 App4.py")

    if st.button("💹 Portefeuille"):
        st.switch_page("pages/💹 App5.py")

st.divider()
st.markdown("👨‍💻 _Développé avec Streamlit – mise à jour temps réel des données crypto._")
