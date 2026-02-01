from __future__ import annotations

import re
from typing import Tuple
import pandas as pd

def _clean_text(s: str) -> str:
    s = str(s).strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^a-z0-9\s]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def categorize_stress_cause(raw: str) -> str:
    s = _clean_text(raw)
    if s in {"", "nan"}:
        return "Unspecified"
    if "prefer not" in s or "prefer" in s:
        return "Prefer not to say"
    if s == "other":
        return "Other"
    if any(k in s for k in ["exam", "grade", "test", "quiz", "result", "gpa"]):
        return "Exams & grades"
    if any(k in s for k in ["financial", "money", "fees", "tuition", "income", "cost"]):
        return "Financial"
    if any(k in s for k in ["deadline", "workload", "assignment", "project", "homework", "time", "study load"]):
        return "Workload & time"
    if any(k in s for k in ["family", "relationship", "parents", "personal", "health", "mental", "life"]):
        return "Family & personal"
    if any(k in s for k in ["career", "future", "job", "employment", "internship"]):
        return "Career & future"
    if any(k in s for k in ["expectation", "competitive", "competition", "rank", "peer"]):
        return "Expectations & competition"
    return "Other"

def build_taxonomy(df: pd.DataFrame, col: str = "stress_cause") -> Tuple[pd.DataFrame, pd.DataFrame]:
    if col not in df.columns:
        return (
            pd.DataFrame(columns=["raw_text", "cleaned_text", "category"]),
            pd.DataFrame(columns=["category", "count", "share"]),
        )
    raw = df[col].astype(str)
    cleaned = raw.map(_clean_text)
    category = raw.map(categorize_stress_cause)
    mapping = pd.DataFrame({"raw_text": raw, "cleaned_text": cleaned, "category": category})
    mapping_unique = mapping.drop_duplicates(subset=["raw_text", "category"]).sort_values(["category", "raw_text"])
    summary = (
        mapping["category"].value_counts()
        .rename_axis("category")
        .reset_index(name="count")
        .assign(share=lambda x: x["count"] / x["count"].sum())
        .sort_values("count", ascending=False)
    )
    return mapping_unique, summary
