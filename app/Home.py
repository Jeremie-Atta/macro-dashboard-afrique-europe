import streamlit as st

st.set_page_config(
    page_title="Dashboard macro — Afrique vs Europe",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Dashboard macroéconomique — Afrique vs Europe")
st.markdown(
"""
Ce dashboard s’appuie sur les données **World Bank Open Data** (2000–2024) nettoyées et structurées.

### Pages
- **Overview** : évolution + KPIs
- **Comparaison** : ranking par pays
- **Chocs** : mise en évidence des ruptures (2009 / 2020 / 2022)
- **Note PDF** : téléchargement de la note d’analyse

Utilise le menu à gauche pour naviguer.
"""
)

st.divider()

st.markdown(
    """
    <div style="text-align:center; color: #6b7280; font-size: 0.9em;">
        Réalisé par <strong>Atta Jérémie KOUAME</strong> · Data Analyst / Économiste<br>
        © 2026
    </div>
    """,
    unsafe_allow_html=True
)
