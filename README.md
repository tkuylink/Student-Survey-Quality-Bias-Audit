<p align="center">
  <h1 align="center">Student Survey Quality & Bias Audit  </h1>
    <p align="center">

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Wrangling-brown)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Figures-informational)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Topic](https://img.shields.io/badge/Topic-Survey%20Quality%20%26%20Bias%20Audit-purple)
![Focus](https://img.shields.io/badge/Focus-Coverage%20%7C%20Representativeness%20%7C%20Measurement-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

A **portfolio-grade survey audit** that evaluates:
- **Coverage** (collection window and timing signals)
- **Representativeness** (sample composition + imbalance indicators)
- **Measurement risks** (scale design pitfalls)
- **Data validity checks** (ranges, allowed values, duplicates)
- **Open-text normalization** (turn messy “stress causes” into a clean taxonomy)

This project is intentionally designed to answer a higher-level question than typical EDA:

> **“How much can we trust insights from this survey, and what would make them more trustworthy?”**

---

## Dataset (Source + Thanks)
This project uses the Kaggle dataset:

- **Student Mental Health and Academic Pressure** by **alhamdulliah123**
- Dataset URL: https://www.kaggle.com/datasets/alhamdulliah123/student-mental-health-and-academic-pressure

Thanks to the dataset author and Kaggle for sharing the data for learning and analysis.

---

## Table of Contents
- [Why this project matters](#why-this-project-matters)
- [What you get](#what-you-get)
- [Quickstart](#quickstart)
- [How the audit works](#how-the-audit-works)
- [Figures & interpretation](#figures--interpretation)
  - [1) Sample composition: Age Group](#1-sample-composition-age-group)
  - [2) Sample composition: Education Level](#2-sample-composition-education-level)
  - [3) Sample composition: Gender](#3-sample-composition-gender)
  - [4) Academic pressure distribution (1–5)](#4-academic-pressure-distribution-15)
  - [5) Responses per day (collection window)](#5-responses-per-day-collection-window)
  - [6) Sleep hours distribution](#6-sleep-hours-distribution)
  - [7) Stress frequency distribution](#7-stress-frequency-distribution)
  - [8) Stress cause taxonomy (cleaned)](#8-stress-cause-taxonomy-cleaned)
- [Decision safety rules](#decision-safety-rules)
- [Outputs](#outputs)
- [Customize / extend](#customize--extend)
- [Notes & limitations](#notes--limitations)

---

## Why this project matters
Survey datasets often look “clean”:
- no missing values,
- simple distributions,
- easy charts.

But surveys can still be **analytically dangerous** because:
- the sample may be **skewed** (selection bias),
- the collection window may reflect a **narrow moment** (exams),
- the question design may **inflate responses** (measurement bias),
- open-text answers create **noise** that blocks usable insights.

This project makes those risks **visible** and **actionable**.

---

## What you get
### Audit Report
A markdown report generated at:
- `reports/audit_report.md`

It includes:
- dataset overview
- validity checks
- representativeness checks
- bias risk matrix
- taxonomy summary
- recommendations for improving the next survey run

### Figures
Saved under:
- `reports/figures/`

These figures are designed to be:
- stakeholder-friendly
- easy to interpret
- honest about uncertainty & representativeness

### Streamlit Dashboard
A simple dashboard at:
- `app/app.py`

It loads your generated outputs and visuals, and displays the report inside the app.

---

## Quickstart

### 1) Install dependencies
```bash
python -m venv .venv
# Windows:
# .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt
````

### 2) Run the pipeline

```bash
python -m src.pipeline --input data/raw/student_survey.csv
```

### 3) Run the dashboard

```bash
streamlit run app/app.py
```

---

## How the audit works

The pipeline performs these steps:

1. **Schema standardization**

* Survey exports often contain messy column names (spaces/newlines).
* The pipeline maps them into canonical names like:

  * `age_group`, `gender`, `education_level`, `academic_pressure`, etc.

2. **Type parsing**

* Parses timestamps and numeric pressure values safely (`errors="coerce"`).

3. **Validity checks**

* Academic pressure is expected in **[1..5]**.
* Stress frequency is validated against expected categories.
* Timestamp parsing success rate is recorded.

4. **Coverage signals**

* If timestamps exist: the pipeline estimates the **collection window** and response burst patterns.

5. **Representativeness / imbalance**

* For demographics, computes:

  * `max_share` (how dominant the top category is)
  * entropy (diversity)
  * effective number of categories

6. **Text normalization**

* Open-text stress causes are cleaned and mapped into a taxonomy:

  * Exams & grades, Financial, Workload & time, etc.
* Also exports a transparent mapping file for review.

7. **Reporting**

* Writes:

  * `reports/audit_report.md`
  * key CSV outputs
  * figures folder

---

# Figures & interpretation

> **Important note:** These charts describe *the survey respondents*, not the full student population.
> Use language like **“in this sample”** and avoid population claims unless sampling is representative.

---

## 1) Sample composition: Age Group

<img width="1024" height="768" alt="composition_age" src="https://github.com/user-attachments/assets/fd3da1d8-598c-4a04-90fa-2325723fb39c" />

### What this shows

Counts of respondents by age group.

### Why it matters (bias risk)

If one age group dominates the sample, you may accidentally conclude that:

* “students” behave a certain way,
  when you really mean:
* “students in the dominant age group in this sample.”

### How to interpret safely

* Treat this as a **coverage map** of who responded.
* When comparing groups, avoid strong claims for groups with very low counts.

### Actionable recommendation

If you want population-level insights, the next survey run should:

* recruit across age groups intentionally (quotas or stratified sampling)
* publish subgroup counts with every chart

---

## 2) Sample composition: Education Level

<img width="1024" height="768" alt="composition_education" src="https://github.com/user-attachments/assets/ba21bcaf-942c-4458-809d-2424b8dffc43" />

### What this shows

Counts of respondents by education level.

### Why it matters

If “College” dominates, then:

* pressure/stress distributions reflect college students more than others.

### Common analytics trap

People interpret this as:

* “College students are the majority in reality”
  But it might only mean:
* “College students were more likely to see/respond to the survey.”

### Actionable recommendation

* Track recruitment channel(s).
* Report response rate per group if possible.

---

## 3) Sample composition: Gender

<img width="1024" height="768" alt="composition_gender" src="https://github.com/user-attachments/assets/eb0725db-58e4-4aee-8b6e-b7c29c702594" />

### What this shows

Counts of respondents by gender.

### Why it matters

Even if the dataset is balanced, **gender composition affects interpretation**, especially for:

* stress reporting tendencies
* social desirability effects
* willingness to respond

### Safe interpretation

* Use this chart to decide which subgroup comparisons are meaningful.
* Always show **counts** next to percentages.

---

## 4) Academic pressure distribution (1–5)

<img width="1024" height="768" alt="pressure_distribution" src="https://github.com/user-attachments/assets/5fee64a2-5cf5-46b1-b8fd-2cc706f2cf8c" />

### What this shows

How many respondents selected each pressure level (1–5).

### Key interpretation points

* Pressure is **ordinal** (1 < 2 < 3 < 4 < 5), not a continuous measurement.
* For small samples, medians and category shares are often more honest than complicated models.

### What not to claim

* Avoid causal language like “X causes high pressure.”
* Avoid population prevalence claims unless the sample is representative.

### What you *can* do

* Describe where the sample concentrates (more 4–5 than 1–2).
* Use it to form hypotheses for larger data collection.

---

## 5) Responses per day (collection window)

<img width="1024" height="768" alt="responses_per_day" src="https://github.com/user-attachments/assets/c4578567-e3a5-448f-9e42-4a90c23a23e1" />

### What this shows

How many responses were submitted each day (based on timestamps).

### Why it matters (coverage risk)

If responses cluster heavily in one day, the survey may capture:

* a specific moment in time (exam week, deadlines, holidays),
  not a stable trend.

### Interpretation rule

A short, bursty collection window increases the risk of:

* time-window bias,
  and makes it harder to generalize.

### Recommendation for future survey runs

* Collect over multiple weeks.
* Add an “exam period” or “major deadlines this week” question.

---

## 6) Sleep hours distribution

<img width="1024" height="768" alt="sleep_distribution" src="https://github.com/user-attachments/assets/ec3f1489-c99b-42c8-a655-21afcd661752" />

### What this shows

Self-reported sleep category counts.

### Why it matters

Sleep is often used as an explanatory factor, but here it is:

* categorical and broad,
  which reduces precision.

### Safe interpretation

* Use it to describe the sample.
* Avoid overinterpreting differences unless subgroup sizes are reasonable.

### Recommendation

If you want stronger analysis:

* collect sleep as a numeric value (hours)
* optionally collect “sleep quality” too

---

## 7) Stress frequency distribution

<img width="1024" height="768" alt="stress_frequency_distribution" src="https://github.com/user-attachments/assets/57cd45f7-fbef-4aa6-a475-e3bdf81a2bc8" />

### What this shows

Counts of stress frequency responses.

### Measurement bias note (important)

If the survey scale lacks “Never” / “Rarely”, responses can be forced upward.
That can inflate perceived stress frequency.

### What to do in reporting

* Explicitly mention scale design limitations.
* Use phrases like “on this response scale” rather than “in reality”.

### Improvement recommendation

Use a balanced scale:

* Never / Rarely / Sometimes / Often / Always

---

## 8) Stress cause taxonomy (cleaned)

<img width="1024" height="768" alt="taxonomy_summary" src="https://github.com/user-attachments/assets/2e9369f2-1341-4411-9d2a-5fa26d21f793" />

### What this shows

Open-text “main cause of stress” answers normalized into a small set of categories.

### Why this step is powerful

Raw open-text answers often look like:

* many unique strings,
  even when they describe the same idea (“exams”, “tests”, “quiz pressure”).

A taxonomy makes the signal readable and reduces noise.

### Transparency / reproducibility

The raw-to-category mapping is exported to:

* `outputs/taxonomy_mapping.csv`

So you can:

* review decisions,
* adjust rules,
* and rerun the pipeline.

### Recommendation for future surveys

Use a hybrid approach:

* multi-select structured options + optional free text
  This preserves interpretability while still capturing new themes.

---

## Decision safety rules

These are rules you can apply to keep analysis honest:

* **Always include subgroup counts** in subgroup charts.
* Avoid interpreting subgroup differences when **n < 5**.
* Use wording:

  * “In this sample…”
  * “Students are…”
* Treat the dataset as **hypothesis-generating**, not population definitive.
* When in doubt, prefer:

  * **counts + ranges**
  * **clear limitations**
    over confident claims.

---

## Outputs

After running:

```bash
python -m src.pipeline --input data/raw/student_survey.csv
```

You get:

### Files

* `reports/audit_report.md` | generated audit report
* `reports/figures/` | all charts
* `outputs/audit_summary.json` | summary metadata + checks
* `outputs/bias_risk_matrix.csv` | structured bias table
* `outputs/grouped_stats.csv` | safe grouped summaries (means/medians)
* `outputs/taxonomy_mapping.csv` | transparent text mapping

---

## Customize / extend

### Improve the taxonomy

Edit rules in:

* `src/text_taxonomy.py`

Then rerun:

```bash
python -m src.pipeline --input data/raw/student_survey.csv
```

### Add uncertainty (advanced but impressive)

If you want next-level reporting:

* bootstrap confidence intervals for shares
* Bayesian credible intervals for proportions

This is ideal for small N and looks very professional.

### Fix Pandas warning (optional)

If you see a warning about `infer_datetime_format`:

* remove that argument from `pd.to_datetime(...)` in `src/clean_schema.py`.
  New pandas versions don’t need it.

---

## Notes & limitations

* Small dataset → subgroup comparisons can be unstable.
* Self-report → subject to social desirability and reporting bias.
* Recruitment channel unknown → selection bias likely.
* Missing scale options can inflate reported frequencies.

These limitations are not “bad news”, they are **exactly what makes this project mature**:
you are showing that you can produce analytics that are safe to trust.
