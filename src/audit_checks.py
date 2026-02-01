from __future__ import annotations

from typing import Dict, Any, List
import pandas as pd

ALLOWED_STRESS_FREQ = {"Sometimes", "Often", "Always"}

def basic_profile(df: pd.DataFrame) -> Dict[str, Any]:
    return {
        "n_rows": int(len(df)),
        "n_cols": int(df.shape[1]),
        "columns": list(df.columns),
        "missing_values": df.isna().sum().to_dict(),
        "missing_any_row": int(df.isna().any(axis=1).sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }

def validity_checks(df: pd.DataFrame) -> Dict[str, Any]:
    results: Dict[str, Any] = {"checks": []}

    if "academic_pressure_num" in df.columns:
        invalid = df[df["academic_pressure_num"].notna() & ~df["academic_pressure_num"].between(1, 5)]
        results["checks"].append({
            "name": "academic_pressure_range_1_to_5",
            "invalid_count": int(len(invalid)),
        })

    if "stress_frequency" in df.columns:
        invalid = df[~df["stress_frequency"].isin(ALLOWED_STRESS_FREQ)]
        results["checks"].append({
            "name": "stress_frequency_allowed_values",
            "allowed": sorted(list(ALLOWED_STRESS_FREQ)),
            "invalid_count": int(len(invalid)),
        })

    if "timestamp_parsed" in df.columns:
        results["checks"].append({
            "name": "timestamp_parse_rate",
            "parsed_ok": int(df["timestamp_parsed"].notna().sum()),
            "parsed_bad": int(df["timestamp_parsed"].isna().sum()),
        })

    return results

def subgroup_counts(df: pd.DataFrame, cols: List[str]) -> Dict[str, Any]:
    out = {}
    for c in cols:
        if c in df.columns:
            out[c] = df[c].value_counts(dropna=False).to_dict()
    return out
