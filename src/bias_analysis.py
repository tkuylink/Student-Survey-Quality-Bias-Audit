from __future__ import annotations

from typing import Dict, Any
import numpy as np
import pandas as pd

def _share(series: pd.Series) -> pd.Series:
    vc = series.value_counts(dropna=False)
    return vc / vc.sum()

def imbalance_indicators(series: pd.Series) -> Dict[str, Any]:
    p = _share(series).astype(float)
    p = p[p > 0]
    max_share = float(p.max()) if len(p) else float("nan")
    entropy = float(-(p * np.log(p)).sum()) if len(p) else float("nan")
    effective_n = float(np.exp(entropy)) if len(p) else float("nan")
    return {"max_share": max_share, "entropy": entropy, "effective_n": effective_n}

def time_window_summary(df: pd.DataFrame) -> Dict[str, Any]:
    if "timestamp_parsed" not in df.columns:
        return {"has_timestamp": False}
    ts = df["timestamp_parsed"].dropna()
    if ts.empty:
        return {"has_timestamp": True, "parsed_nonnull": 0}
    min_ts = ts.min()
    max_ts = ts.max()
    days = (max_ts.normalize() - min_ts.normalize()).days + 1
    by_day = ts.dt.normalize().value_counts().sort_index()
    return {
        "has_timestamp": True,
        "min_timestamp": str(min_ts),
        "max_timestamp": str(max_ts),
        "calendar_days_covered": int(days),
        "responses_per_day": {str(k.date()): int(v) for k, v in by_day.items()},
        "max_day_share": float(by_day.max() / by_day.sum()) if by_day.sum() else None,
    }

def bias_risk_matrix(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    rows.append({
        "bias_type": "Selection / volunteer bias",
        "risk_level": "High",
        "evidence": "Voluntary responses; sample may over-represent students motivated to respond.",
        "mitigation_next_time": "Structured recruitment, track response rates, stratify by student groups."
    })

    tw = time_window_summary(df)
    if tw.get("has_timestamp") and tw.get("calendar_days_covered", 0) <= 2:
        rows.append({
            "bias_type": "Time-window / burst collection bias",
            "risk_level": "High",
            "evidence": f"Responses collected within ~{tw.get('calendar_days_covered')} day(s); may reflect a narrow moment (e.g., exams).",
            "mitigation_next_time": "Collect over multiple weeks; add an exam-period indicator; compare early vs late responses."
        })
    else:
        rows.append({
            "bias_type": "Time-window / burst collection bias",
            "risk_level": "Medium",
            "evidence": "Collection window unknown or longer; temporal skew still possible.",
            "mitigation_next_time": "Record collection window; recruit evenly across time."
        })

    for col, label in [("age_group", "Age group"), ("gender", "Gender"), ("education_level", "Education level")]:
        if col in df.columns:
            ind = imbalance_indicators(df[col])
            max_share = ind["max_share"]
            risk = "High" if max_share >= 0.65 else ("Medium" if max_share >= 0.50 else "Low")
            rows.append({
                "bias_type": f"Demographic imbalance ({label})",
                "risk_level": risk,
                "evidence": f"Top category share is {max_share:.1%}; distribution may not represent the target population.",
                "mitigation_next_time": "Use quotas/stratified sampling; publish subgroup counts; avoid population claims with low-N groups."
            })

    rows.append({
        "bias_type": "Measurement / instrument bias",
        "risk_level": "Medium",
        "evidence": "Stress frequency scale lacks 'Never/Rarely' which can inflate frequency estimates.",
        "mitigation_next_time": "Use balanced Likert scale with clear anchors."
    })
    rows.append({
        "bias_type": "Social desirability bias",
        "risk_level": "Medium",
        "evidence": "Self-reported stress may be under/over-reported depending on context.",
        "mitigation_next_time": "Anonymous collection; neutral wording; include validated scales where possible."
    })
    return pd.DataFrame(rows)
