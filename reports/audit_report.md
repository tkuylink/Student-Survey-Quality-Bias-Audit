# Student Survey Quality & Bias Audit

This report evaluates **coverage, sample representativeness, measurement risks, and text-response noise**.
It is designed to prevent overconfident conclusions from small or biased survey samples.

## Dataset overview
- Responses: **33**
- Columns: **10**
- Collection window: **2025-12-13 06:18:00 → 2025-12-14 05:30:00**
- Calendar days covered: **2**
- Largest single-day share: **84.8%**

## Key interpretation guardrails
- This is a **survey sample**, not a controlled population study.
- Treat subgroup comparisons as low confidence when subgroup size is small (commonly **n < 5**).
- Use language like **'in this sample'** rather than population-level claims.

## Data validity checks
| name                            |   invalid_count | allowed                          |   parsed_ok |   parsed_bad |
|:--------------------------------|----------------:|:---------------------------------|------------:|-------------:|
| academic_pressure_range_1_to_5  |               0 | nan                              |         nan |          nan |
| stress_frequency_allowed_values |               0 | ['Always', 'Often', 'Sometimes'] |         nan |          nan |
| timestamp_parse_rate            |             nan | nan                              |          33 |            0 |

## Bias risk matrix
| bias_type                               | risk_level   | evidence                                                                           | mitigation_next_time                                                                                |
|:----------------------------------------|:-------------|:-----------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------|
| Selection / volunteer bias              | High         | Voluntary responses; sample may over-represent students motivated to respond.      | Structured recruitment, track response rates, stratify by student groups.                           |
| Time-window / burst collection bias     | High         | Responses collected within ~2 day(s); may reflect a narrow moment (e.g., exams).   | Collect over multiple weeks; add an exam-period indicator; compare early vs late responses.         |
| Demographic imbalance (Age group)       | Medium       | Top category share is 60.6%; distribution may not represent the target population. | Use quotas/stratified sampling; publish subgroup counts; avoid population claims with low-N groups. |
| Demographic imbalance (Gender)          | Medium       | Top category share is 63.6%; distribution may not represent the target population. | Use quotas/stratified sampling; publish subgroup counts; avoid population claims with low-N groups. |
| Demographic imbalance (Education level) | High         | Top category share is 72.7%; distribution may not represent the target population. | Use quotas/stratified sampling; publish subgroup counts; avoid population claims with low-N groups. |
| Measurement / instrument bias           | Medium       | Stress frequency scale lacks 'Never/Rarely' which can inflate frequency estimates. | Use balanced Likert scale with clear anchors.                                                       |
| Social desirability bias                | Medium       | Self-reported stress may be under/over-reported depending on context.              | Anonymous collection; neutral wording; include validated scales where possible.                     |

## Stress cause taxonomy (open-text normalization)
| category                   |   count |    share |
|:---------------------------|--------:|---------:|
| Exams & grades             |      13 | 0.393939 |
| Financial                  |       8 | 0.242424 |
| Other                      |       8 | 0.242424 |
| Prefer not to say          |       1 | 0.030303 |
| Workload & time            |       1 | 0.030303 |
| Family & personal          |       1 | 0.030303 |
| Expectations & competition |       1 | 0.030303 |

**Why this matters:** open-text answers create many near-duplicates. A transparent taxonomy makes patterns readable without overfitting.

## Recommendations for the next survey run
### Representativeness
- Recruit across multiple groups (age/education), not a single channel.
- Track invite count and response rate to quantify selection bias.

### Measurement quality
- Use balanced Likert options (Never → Always).
- Add structured stress-cause options + optional free text.

### Analysis safety
- Report subgroup counts alongside charts.
- Avoid causal language; use effect sizes and uncertainty where possible.

## Notes
- **Small sample warning**: Interpret subgroup differences cautiously; low-N segments can be unstable.
- **Taxonomy transparency**: Mapping exported to outputs\taxonomy_mapping.csv.
