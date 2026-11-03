"""Point d'entree principal de l'API FastAPI - Starter Kit Apprenants.

Ce fichier est le coeur de votre mission pour le backend de la plateforme IA-TOS.
Vous devez completer les routes ci-dessous en vous appuyant sur :
- Le package metier : iatos_core (agents, scoring, sentiment, logger, config)
- Le contrat d'interface : backend.schemas (Pydantic v2)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from iatos_core import __version__
from iatos_core.logger import logger
from iatos_core.ml.scoring import CreditScoringPredictor
from iatos_core.ml.sentiment import SentimentAnalyzer
from iatos_core.agent.graph import run_agent_message

from backend.schemas import (
    ChatRequest,
    ChatResponse,
    CreditPredictRequest,
    CreditPredictResponse,
    HealthResponse,
    SentimentPredictRequest,
    SentimentPredictResponse,
)

# Services partages (Singletons en memoire)
scoring_predictor: CreditScoringPredictor = None
sentiment_analyzer: SentimentAnalyzer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cycle de vie de l'application FastAPI : chargement unique des modeles."""
    global scoring_predictor, sentiment_analyzer
    logger.info("Demarrage des services FastAPI IA-TOS...")

    scoring_predictor = CreditScoringPredictor()
    sentiment_analyzer = SentimentAnalyzer()
    logger.info("Modeles de scoring et de sentiment charges en memoire.")

    yield
    logger.info("Arret des services FastAPI IA-TOS.")


# Instanciation de l'application FastAPI
app = FastAPI(
    title="Plateforme IA-TOS - API Multi-Services",
    description="API exposant l'agent conversationnel LangGraph, le scoring de credit et l'analyse de sentiment.",
    version=__version__,
    lifespan=lifespan,
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["Supervision"])
def health_check():
    """Endpoint de surveillance (Healthcheck) pour Uptime Kuma ou Docker."""
    return HealthResponse(status="ok", version=__version__, service="iatos-api")


@app.post("/chat", response_model=ChatResponse, tags=["Agent Conversationnel"])
def chat_endpoint(payload: ChatRequest):
    """Endpoint conversationnel interrogeant l'agent LangGraph outille."""
    try:
        history_dicts = [{"role": msg.role, "content": msg.content} for msg in payload.history]
        resultat = run_agent_message(user_message=payload.message, history=history_dicts)
        return ChatResponse(**resultat)
    except Exception as exc:
        logger.error("Erreur sur /chat : {err}", err=exc)
        raise HTTPException(status_code=500, detail="Erreur interne de l'agent conversationnel.")


@app.post("/predict/credit", response_model=CreditPredictResponse, tags=["Scoring Tabulaire"])
def predict_credit(payload: CreditPredictRequest):
    """Endpoint de prediction du score de credit (baseline Scikit-Learn M0)."""
    global scoring_predictor
    try:
        if scoring_predictor is None:
            scoring_predictor = CreditScoringPredictor()
        resultat = scoring_predictor.predict(
            montant_demande=payload.montant_demande,
            duree_mois=payload.duree_mois,
            revenu_mensuel=payload.revenu_mensuel,
        )
        return CreditPredictResponse(**resultat)
    except Exception as exc:
        logger.error("Erreur sur /predict/credit : {err}", err=exc)
        raise HTTPException(status_code=500, detail="Erreur interne du service de scoring.")


@app.post("/predict/sentiment", response_model=SentimentPredictResponse, tags=["Traitement NLP"])
def predict_sentiment(payload: SentimentPredictRequest):
    """Endpoint d'analyse de polarite de sentiment (baseline NLTK VADER M0)."""
    global sentiment_analyzer
    try:
        if sentiment_analyzer is None:
            sentiment_analyzer = SentimentAnalyzer()
        resultat = sentiment_analyzer.analyze(payload.texte)
        return SentimentPredictResponse(**resultat)
    except Exception as exc:
        logger.error("Erreur sur /predict/sentiment : {err}", err=exc)
        raise HTTPException(status_code=500, detail="Erreur interne du service de sentiment.")
