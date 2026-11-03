"""Page 1 : Formulaire de Scoring de Credit (Baseline Regression Lineaire M0).

Starter Kit Apprenants - Brief 1 IA-TOS.
"""

import os
import requests
import streamlit as st

FASTAPI_URL = os.getenv("FASTAPI_BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Scoring Credit | Brief 1",
    page_icon="💳",
    layout="wide",
)

st.title("Page 1 : Formulaire Predictif de Scoring de Credit")
st.markdown("""
Cette page interroge le microservice de scoring de credit base sur une **Regression Lineaire Scikit-Learn** 
entrainee sur les 3 variables financieres neutres du dossier (`montant_demande`, `duree_mois`, `revenu_mensuel`).
""")

st.info("""
**Note d'architecture pedagogique (M0)** : Ce modele est restreint a 3 variables neutres. 
Le dataset complet contient des variables demographiques et contextuelles qui serviront au **Module 2** 
pour realiser l'audit d'equite algorithmique (Disparate Impact), l'anonymisation RGPD et la mitigation des biais.
""")

with st.form("form_credit"):
    montant = st.number_input("Montant demande (EUR)", min_value=1000.0, max_value=500000.0, value=10000.0, step=500.0)
    duree = st.slider("Duree du pret (mois)", min_value=6, max_value=84, value=24)
    revenu = st.number_input("Revenu mensuel net (EUR)", min_value=500.0, max_value=100000.0, value=3000.0, step=100.0)
    submitted = st.form_submit_button("Calculer le score")

if submitted:
    try:
        resp = requests.post(
            f"{FASTAPI_URL}/predict/credit",
            json={"montant_demande": montant, "duree_mois": duree, "revenu_mensuel": revenu},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        col1, col2 = st.columns(2)
        col1.metric("Score de credit", f"{data['score']:.0f} / 850")
        col2.metric("Decision", data["decision"])

        # Score borne entre 300 et 850 : normalisation sur [0, 1] pour la barre
        st.progress((data["score"] - 300) / 550)

        if data["decision"] == "Favorable":
            st.success(f"{data['decision']} : {data['motif']}")
        elif data["decision"].startswith("Ajourne"):
            st.warning(f"{data['decision']} : {data['motif']}")
        else:
            st.error(f"{data['decision']} : {data['motif']}")

        st.caption(f"Modele : {data['type_modele']}")
        with st.expander("Features utilisees"):
            st.json(data["features_utilisees"])
    except requests.RequestException as exc:
        st.error(f"Impossible de joindre le backend : {exc}")
