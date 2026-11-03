"""Page 2 : Analyseur de Sentiment (Baseline Lexicale NLTK VADER M0).

Starter Kit Apprenants - Brief 1 IA-TOS.
"""

import os
import requests
import streamlit as st

FASTAPI_URL = os.getenv("FASTAPI_BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Analyse de Sentiment | Brief 1",
    page_icon="💬",
    layout="wide",
)

st.title("Page 2 : Analyseur de Sentiment des Retours Clients")
st.markdown("""
Cette page interroge le microservice NLP d'analyse de polarite base sur la methode lexicale 
**NLTK VADER** (`SentimentIntensityAnalyzer`).
""")

st.info("""
**Note d'architecture pedagogique (M0)** : Cette approche par dictionnaire lexical constitue notre 
baseline de depart. Elle sera confrontee puis remplacee dans les modules suivants par des modeles 
de Transformers pre-entraines en francais (**CamemBERT / RoBERTa**) et du Fine-Tuning LoRA (PEFT).
""")

EXEMPLES = {
    "Positif": "Excellent service, the support team was fantastic and very helpful!",
    "Negatif": "Terrible experience, the product is awful and the delivery was a disaster.",
    "Neutre": "The package was delivered on Tuesday.",
}

# Les boutons d'exemple pre-remplissent la zone de texte via session_state
if "texte" not in st.session_state:
    st.session_state["texte"] = ""

col_a, col_b, col_c = st.columns(3)
for col, (nom, exemple) in zip((col_a, col_b, col_c), EXEMPLES.items()):
    if col.button(f"Exemple {nom}"):
        st.session_state["texte"] = exemple

texte = st.text_area("Texte a analyser (anglais, VADER)", key="texte", height=120)

if st.button("Analyser la polarite"):
    if not texte.strip():
        st.warning("Saisissez un texte a analyser.")
    else:
        try:
            resp = requests.post(f"{FASTAPI_URL}/predict/sentiment", json={"texte": texte}, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            st.subheader(f"Resultat : {data['label']}")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Compound", f"{data['compound']:.3f}")
            c2.metric("Positif", f"{data['scores']['pos']:.0%}")
            c3.metric("Neutre", f"{data['scores']['neu']:.0%}")
            c4.metric("Negatif", f"{data['scores']['neg']:.0%}")

            # Compound borne entre -1 et 1 : normalisation sur [0, 1] pour la barre
            st.progress((data["compound"] + 1) / 2)
            st.caption(f"Modele : {data['type_modele']}")
        except requests.RequestException as exc:
            st.error(f"Impossible de joindre le backend : {exc}")
