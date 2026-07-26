# Day Scenario Human Review Rubric C3.6.2

**Status:** CANON (rubric for blind human labeling)  
**Version:** `day_scenario_human_review_rubric_c362.1`  
**Parent:** [DAY_SCENARIO_HUMAN_GOLDEN_C362.md](./DAY_SCENARIO_HUMAN_GOLDEN_C362.md)

## Overall scenario band (operational)

| Band | Definition |
|------|------------|
| **pass** | Can ship to the user **without** editorial rewrite. Safe, coherent, useful enough. |
| **acceptable_with_issues** | Useful and safe, but has **noticeable** quality defects. Not an automatic negative for every analyzer hit. |
| **reject** | Objectively not useful / coherent / personalized enough to show as a day scenario. |
| **cannot_assess** | Missing language skill, evidence context, or confidence — **exclude** from P/R. |

Do **not** derive defect labels only from `reject`.

## Defect labels

For each defect code in the catalog:

| Presence | Meaning |
|----------|---------|
| **present** | Defect is clearly visible in the scenario text/structure. |
| **absent** | Defect is clearly not present. |
| **uncertain** | Reviewer cannot decide — **not** counted as absent. |
| **not_applicable** | Code does not apply to this case (e.g. locale-only rule on wrong locale) — **not** negative support. |

Also record when present:

- **severity:** `minor` | `material` | `severe`
- **evidence_location** (path into scenario)
- short **rationale**
- whether it **affects_overall_band**

## Blind rules

Reviewers must **not** see:

- analyzer defects / scores  
- gate maturity / runtime action  
- synthetic expected labels / mutation names  
- other reviewers’ labels  

Analyzer output attaches **only after** consensus is sealed.

## Quorum

- Minimum **two** independent reviewers.  
- Disagreement → adjudicator → sealed consensus.  
- History is **append-only**.
