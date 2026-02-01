from __future__ import annotations

import re
from typing import Dict, Tuple, Optional
import pandas as pd

_CANONICAL = {
    "timestamp": ["timestamp", "time", "submitted", "date/time"],
    "age_group": ["age group", "age", "agegroup"],
    "gender": ["gender", "sex"],
    "education_level": ["current education level", "education level", "education"],
    "academic_pressure": ["how much academic pressure", "academic pressure"],
    "stress_frequency": ["how often do you feel stressed", "stress due to studies", "stress frequency"],
    "sleep_hours": ["how many hours do you sleep", "sleep", "sleep hours"],
    "stress_cause": ["main cause of your academic stress", "cause of your academic stress", "stress cause"],
}

def _normalize_col(name: str) -> str:
    name = re.sub(r"\s+", " ", str(name)).strip().lower()
    return name

def _match_column(cols_norm: Dict[str, str], keywords: list[str]) -> Optional[str]:
    for original, normed in cols_norm.items():
        for kw in keywords:
            if kw in normed:
                return original
    return None

def standardize_schema(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    cols_norm = {c: _normalize_col(c) for c in df.columns}
    mapping: Dict[str, str] = {}
    for canon, keys in _CANONICAL.items():
        hit = _match_column(cols_norm, keys)
        if hit is not None:
            mapping[hit] = canon
    df2 = df.rename(columns=mapping).copy()
    meta = {
        "original_columns": list(df.columns),
        "mapping_used": mapping,
        "canonical_columns_present": [c for c in _CANONICAL.keys() if c in df2.columns],
        "canonical_columns_missing": [c for c in _CANONICAL.keys() if c not in df2.columns],
    }
    return df2, meta

def parse_types(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "timestamp" in out.columns:
        out["timestamp_parsed"] = pd.to_datetime(out["timestamp"], errors="coerce")
    if "academic_pressure" in out.columns:
        out["academic_pressure_num"] = pd.to_numeric(out["academic_pressure"], errors="coerce")
    for col in ["age_group", "gender", "education_level", "stress_frequency", "sleep_hours", "stress_cause"]:
        if col in out.columns:
            out[col] = out[col].astype(str).str.strip()
    return out
