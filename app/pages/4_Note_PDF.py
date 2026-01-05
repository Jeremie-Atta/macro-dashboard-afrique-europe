import streamlit as st
from pathlib import Path

PDF_PATH = Path("reports/note_analyse_macro.pdf")
MD_PATH = Path("reports/note_analyse_macro.md")

st.title("Note d’analyse")

st.write("Télécharge la note d’analyse macroéconomique (PDF) ou consulte la version Markdown.")

col1, col2 = st.columns(2)

with col1:
    if PDF_PATH.exists():
        st.download_button(
            "⬇️ Télécharger la note (PDF)",
            data=PDF_PATH.read_bytes(),
            file_name=PDF_PATH.name,
            mime="application/pdf"
        )
    else:
        st.warning("Le PDF n’a pas été trouvé dans reports/")

with col2:
    if MD_PATH.exists():
        st.download_button(
            "⬇️ Télécharger la note (Markdown)",
            data=MD_PATH.read_bytes(),
            file_name=MD_PATH.name,
            mime="text/markdown"
        )
    else:
        st.warning("Le Markdown n’a pas été trouvé dans reports/")

st.divider()

if MD_PATH.exists():
    st.subheader("Aperçu (Markdown)")
    st.markdown(MD_PATH.read_text(encoding="utf-8"))
