"""
API Router — Lead Scoring (ML Module).
Provides endpoints for ML-based lead conversion prediction.
"""
import os
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import numpy as np

from app.database import get_db
from app.api.deps import get_current_user, require_internal
from app.domain.auth.models import User

logger = logging.getLogger("crm.ml")
router = APIRouter(prefix="/ml", tags=["Machine Learning"])

# ── ML Model loading (lazy singleton) ──
_model = None
_scaler = None
_feature_names = None

ML_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "ml", "outputs", "models")
# Fallback: handle case-sensitive Linux (folder may be "ML" instead of "ml")
if not os.path.isdir(ML_DIR):
    ML_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "ML", "outputs", "models")


def _load_model():
    """Charge le modèle ML une seule fois (lazy loading)."""
    global _model, _scaler, _feature_names
    if _model is not None:
        return
    try:
        import joblib
        _model = joblib.load(os.path.join(ML_DIR, "best_model.pkl"))
        _scaler = joblib.load(os.path.join(ML_DIR, "scaler.pkl"))
        _feature_names = joblib.load(os.path.join(ML_DIR, "feature_names.pkl"))
        logger.info(f"✅ ML model loaded: {type(_model).__name__}, {len(_feature_names)} features")
    except Exception as e:
        logger.warning(f"⚠️ ML model not available: {e}")
        _model = None


# ── Schemas ──
class LeadScoreRequest(BaseModel):
    source: str = "website"
    sector: str = "IT / Digital"
    estimated_value: float = 25000
    days_in_pipeline: int = 30
    has_email: int = 1
    has_phone: int = 1
    activities_count: int = 3
    calls: int = 1
    emails_sent: int = 1
    meetings: int = 1


class LeadScoreResponse(BaseModel):
    score: float
    label: str
    probability: float
    top_factors: list


class ModelInfoResponse(BaseModel):
    model_name: str
    features_count: int
    feature_names: list
    status: str
    metrics: dict


# ── Feature Engineering (same as training) ──
def _build_features(data: LeadScoreRequest) -> dict:
    """Reproduit exactement le feature engineering du notebook."""
    d = data.dict()
    # Engineered features
    d["contact_score"] = d["has_email"] + d["has_phone"]
    d["activity_intensity"] = round(d["activities_count"] / max(d["days_in_pipeline"], 1), 4)
    d["meeting_ratio"] = round(d["meetings"] / max(d["activities_count"], 1), 4)
    d["is_high_value"] = int(d["estimated_value"] > 40000)
    d["is_fresh"] = int(d["days_in_pipeline"] <= 30)
    d["log_value"] = round(float(np.log1p(d["estimated_value"])), 4)
    d["has_activities"] = int(d["activities_count"] > 0)

    # One-hot encoding for source
    all_sources = ["email", "other", "phone", "referral", "social_media", "trade_show", "website"]
    for s in all_sources:
        d[f"source_{s}"] = int(d["source"] == s)

    # One-hot encoding for sector
    all_sectors = ["Commerce", "Finance / Banque", "Immobilier", "Industrie", "IT / Digital", "Santé", "Tourisme", "Éducation"]
    for s in all_sectors:
        d[f"sector_{s}"] = int(d["sector"] == s)

    return d


def _get_top_factors(data: LeadScoreRequest) -> list:
    """Retourne les facteurs clés qui influencent le score."""
    factors = []
    if data.source == "referral":
        factors.append({"factor": "Source Referral", "impact": "positive", "detail": "Recommandation client — fort signal"})
    elif data.source == "trade_show":
        factors.append({"factor": "Salon professionnel", "impact": "positive", "detail": "Contact direct en événement"})
    elif data.source == "social_media":
        factors.append({"factor": "Réseaux sociaux", "impact": "negative", "detail": "Lead généralement froid"})

    if data.activities_count >= 5:
        factors.append({"factor": "Engagement élevé", "impact": "positive", "detail": f"{data.activities_count} interactions enregistrées"})
    elif data.activities_count == 0:
        factors.append({"factor": "Aucune activité", "impact": "negative", "detail": "Pas d'interaction commerciale"})

    if data.has_email and data.has_phone:
        factors.append({"factor": "Contact complet", "impact": "positive", "detail": "Email + téléphone disponibles"})

    if data.days_in_pipeline > 90:
        factors.append({"factor": "Stagnation", "impact": "negative", "detail": f"{data.days_in_pipeline} jours dans le pipeline"})
    elif data.days_in_pipeline <= 20:
        factors.append({"factor": "Lead frais", "impact": "positive", "detail": f"Seulement {data.days_in_pipeline} jours"})

    if data.estimated_value > 50000:
        factors.append({"factor": "Haute valeur", "impact": "positive", "detail": f"{data.estimated_value:,.0f} DT estimé"})

    return factors[:5]


# ── Endpoints ──
@router.post("/score", response_model=LeadScoreResponse)
def predict_lead_score(
    payload: LeadScoreRequest,
    current_user: User = Depends(require_internal),
):
    """Prédit le score de conversion d'un lead."""
    _load_model()
    if _model is None:
        raise HTTPException(status_code=503, detail="ML model not loaded")

    features = _build_features(payload)
    # Build feature vector in correct order
    vector = [features.get(f, 0) for f in _feature_names]
    X = np.array([vector])
    X_scaled = _scaler.transform(X)

    proba = float(_model.predict_proba(X_scaled)[0][1])
    label = "Chaud 🔥" if proba >= 0.7 else "Tiède 🟡" if proba >= 0.4 else "Froid ❄️"

    return LeadScoreResponse(
        score=round(proba * 100, 1),
        label=label,
        probability=round(proba, 4),
        top_factors=_get_top_factors(payload),
    )


@router.get("/info", response_model=ModelInfoResponse)
def get_model_info(
    current_user: User = Depends(require_internal),
):
    """Retourne les informations sur le modèle ML chargé."""
    _load_model()
    if _model is None:
        return ModelInfoResponse(
            model_name="Non chargé", features_count=0,
            feature_names=[], status="offline",
            metrics={}
        )
    return ModelInfoResponse(
        model_name=type(_model).__name__,
        features_count=len(_feature_names),
        feature_names=_feature_names,
        status="online",
        metrics={"F1": 0.909, "AUC": 0.963, "Accuracy": 0.890}
    )


@router.post("/score-lead/{lead_id}", response_model=LeadScoreResponse)
def score_existing_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_internal),
):
    """Score un lead existant depuis la base de données."""
    _load_model()
    if _model is None:
        raise HTTPException(status_code=503, detail="ML model not loaded")

    from app.domain.leads.models import Lead
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    payload = LeadScoreRequest(
        source=lead.source.value if lead.source else "website",
        sector="IT / Digital",
        estimated_value=float(lead.estimated_value or 25000),
        days_in_pipeline=30,
        has_email=1 if lead.email else 0,
        has_phone=1 if lead.phone else 0,
        activities_count=0,
        calls=0, emails_sent=0, meetings=0,
    )

    features = _build_features(payload)
    vector = [features.get(f, 0) for f in _feature_names]
    X = np.array([vector])
    X_scaled = _scaler.transform(X)
    proba = float(_model.predict_proba(X_scaled)[0][1])
    label = "Chaud 🔥" if proba >= 0.7 else "Tiède 🟡" if proba >= 0.4 else "Froid ❄️"

    return LeadScoreResponse(
        score=round(proba * 100, 1),
        label=label,
        probability=round(proba, 4),
        top_factors=_get_top_factors(payload),
    )
