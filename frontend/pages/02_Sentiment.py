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

# ==============================================================================
# TODO (Apprenants) : Implémenter la saisie textuelle et l'appel API
#
# Étapes suggérées :
# 1. Proposer une zone de saisie texte avec st.text_area().
# 2. Optionnel : Proposer des boutons de texte d'exemples (positif, négatif, neutre).
# 3. Ajouter un bouton d'action avec st.button("Analyser la polarité").
# 4. Lors du clic :
#    a. Émettre un POST vers f"{FASTAPI_URL}/predict/sentiment" avec le payload JSON :
#       {"texte": texte_saisi}
#    b. Récupérer la réponse JSON (SentimentPredictResponse) contenant :
#       - label (str : 'Positif', 'Neutre', 'Negatif')
#       - compound (float entre -1.0 et 1.0)
#       - details (dict avec 'pos', 'neu', 'neg')
#       - method (str)
#    c. Restituer le résultat avec des composants visuels adaptés (st.metric, st.progress, etc.).
# ==============================================================================

st.info("A vous de jouer ! Implementez l'analyseur de sentiment et l'affichage des metriques NLP.")
Exemples = {
    "Positif": "im so happy",
    "Neutre": "its ok",
    "Négatif": "im so sad"
}

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Exemple_Positif") :
        st.session_state["texte"]= Exemples["Positif"]

with col2:
    if st.button("Exemple_neutre") :
        st.session_state["texte"]= Exemples["Neutre"]

with col3:
    if st.button("Exemple_Négatif") :
        st.session_state["texte"]= Exemples["Négatif"]

zone_saisie = st.text_area("Texte à analyser", key="texte")
bouton_action = st.button("Analyser la polarité")
c1, c2, c3, c4 = st.columns(4)

if bouton_action :
    payload = {"texte": zone_saisie}
    response = requests.post(f"{FASTAPI_URL}/predict/sentiment", json = payload, timeout = 5)
    response.raise_for_status()
    data = response.json()
    c1.metric("compound", data["compound"])
    c2.metric("Positif", data["scores"]["pos"])
    c3.metric("Neutre", data["scores"]["neu"])
    c4.metric("Négatif", data["scores"]["neg"])
    st.progress((data["compound"] + 1)/2)