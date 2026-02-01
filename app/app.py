import sys
import json
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import run as run_pipeline  # noqa: E402

st.set_page_config(page_title="Survey Quality & Bias Audit", layout="wide")

st.title("Student Survey Quality & Bias Audit")
st.caption("Coverage, representativeness, measurement risks, and text taxonomy — designed to prevent misleading conclusions.")

DEFAULT_INPUT = PROJECT_ROOT / "data" / "raw" / "student_survey.csv"
OUT_DIR = PROJECT_ROOT / "outputs"
REPORT_PATH = PROJECT_ROOT / "reports" / "audit_report.md"
FIG_DIR = PROJECT_ROOT / "reports" / "figures"

with st.sidebar:
    st.header("Run audit")
    uploaded = st.file_uploader("Upload CSV (optional)", type=["csv"])
    input_path = st.text_input("Or CSV path", value=str(DEFAULT_INPUT))
    run_btn = st.button("Run / Refresh Audit")

effective_input = Path(input_path)
if uploaded is not None:
    tmp_dir = PROJECT_ROOT / "data" / "raw"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / "uploaded_survey.csv"
    tmp_path.write_bytes(uploaded.getbuffer())
    effective_input = tmp_path

if run_btn:
    with st.spinner("Running audit pipeline..."):
        run_pipeline(
            input_path=str(effective_input),
            out_dir=str(OUT_DIR),
            report_path=str(REPORT_PATH),
            figures_dir=str(FIG_DIR),
        )
    st.success("✅ Done! Audit outputs + report regenerated.")

summary_path = OUT_DIR / "audit_summary.json"
mapping_path = OUT_DIR / "taxonomy_mapping.csv"
grouped_path = OUT_DIR / "grouped_stats.csv"
bias_path = OUT_DIR / "bias_risk_matrix.csv"

if not summary_path.exists():
    st.info("Run the audit from the sidebar to generate outputs.")
    st.stop()

summary = json.loads(summary_path.read_text(encoding="utf-8"))
mapping = pd.read_csv(mapping_path) if mapping_path.exists() else pd.DataFrame()
grouped = pd.read_csv(grouped_path) if grouped_path.exists() else pd.DataFrame()
bias_df = pd.read_csv(bias_path) if bias_path.exists() else pd.DataFrame()

tab_overview, tab_bias, tab_taxonomy, tab_report = st.tabs(["Overview", "Bias & Coverage", "Text Taxonomy", "Report"])

with tab_overview:
    c1, c2, c3 = st.columns(3)
    c1.metric("Responses", summary["profile"]["n_rows"])
    c2.metric("Columns", summary["profile"]["n_cols"])
    tw = summary.get("time_window", {})
    c3.metric("Days covered", tw.get("calendar_days_covered", "N/A"))

    st.subheader("Imbalance indicators (high values imply skew)")
    im = summary.get("imbalance_indicators", {})
    if im:
        rows = []
        for field, vals in im.items():
            rows.append({"field": field, **vals})
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    else:
        st.info("No imbalance indicators available.")

    st.subheader("Grouped stats (safe summaries)")
    if not grouped.empty:
        st.dataframe(grouped, width="stretch", hide_index=True)
    else:
        st.info("No grouped stats available.")

with tab_bias:
    st.subheader("Collection window (responses per day)")
    fig_path = FIG_DIR / "responses_per_day.png"
    if fig_path.exists():
        st.image(str(fig_path), width="stretch")
    else:
        st.info("No timestamp coverage chart available.")

    st.subheader("Bias risk matrix")
    if not bias_df.empty:
        st.dataframe(bias_df, width="stretch", hide_index=True)
    else:
        st.info("Bias matrix not available.")

    st.subheader("Decision safety notes")
    st.markdown(
        "- Avoid population claims unless sampling is representative.\n"
        "- Treat subgroup comparisons as **low confidence** when subgroup size is small (commonly `n < 5`).\n"
        "- Report counts alongside percentages.\n"
        "- Use neutral language: **in this sample** rather than **students generally**."
    )

with tab_taxonomy:
    st.subheader("Raw → cleaned taxonomy mapping")
    if not mapping.empty:
        st.dataframe(mapping, width="stretch", hide_index=True)
        st.subheader("Category counts")
        cat_counts = mapping.groupby("category")["raw_text"].count().sort_values(ascending=False).reset_index(name="n")
        st.plotly_chart(px.bar(cat_counts, x="category", y="n"), width="stretch")
    else:
        st.info("Taxonomy mapping not found. Run pipeline.")

with tab_report:
    st.subheader("Audit report (Markdown)")
    if REPORT_PATH.exists():
        st.markdown(REPORT_PATH.read_text(encoding="utf-8"))
    else:
        st.info("Report not found. Run pipeline.")
