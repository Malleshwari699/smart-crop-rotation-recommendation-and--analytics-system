# =============================================================================
# utils/prediction.py
# Prediction Logic Module for Smart Crop Recommendation System
# =============================================================================

import numpy as np

# ── Fertilizer recommendations ────────────────────────────────────────────────
FERTILIZER_MAP = {
    "rice":        {"name": "Urea + DAP",            "detail": "Apply Urea (120 kg/ha) split in 3 doses. Basal DAP (50 kg/ha) at transplanting."},
    "wheat":       {"name": "NPK 12-32-16 + Urea",   "detail": "Basal NPK 12-32-16 (100 kg/ha); top-dress Urea at tillering and jointing."},
    "maize":       {"name": "Urea + SSP",             "detail": "SSP (250 kg/ha) as basal; Urea (100 kg/ha) split at sowing and knee-height stage."},
    "sugarcane":   {"name": "NPK 10-26-26 + Urea",   "detail": "Apply NPK 10-26-26 (300 kg/ha) at planting; Urea top-dressing at 30 and 90 days."},
    "cotton":      {"name": "DAP + MOP",              "detail": "DAP (100 kg/ha) at sowing; MOP (50 kg/ha) at squaring; Urea split in 3 doses."},
    "mungbean":    {"name": "SSP + Rhizobium",        "detail": "Seed treatment with Rhizobium; SSP (150 kg/ha) as basal; avoid excess Nitrogen."},
    "blackgram":   {"name": "SSP + Urea (low dose)",  "detail": "SSP (100 kg/ha) basal; Urea (15 kg/ha) only at sowing. Rhizobium seed treatment."},
    "lentil":      {"name": "DAP + Sulphur",          "detail": "DAP (100 kg/ha) at sowing; Sulphur (20 kg/ha) for improved protein content."},
    "chickpea":    {"name": "SSP + Urea + ZnSO4",     "detail": "SSP (150 kg/ha) basal; Urea (20 kg/ha) starter; ZnSO4 (25 kg/ha) if deficient."},
    "kidneybeans": {"name": "DAP + MOP + Boron",      "detail": "DAP (75 kg/ha) at planting; MOP (40 kg/ha); foliar Boron spray at flowering."},
    "pigeonpeas":  {"name": "SSP + Rhizobium + MOP",  "detail": "Rhizobium seed inoculation; SSP (100 kg/ha); MOP (40 kg/ha) at flowering."},
    "mothbeans":   {"name": "SSP + Urea (minimal)",   "detail": "SSP (80 kg/ha) at sowing; minimal Urea (10 kg/ha). Drought-tolerant — avoid over-fertilizing."},
    "pomegranate": {"name": "NPK 19-19-19 + Micro",   "detail": "NPK 19-19-19 (500 g/tree/year); FeSO4 + ZnSO4 micronutrient spray twice a season."},
    "banana":      {"name": "Urea + MOP + Borax",     "detail": "Urea (200 g/plant/month); MOP (300 g/plant); Borax (2 g/L) foliar spray at bunch emergence."},
    "mango":       {"name": "NPK 13-0-46 + Urea",     "detail": "Apply Urea at flushing; NPK 13-0-46 post-harvest; FeSO4 + MnSO4 micronutrient mix."},
    "grapes":      {"name": "NPK 12-61-0 + Ca(NO3)2", "detail": "High-P fertilizer at bud-break; Calcium Nitrate at berry set; K foliar at veraison."},
    "watermelon":  {"name": "NPK 13-40-13 + Calcium", "detail": "High-P starter; switch to K-dominant fertilizer at fruit set; Ca spray to prevent BER."},
    "muskmelon":   {"name": "NPK 19-19-19 + Boron",   "detail": "Balanced NPK through fertigation; Boron (1 g/L) at flowering; reduce N at fruit set."},
    "apple":       {"name": "Urea + DAP + ZnSO4",     "detail": "Urea pre-bloom + post-harvest; DAP at green tip; ZnSO4 + Borax dormant spray."},
    "orange":      {"name": "NPK 15-15-15 + MgSO4",   "detail": "Split NPK through the year; MgSO4 (2%) foliar for leaf greenness; Ca spray post-bloom."},
    "papaya":      {"name": "Urea + DAP + MOP",        "detail": "Monthly Urea (100 g/plant); DAP at planting; MOP (150 g/plant) every 2 months."},
    "coconut":     {"name": "NPK 13-0-46 + FeSO4",    "detail": "NPK 13-0-46 (1 kg/palm/year); FeSO4 + MnSO4 in basins; green manure as supplement."},
    "jute":        {"name": "Urea + SSP + MOP",        "detail": "SSP (250 kg/ha) basal; Urea (60 kg/ha) in 2 splits; MOP (60 kg/ha) at sowing."},
    "coffee":      {"name": "NPK 17-17-17 + K2SO4",   "detail": "NPK 17-17-17 (500 g/plant/year) in 3 doses; K2SO4 at berry development; Borax spray."},
}

# ── Rotation recommendations ───────────────────────────────────────────────────
ROTATION_NOTES = {
    ("rice",       "rice"):        "⚠️ Same crop again. Consider rotating with legumes (lentil/chickpea) to replenish Nitrogen.",
    ("wheat",      "wheat"):       "⚠️ Continuous wheat depletes Zinc. Rotate with maize or legumes next season.",
    ("maize",      "maize"):       "⚠️ Continuous maize risks rootworm buildup. Rotate with soybean or legumes.",
    ("cotton",     "cotton"):      "⚠️ Continuous cotton increases pest pressure. Rotate with cereals next season.",
    ("sugarcane",  "sugarcane"):   "⚠️ Long sugarcane ratoon reduces yields. Fallow or rotate with legumes.",
}

GOOD_ROTATIONS = {
    "legume":  ["chickpea", "kidneybeans", "lentil", "mungbean",
                "blackgram", "pigeonpeas", "mothbeans"],
    "cereal":  ["rice", "wheat", "maize", "jute"],
    "cash":    ["cotton", "sugarcane", "coffee"],
    "fruit":   ["banana", "mango", "apple", "grapes", "orange",
                "papaya", "pomegranate", "coconut", "watermelon",
                "muskmelon"],
}


def get_rotation_group(crop: str) -> str:
    for group, crops in GOOD_ROTATIONS.items():
        if crop in crops:
            return group
    return "other"


def make_rotation_note(prev: str, predicted: str) -> str:
    """Generate a meaningful rotation advisory."""
    key = (prev, predicted)
    if key in ROTATION_NOTES:
        return ROTATION_NOTES[key]

    pg = get_rotation_group(prev)
    rg = get_rotation_group(predicted)

    if pg == "cereal" and rg == "legume":
        return f"✅ Excellent rotation! {prev.title()} → {predicted.title()} fixes atmospheric Nitrogen and improves soil structure."
    if pg == "legume" and rg == "cereal":
        return f"✅ Great rotation! Legume residues from {prev.title()} enrich Nitrogen for {predicted.title()}."
    if pg == "cash" and rg == "cereal":
        return f"✅ Good rotation! Cereal after cash crop helps break pest cycles and restore soil balance."
    if pg == rg:
        return f"ℹ️ Both crops are in the same group ({pg}). Consider a cereal-legume rotation in future seasons."
    return f"✅ Switching from {prev.title()} to {predicted.title()} supports healthy crop diversity."


# ── Core prediction function ──────────────────────────────────────────────────
def predict_crop(model_bundle: dict, input_data: dict) -> dict:
    """
    Run prediction using the loaded model bundle.

    Parameters
    ----------
    model_bundle : dict — output of joblib.load(MODEL_PATH)
    input_data   : dict — keys: N, P, K, temperature, humidity, ph,
                          rainfall, previous_crop

    Returns
    -------
    dict with keys:
        crop, confidence, fertilizer_name, fertilizer_detail,
        rotation_note, top5 (list of {crop, prob})
    """
    from utils.preprocessing import preprocess_input

    clf    = model_bundle["model"]
    le_y   = model_bundle["le_y"]
    le_prev = model_bundle["le_prev"]

    X          = preprocess_input(input_data, le_prev)
    pred_idx   = clf.predict(X)[0]
    pred_crop  = le_y.inverse_transform([pred_idx])[0]
    proba      = clf.predict_proba(X)[0]
    confidence = round(float(proba.max()) * 100, 1)

    # Top-5 crops by probability
    top5_idx = proba.argsort()[::-1][:5]
    top5 = [
        {"crop": le_y.inverse_transform([i])[0].title(),
         "prob": round(float(proba[i]) * 100, 1)}
        for i in top5_idx
    ]

    fert = FERTILIZER_MAP.get(pred_crop, {
        "name":   "Balanced NPK",
        "detail": "Consult your local agri-extension officer for tailored advice."
    })
    prev = input_data.get("previous_crop", "")
    rot  = make_rotation_note(prev, pred_crop)

    return {
        "crop":              pred_crop,
        "crop_title":        pred_crop.title(),
        "confidence":        confidence,
        "fertilizer_name":   fert["name"],
        "fertilizer_detail": fert["detail"],
        "rotation_note":     rot,
        "top5":              top5,
    }
