import streamlit as st

def iloss(price_ratio, numerical=False):
    """Calcul de la perte non permanente comparée au buy & hold."""
    il = 2 * (price_ratio**0.5 / (1 + price_ratio)) - 1
    return f"{il:.2%}" if not numerical else il

# Titre de l'application
st.title("Calcul de la Perte Non Permanente (Impermanent Loss)")

# Explication rapide
st.markdown("""
Entrez les variations de prix de deux actifs (A et B) pour calculer la perte non permanente 
liée à une stratégie de fourniture de liquidité.
""")

# Entrées utilisateur
var_A = st.number_input("Variation de l'Actif A (%)", value=10.0, step=1.0)
var_B = st.number_input("Variation de l'Actif B (%)", value=5.0, step=1.0)

# Calcul du price ratio
price_ratio = (var_A / 100 + 1) / (var_B / 100 + 1)

# Bouton de calcul
if st.button("Calculer la perte non permanente"):
    result = iloss(price_ratio)
    st.success(f"Perte non permanente estimée : {result}")
