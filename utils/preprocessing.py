# =============================================================================
# utils/preprocessing.py
# Data Preprocessing Module for Smart Crop Recommendation System
# =============================================================================

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler


# ── Constants ─────────────────────────────────────────────────────────────────
FEATURE_COLS  = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
FEATURE_NAMES = ["Nitrogen", "Phosphorus", "Potassium",
                 "Temperature", "Humidity", "pH", "Rainfall", "Previous Crop"]

VALID_RANGES = {
    "N":           (0,   140),
    "P":           (5,   145),
    "K":           (5,   205),
    "temperature": (8,    44),
    "humidity":    (14,  100),
    "ph":          (3.5, 9.94),
    "rainfall":    (20,  299),
}

PREVIOUS_CROPS = ["cotton", "maize", "rice", "sugarcane", "wheat"]

ALL_CROPS = [
    "apple", "banana", "blackgram", "chickpea", "coconut", "coffee",
    "cotton", "grapes", "jute", "kidneybeans", "lentil", "maize",
    "mango", "mothbeans", "mungbean", "muskmelon", "orange", "papaya",
    "pigeonpeas", "pomegranate", "rice", "watermelon",
]


# ── Dataset loader ─────────────────────────────────────────────────────────────
def load_dataset(path: str) -> pd.DataFrame:
    """Load the CSV dataset and perform basic sanity checks."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)

    # Standardise column names (strip whitespace, lowercase)
    df.columns = [c.strip().lower() for c in df.columns]

    required = {"n", "p", "k", "temperature", "humidity", "ph",
                "rainfall", "label", "previous_crop"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing columns: {missing}")

    # Drop nulls
    before = len(df)
    df = df.dropna()
    if len(df) < before:
        print(f"⚠️  Dropped {before - len(df)} rows with missing values.")

    # Restore original capitalisation expected by the rest of the code
    df = df.rename(columns={"n": "N", "p": "P", "k": "K"})

    print(f"✅ Dataset loaded: {df.shape[0]} rows, {df['label'].nunique()} crops")
    return df


# ── Encoder helpers ────────────────────────────────────────────────────────────
def build_encoders(df: pd.DataFrame):
    """
    Fit LabelEncoders for previous_crop and label columns.
    Returns (le_prev, le_label).
    """
    le_prev  = LabelEncoder().fit(df["previous_crop"])
    le_label = LabelEncoder().fit(df["label"])
    return le_prev, le_label


# ── Feature / target split ────────────────────────────────────────────────────
def prepare_features(df: pd.DataFrame, le_prev: LabelEncoder):
    """
    Encode categorical column and return X (numpy array) and column list.
    """
    df = df.copy()
    df["previous_crop_enc"] = le_prev.transform(df["previous_crop"])
    cols = FEATURE_COLS + ["previous_crop_enc"]
    X    = df[cols].values
    return X, cols


# ── Input validation ──────────────────────────────────────────────────────────
def validate_input(data: dict) -> tuple[bool, list]:
    """
    Validate a single prediction input dict.
    Returns (is_valid, list_of_error_messages).
    """
    errors = []
    for field, (lo, hi) in VALID_RANGES.items():
        val = data.get(field)
        if val is None:
            errors.append(f"'{field}' is required.")
            continue
        try:
            val = float(val)
        except (ValueError, TypeError):
            errors.append(f"'{field}' must be a number.")
            continue
        if not (lo <= val <= hi):
            errors.append(f"'{field}' must be between {lo} and {hi} (got {val}).")

    prev = data.get("previous_crop", "")
    if prev not in PREVIOUS_CROPS:
        errors.append(f"'previous_crop' must be one of: {PREVIOUS_CROPS}")

    return len(errors) == 0, errors


# ── Single-row pre-processor for prediction ────────────────────────────────────
def preprocess_input(data: dict, le_prev: LabelEncoder) -> np.ndarray:
    """
    Convert raw form data dict → numpy array ready for model.predict().
    Raises ValueError on bad input.
    """
    ok, errs = validate_input(data)
    if not ok:
        raise ValueError(" | ".join(errs))

    prev_enc = le_prev.transform([data["previous_crop"]])[0]

    row = [
        float(data["N"]),
        float(data["P"]),
        float(data["K"]),
        float(data["temperature"]),
        float(data["humidity"]),
        float(data["ph"]),
        float(data["rainfall"]),
        prev_enc,
    ]
    return np.array([row])


# ── Summary statistics for dashboard ──────────────────────────────────────────
def get_dataset_summary(df: pd.DataFrame) -> dict:
    """Return a dict of summary stats used by the analytics dashboard."""
    return {
        "total_samples":  len(df),
        "num_crops":      df["label"].nunique(),
        "crop_counts":    df["label"].value_counts().to_dict(),
        "prev_crop_counts": df["previous_crop"].value_counts().to_dict(),
        "nutrient_means": df.groupby("label")[["N", "P", "K"]].mean().round(2).to_dict(),
        "rainfall_stats": df.groupby("label")["rainfall"].mean().round(2).to_dict(),
        "ph_stats":       df.groupby("label")["ph"].mean().round(2).to_dict(),
        "feature_means":  df[FEATURE_COLS].mean().round(2).to_dict(),
    }
