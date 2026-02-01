from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import pandas as pd

def _md_table(df: pd.DataFrame, max_rows: int = 50) -> str:
    if df.empty:
        return "_(no data)_"
    return df.head(max_rows).to_markdown(index=False)

def write_audit_report(
    report_path: str | Path,
    summary: Dict[str, Any],
    bias_matrix: pd.DataFrame,
    taxonomy_summary: pd.DataFrame,
    notes: Dict[str, str],
) -> None:
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    md = []
    md.append("# Student Survey Quality & Bias Audit")
    md.append("")
    md.append("This report evaluates **coverage, sample representativeness, measurement risks, and text-response noise**.")
    md.append("It is designed to prevent overconfident conclusions from small or biased survey samples.")
    md.append("")

    md.append("## Dataset overview")
    md.append(f"- Responses: **{summary['profile']['n_rows']}**")
    md.append(f"- Columns: **{summary['profile']['n_cols']}**")
    tw = summary.get("time_window", {})
    if tw.get("has_timestamp"):
        md.append(f"- Collection window: **{tw.get('min_timestamp')} → {tw.get('max_timestamp')}**")
        md.append(f"- Calendar days covered: **{tw.get('calendar_days_covered')}**")
        md.append(f"- Largest single-day share: **{tw.get('max_day_share', 0):.1%}**")
    md.append("")

    md.append("## Key interpretation guardrails")
    md.append("- This is a **survey sample**, not a controlled population study.")
    md.append("- Treat subgroup comparisons as low confidence when subgroup size is small (commonly **n < 5**).")
    md.append("- Use language like **'in this sample'** rather than population-level claims.")
    md.append("")

    md.append("## Data validity checks")
    checks = pd.DataFrame(summary.get("validity", {}).get("checks", []))
    md.append(_md_table(checks))
    md.append("")

    md.append("## Bias risk matrix")
    md.append(_md_table(bias_matrix))
    md.append("")

    md.append("## Stress cause taxonomy (open-text normalization)")
    md.append(_md_table(taxonomy_summary))
    md.append("")
    md.append("**Why this matters:** open-text answers create many near-duplicates. A transparent taxonomy makes patterns readable without overfitting.")
    md.append("")

    md.append("## Recommendations for the next survey run")
    md.append("### Representativeness")
    md.append("- Recruit across multiple groups (age/education), not a single channel.")
    md.append("- Track invite count and response rate to quantify selection bias.")
    md.append("")
    md.append("### Measurement quality")
    md.append("- Use balanced Likert options (Never → Always).")
    md.append("- Add structured stress-cause options + optional free text.")
    md.append("")
    md.append("### Analysis safety")
    md.append("- Report subgroup counts alongside charts.")
    md.append("- Avoid causal language; use effect sizes and uncertainty where possible.")
    md.append("")

    md.append("## Notes")
    for k, v in notes.items():
        md.append(f"- **{k}**: {v}")

    report_path.write_text("\n".join(md).strip() + "\n", encoding="utf-8")
