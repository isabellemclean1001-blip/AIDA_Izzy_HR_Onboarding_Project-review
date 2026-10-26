# AIDA 1141 Final Professional Project – Onboarding Tasks at Risk of Missing the Start Date

> **Status: in progress.** Working plan; scope, methods, and deliverables to be confirmed with the instructor.

## Course focus

Investigate a data-science or introductory machine-learning question, and document the problem, data, method, evaluation, risks, findings, and next steps.

## Question

Using synthetic onboarding records for the fictional Town of Pinecrest, can a model flag onboarding tasks at risk of missing the employee's start date better than simple follow-up rules, at a review volume the coordinator could manage? When should the coordinator not rely on it?

The coordinator decides whether to follow up on a task. The model only suggests which tasks to review; a person confirms every follow-up.

## Data

**Data version 2**, in [`shared/synthetic-data/`](../../shared/synthetic-data/): the cleaned requests (`cleaning/output/requests_cleaned.csv`) and the assessment snapshots (`requests/data/assessments.csv`). The answer key and simulation values in `requests/evaluation_only/` are never used for modelling.

Earlier project exercises (`../project-labs/`) used **data version 1** and remain unchanged as an earlier checkpoint. Results from the two versions are not mixed.

## Planned approach

1. **Define eligible assessments and labels:** a task is at risk if the team finishes after 08:00 on the start date. Assessments whose outcome is still unknown at the data-extract date are excluded and counted; early-warning assessments (before the deadline) are evaluated separately from overdue ones.
2. **Split by employee** into training, validation, and test sets, so one employee's tasks never appear in more than one set.
3. **Feature pipeline:** prepare only information available at each assessment (for example, task type, department, employee type, intake channel, days until start, time in status, and team workload) in a reproducible pipeline fitted on training data only.
4. **Baselines:** a "never at risk" reference and a transparent days-until-start rule, with its threshold chosen on training data.
5. **Model:** a logistic regression; a second course-taught model may be compared if time allows.
6. **Choose the flag threshold on validation data** to reach the 90% recall target with the fewest flags, and design a human review queue (for example, a second-look tier for cases near the threshold or where the model and rule disagree).
7. **Evaluate on validation:** recall (primary), precision, flags and unique tasks flagged, and ranking measures, compared with the baselines.
8. **Examine errors and groups:** missed at-risk tasks, unnecessary flags, and results by task type, channel, checkpoint, and employee type, marking groups too small for firm conclusions.
9. **Bias and privacy review:** check whether the model's errors fall unevenly across groups such as employee type or department, and confirm that it uses no personal or sensitive information.
10. **Interpret and communicate:** explain which inputs drive the model's suggestions, in terms the coordinator can use, without treating associations as causes.
11. **Evaluate the frozen pipeline, threshold, and review policy once on the test set.**
12. Document risks, limitations, monitoring needs, and next steps in a model card and decision brief.

An optional clustering exploration (for example, grouping tasks by their delay profiles) may be added if it supports the question. The methods build on AIDA 1141 Exercises 04–09, rerun on data version 2. The method choice is to be confirmed with the instructor.

## Planned deliverables

- Analysis notebooks (`analysis/`) and saved results (`outputs/`)
- `report.md`: problem, data, method, evaluation, risks, findings, and next steps
- Model card
- `decision-brief.md`: what the evidence supports, what it does not, and the human-review rule
- Demonstration for the final technical defence

For each analysis included: the question, data version, method, key finding, limitation, and steps to reproduce.

## Checkpoints

| Week | Checkpoint |
|:---|:---|
| 10 (2–6 Nov) | Gate 3: working prototype (bring early project work) |
| 12 (16–20 Nov) | Gate 4: validation evidence; review preliminary findings, errors, risks, and limitations |
| 14 (30 Nov–4 Dec) | Gate 5: release candidate, in-class presentation, peer review, and revision |
| 15 (7–9 Dec) | Gate 6: release readiness and documentation check |
| Final-examination period (14–18 Dec) | Submit, demonstrate, and complete the individual technical defence |

## Boundaries

This project uses only synthetic records and supports a coordinator's review; it does not make onboarding decisions automatically. Its analysis is distinct from the AIDA 2156 and AIDA 2154 final projects, which share the same workflow and data but answer different questions.
