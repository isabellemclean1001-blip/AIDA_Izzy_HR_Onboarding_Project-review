# AIDA 2156 Final Professional Project – Where Onboarding Delays Appear

> **Status: in progress.** Working plan; scope, methods, and deliverables to be confirmed with the instructor.

## Course focus

Apply and interpret appropriate statistical methods, and communicate findings with visualizations or a dashboard.

## Question

In synthetic onboarding records for the fictional Town of Pinecrest, where do delays and incomplete handoffs appear in the workflow, and how reliable are those findings?

The fictional HR team lead would use the findings to decide where to monitor more closely and what to investigate further. Observed delays do not by themselves establish causes such as a staffing or capacity problem.

## Data

**Data version 2**, in [`shared/synthetic-data/`](../../shared/synthetic-data/): the raw system export (`requests/data/requests.csv`) for completeness analysis, the cleaned requests (`cleaning/output/requests_cleaned.csv`), and status events (`requests/data/status_events.csv`). The answer key and simulation values in `requests/evaluation_only/` are never used for analysis.

Earlier project exercises (`../project-labs/`) used **data version 1** and remain unchanged as an earlier checkpoint. Results from the two versions are not mixed.

## Planned approach

1. **Data quality and missingness:** describe missing, inconsistent, and invalid values in the raw export, whether missingness differs by channel or task type, how cleaning handles them, and which values remain unresolved.
2. **Distributions:** measure processing time as working time, using the simulated closure calendar and a documented rule for after-hours submissions, and summarize centre, spread, and skew overall and by task type.
3. **Process steps:** split processing time into the information check, assignment, and team processing, and identify the longest observed stage.
4. **Relationships and confounding:** examine how processing time relates to task type, channel, department, workload, and timing, and check whether an apparent difference changes when a third variable is taken into account.
5. **Statistical inference:** estimate differences between groups and periods with confidence intervals that account for related tasks from the same employee (for example, resampling employees rather than individual tasks), and interpret them carefully.
6. **Feature relationships:** use correlation and principal component analysis to see which workflow measures move together.
7. **Outliers and robustness:** review unusually long or short requests and check whether robust summaries and reasonable analysis choices (for example, the after-hours rule and including or excluding requests unfinished at the extract date) change the conclusions.
8. **Workload over time:** describe weekly arrivals, completions, and outstanding requests across both simulated years, and whether the spring pattern recurs within the simulation.
9. **Communicate findings and uncertainty** in a dashboard or a set of labelled visualizations, each with a caption and a note on data limits.

The methods build on AIDA 2156 Exercises 01–06, rerun on data version 2. The method choice is to be confirmed with the instructor.

## Planned deliverables

- Analysis notebooks (`analysis/`) and figures (`figures/`)
- Dashboard or labelled visualization set
- `report.md`: questions, methods, findings, uncertainty, and limitations
- `decision-brief.md`: what the evidence supports and what further evidence would be needed
- Demonstration for the final technical defence

For each analysis included: the question, data version, method, key finding, limitation, and steps to reproduce.

## Checkpoints

| Week | Checkpoint |
|:---|:---|
| 10 (2–6 Nov) | Gate 3: working prototype (bring early project work) |
| 12 (16–20 Nov) | Gate 4: validation evidence; review preliminary findings, errors, risks, and limitations |
| 14 (30 Nov–4 Dec) | Gate 5: release candidate, in-class presentation, reproducibility review, and revision |
| 15 (7–9 Dec) | Gate 6: release readiness and documentation check |
| Final-examination period (14–18 Dec) | Submit, demonstrate, and complete the individual technical defence |

## Boundaries

This project uses only synthetic records and describes patterns in a simulated workflow, not real HR performance or staff effort. Its analysis is distinct from the AIDA 1141 and AIDA 2154 final projects, which share the same workflow and data but answer different questions.
