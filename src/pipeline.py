from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any

import pandas as pd
import matplotlib.pyplot as plt

from src.io import read_csv, write_csv, write_json
from src.clean_schema import standardize_schema, parse_types
from src.audit_checks import basic_profile, validity_checks
from src.bias_analysis import imbalance_indicators, time_window_summary, bias_risk_matrix
from src.text_taxonomy import build_taxonomy
from src.reporting import write_audit_report


def _save_bar(series: pd.Series, title: str, out_path: Path, xlabel: str = "", ylabel: str = "Count") -> None:
    plt.figure()
    series.plot(kind="bar")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=160)
    plt.close()


def run(
    input_path: str,
    out_dir: str = "outputs",
    report_path: str = "reports/audit_report.md",
    figures_dir: str = "reports/figures",
) -> Dict[str, Any]:
    out_dir = Path(out_dir)
    figures_dir = Path(figures_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    df_raw = read_csv(input_path)
    df_std, schema_meta = standardize_schema(df_raw)
    df = parse_types(df_std)

    # Save processed copy
    proc_path = Path("data/processed/processed_survey.csv")
    proc_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(proc_path, index=False)

    profile = basic_profile(df)
    validity = validity_checks(df)
    tw = time_window_summary(df)

    # Composition figures + imbalance indicators
    imbalance = {}
    for col, fig_name in [
        ("age_group", "composition_age.png"),
        ("gender", "composition_gender.png"),
        ("education_level", "composition_education.png"),
    ]:
        if col in df.columns:
            vc = df[col].value_counts(dropna=False)
            _save_bar(vc, f"Sample composition: {col.replace('_', ' ').title()}", figures_dir / fig_name)
            imbalance[col] = imbalance_indicators(df[col])

    # Responses per day
    if "timestamp_parsed" in df.columns and df["timestamp_parsed"].notna().any():
        by_day = df["timestamp_parsed"].dropna().dt.normalize().value_counts().sort_index()
        _save_bar(by_day, "Responses per day (collection window)", figures_dir / "responses_per_day.png", xlabel="Date")

    # Distributions
    if "academic_pressure_num" in df.columns:
        vc = df["academic_pressure_num"].value_counts().sort_index()
        _save_bar(vc, "Academic pressure distribution (1–5)", figures_dir / "pressure_distribution.png", xlabel="Pressure (1–5)")

    if "stress_frequency" in df.columns:
        vc = df["stress_frequency"].value_counts()
        _save_bar(vc, "Stress frequency distribution", figures_dir / "stress_frequency_distribution.png")

    if "sleep_hours" in df.columns:
        vc = df["sleep_hours"].value_counts()
        _save_bar(vc, "Sleep hours distribution", figures_dir / "sleep_distribution.png")

    # Taxonomy
    mapping_df, tax_summary = build_taxonomy(df, col="stress_cause")
    write_csv(mapping_df, out_dir / "taxonomy_mapping.csv")
    if not tax_summary.empty:
        plt.figure()
        plt.bar(tax_summary["category"], tax_summary["count"])
        plt.xticks(rotation=30, ha="right")
        plt.title("Stress cause taxonomy (cleaned)")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig(figures_dir / "taxonomy_summary.png", dpi=160)
        plt.close()

    # Grouped stats (simple)
    grouped_rows = []
    if "academic_pressure_num" in df.columns:
        for col in ["age_group", "gender", "education_level"]:
            if col in df.columns:
                g = df.groupby(col, dropna=False).agg(
                    n=("academic_pressure_num", "size"),
                    pressure_mean=("academic_pressure_num", "mean"),
                    pressure_median=("academic_pressure_num", "median"),
                ).reset_index().rename(columns={col: "group_value"})
                g.insert(0, "group_by", col)
                grouped_rows.append(g)

    grouped_stats = pd.concat(grouped_rows, ignore_index=True) if grouped_rows else pd.DataFrame()
    write_csv(grouped_stats, out_dir / "grouped_stats.csv")

    # Bias matrix
    bias_df = bias_risk_matrix(df)
    bias_df.to_csv(out_dir / "bias_risk_matrix.csv", index=False)

    summary = {
        "schema": schema_meta,
        "profile": profile,
        "time_window": tw,
        "imbalance_indicators": imbalance,
        "validity": validity,
        "files": {
            "processed_csv": str(proc_path),
            "audit_summary": str(out_dir / "audit_summary.json"),
            "taxonomy_mapping": str(out_dir / "taxonomy_mapping.csv"),
            "grouped_stats": str(out_dir / "grouped_stats.csv"),
            "bias_risk_matrix": str(out_dir / "bias_risk_matrix.csv"),
        },
    }
    write_json(summary, out_dir / "audit_summary.json")

    notes = {
        "Small sample warning": "Interpret subgroup differences cautiously; low-N segments can be unstable.",
        "Taxonomy transparency": f"Mapping exported to {summary['files']['taxonomy_mapping']}.",
    }

    write_audit_report(
        report_path=report_path,
        summary={"profile": profile, "time_window": tw, "validity": validity},
        bias_matrix=bias_df,
        taxonomy_summary=tax_summary,
        notes=notes,
    )

    return {
        "out_dir": str(out_dir),
        "report_path": str(Path(report_path)),
        "figures_dir": str(figures_dir),
        "n_rows": profile["n_rows"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Student survey quality & bias audit")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--out", default="outputs", help="Outputs directory")
    parser.add_argument("--report", default="reports/audit_report.md", help="Report markdown path")
    parser.add_argument("--figures", default="reports/figures", help="Figures directory")
    args = parser.parse_args()

    res = run(args.input, args.out, args.report, args.figures)

    print("\nDone! Audit project outputs created.", flush=True)
    print(f"Outputs folder: {res['out_dir']}", flush=True)
    print(f"Report: {res['report_path']}", flush=True)
    print(f"Figures: {res['figures_dir']}", flush=True)
    print(f"Responses analyzed: {res['n_rows']}\n", flush=True)


if __name__ == "__main__":
    main()
