from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from .services.dfi_client import DFIClient
from .services.medlm_client import MedLMClient
from .services.featuregen_client import FeatureGenClient
from .services.gnn_ddi_client import GNNDdiClient
from .services.recommender_client import RecommenderClient
from .services.kg_client import KGClient
from .services.ner_client import NERClient
from .services.standardizer_client import StandardizerClient
from .models.audit import log_audit
import yaml
import os
import asyncio

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def load_config():
    with open(os.path.join(os.path.dirname(__file__), 'config/risk_weights.yaml')) as f:
        weights = yaml.safe_load(f)
    with open(os.path.join(os.path.dirname(__file__), 'config/risk_thresholds.yaml')) as f:
        thresholds = yaml.safe_load(f)
    return weights, thresholds

@router.post("/predict/risk")
async def predict_risk(request: dict, token: str = Depends(oauth2_scheme)):
    # --- 1. Aggregate Inputs ---
    patient_id = request.get('patient_id')
    prescription = request.get('prescription', [])
    # Init clients
    kg = KGClient()
    featuregen = FeatureGenClient()
    gnn_ddi = GNNDdiClient()
    dfi = DFIClient()
    medlm = MedLMClient()
    recommender = RecommenderClient()
    standardizer = StandardizerClient()

    # a. Patient history (allergies, conditions)
    patient_history = await kg.get_patient_history(patient_id)
    allergies = set(patient_history.get('allergies', []))
    conditions = set(patient_history.get('conditions', []))

    # b. KG-feature-vector for each drug
    feature_tasks = [featuregen.get_features(patient_id, d['drug_id']) for d in prescription]
    features = await asyncio.gather(*feature_tasks)

    # c. DDI for each pair
    ddi_tasks = []
    ddi_pairs = []
    for i in range(len(prescription)):
        for j in range(i+1, len(prescription)):
            ddi_tasks.append(gnn_ddi.get_ddi(prescription[i]['drug_id'], prescription[j]['drug_id']))
            ddi_pairs.append((prescription[i], prescription[j]))
    ddi_results = await asyncio.gather(*ddi_tasks) if ddi_tasks else []

    # d. ADR flags
    adr_tasks = [kg.get_adr_flags(patient_id, d['drug_id']) for d in prescription]
    adr_results = await asyncio.gather(*adr_tasks)

    # e. DFI for each drug
    dfi_tasks = [dfi.get_dfi(d['drug_id']) for d in prescription]
    dfi_results = await asyncio.gather(*dfi_tasks)

    # f. Home-remedy suggestions
    remedy_tasks = [medlm.get_home_remedies(d['name']) for d in prescription]
    remedy_results = await asyncio.gather(*remedy_tasks)

    # --- 2. Risk Scoring Engine ---
    weights, thresholds = load_config()
    # Example: sum normalized DDI/ADR risk (stub logic)
    risk_score = 0.0
    contributors = []
    for i, (drug, feat, adr) in enumerate(zip(prescription, features, adr_results)):
        ddi_risk = 0.0
        for j, (pair, ddi) in enumerate(zip(ddi_pairs, ddi_results)):
            if drug['drug_id'] in [pair[0]['drug_id'], pair[1]['drug_id']]:
                ddi_risk += ddi.get('risk', 0)
        adr_risk = adr.get('risk', 0)
        score = weights.get('ddi_weight', 0.5) * ddi_risk + weights.get('adr_weight', 0.5) * adr_risk
        risk_score += score
        contributors.append({"drug_id": drug['drug_id'], "ddi": ddi_risk, "adr": adr_risk, "score": score})

    # Normalize risk_score
    risk_score = min(1.0, risk_score / max(1, len(prescription)))

    # --- 3. Risk Classification ---
    if any(a in allergies for a in [d['drug_id'] for d in prescription]):
        level = 'CRITICAL'
    elif risk_score >= thresholds.get('critical', 0.9):
        level = 'CRITICAL'
    elif risk_score >= thresholds.get('high', 0.7):
        level = 'HIGH'
    elif risk_score >= thresholds.get('moderate', 0.3):
        level = 'MODERATE'
    else:
        level = 'LOW'

    # --- 4. DFI Caution Module ---
    dfi_cautions = []
    dfi_flag = False
    for drug, dfi_list in zip(prescription, dfi_results):
        for dfi_item in dfi_list:
            dfi_cautions.append({
                "drug": drug['name'],
                "food_item": dfi_item.get('food_item'),
                "advice": dfi_item.get('advice'),
                "type": dfi_item.get('type'),
                "reason": dfi_item.get('reason')
            })
            dfi_flag = True

    # --- 5. Home-Remedy Advice ---
    home_remedies = []
    for drug, remedies in zip(prescription, remedy_results):
        for r in remedies[:3]:
            home_remedies.append({
                "drug": drug['name'],
                "remedy": r.get('remedy'),
                "description": r.get('description'),
                "caution": r.get('cautionary_note'),
                "confidence": r.get('confidence', 1.0)
            })

    # --- 6. Recommendations ---
    recommendations = []
    if level in ('HIGH', 'CRITICAL'):
        rec_tasks = [recommender.get_alternatives(d['drug_id'], patient_history) for d in prescription]
        rec_results = await asyncio.gather(*rec_tasks)
        for recs in rec_results:
            recommendations.extend(recs[:3])

    # --- 7. Explainability & Evidence ---
    evidence_paths = []
    for pair in ddi_pairs:
        paths = await kg.get_evidence_paths(pair[0]['drug_id'], pair[1]['drug_id'])
        evidence_paths.extend(paths[:3])

    # --- 8. Alert Trigger ---
    if level in ('HIGH', 'CRITICAL') or dfi_flag:
        # TODO: emit RISK_ALERT event (Kafka/Redis pub-sub)
        pass

    # --- Audit Log ---
    log_audit({
        "patient_id": patient_id,
        "prescription": prescription,
        "risk_score": risk_score,
        "level": level,
        "dfi_cautions": dfi_cautions,
        "home_remedies": home_remedies,
        "recommendations": recommendations,
        "evidence_paths": evidence_paths,
        "contributors": contributors
    })

    return {
        "risk_score": risk_score,
        "level": level,
        "ddi_summary": ddi_results,
        "dfi_cautions": dfi_cautions,
        "home_remedies": home_remedies,
        "recommendations": recommendations,
        "evidence_paths": evidence_paths,
        "contributors": contributors
    }

@router.get("/risk/{patient_id}")
async def get_risk_history(patient_id: str, token: str = Depends(oauth2_scheme)):
    # TODO: fetch historical risk records
    return {"msg": f"History for {patient_id} not yet implemented"}

@router.get("/risk/config")
async def get_config(token: str = Depends(oauth2_scheme)):
    # TODO: return config
    return {"msg": "Config not yet implemented"}

@router.put("/risk/config")
async def update_config(config: dict, token: str = Depends(oauth2_scheme)):
    # TODO: update config
    return {"msg": "Config update not yet implemented"}
