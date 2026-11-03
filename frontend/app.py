"""Application Streamlit multi-pages - Page d'accueil & Page 0 (Chatbot LangGraph).

Starter Kit Apprenants - Brief 1 IA-TOS.
"""

import os
import requests
import streamlit as st

# URL du backend FastAPI (injectable via variable d'environnement)
FASTAPI_URL = os.getenv("FASTAPI_BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Plateforme IA-TOS | Brief 1",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar globale avec statut de l'API
with st.sidebar:
    st.title("Plateforme IA-TOS")
    st.caption("Module 0 : Socle Applicatif & Microservices")
    st.divider()

    # Verification de l'etat de l'API FastAPI
    try:
        resp = requests.get(f"{FASTAPI_URL}/health", timeout=2)
        if resp.status_code == 200:
            st.success("API Backend : En ligne")
        else:
            st.warning(f"API Backend : Statut {resp.status_code}")
    except Exception:
        st.error("API Backend : Hors ligne (Vérifiez le port 8000)")

    st.markdown("""
    **Pages disponibles :**
    - **Page 0** : Chatbot Agentique (LangGraph)
    - **Page 1** : Scoring Credit (Regression Lineaire)
    - **Page 2** : Analyse de Sentiment (NLTK)
    """)
    st.divider()
    st.caption("Projet OPCO Atlas - Simplon & Atos 2026")

# En-tete principal
st.title("Page 0 : Assistant Conversationnel Agentique")
st.markdown("""
Bienvenue sur la plateforme unifiee **IA-TOS**. Cet agent conversationnel est orchestre avec **LangGraph** 
et connecte au LLM local **Qwen 2.5** via **Ollama**. Il possede un outil deterministe de calcul arithmetique (`calculer`).
""")

# Historique de la conversation conserve entre les reruns Streamlit
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("tool_results"):
            with st.expander("Trace de l'outil de calcul"):
                for trace in msg["tool_results"]:
                    st.code(trace)

user_prompt = st.chat_input("Posez une question ou demandez un calcul (ex : combien font 12 + 8 ?)")

if user_prompt:
    # L'historique envoye au backend exclut le message courant
    history_payload = [
        {"role": m["role"], "content": m["content"]} for m in st.session_state["messages"]
    ]
    st.session_state["messages"].append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("L'agent reflechit..."):
                resp = requests.post(
                    f"{FASTAPI_URL}/chat",
                    json={"message": user_prompt, "history": history_payload},
                    timeout=120,
                )
            resp.raise_for_status()
            data = resp.json()
            st.write(data["response"])
            tool_results = data["tool_results"] if data["tool_called"] else []
            if tool_results:
                with st.expander("Trace de l'outil de calcul"):
                    for trace in tool_results:
                        st.code(trace)
            st.session_state["messages"].append(
                {"role": "assistant", "content": data["response"], "tool_results": tool_results}
            )
        except requests.RequestException as exc:
            st.error(f"Impossible de joindre le backend : {exc}")
