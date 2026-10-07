# Label Guide – Onboarding Task Follow-Up

## 1. What is being labelled

Each row represents one assessment of one onboarding task at checkpoint 1 or checkpoint 2. A task can have up to two assessments, and one fictional employee can have several tasks.

## 2. The label: `at_risk`

`at_risk = True` means the team finishes the task after 08:00 on the confirmed start date. `False` means it finishes at or before that deadline.

Labels come from the simulated completion outcomes produced by the documented generator rules, not real staff decisions. No follow-up or expediting is simulated, so the label represents the outcome without additional intervention. Both checkpoints for a task share the same label, which is the opposite of `ready_by_start`.

## 3. Routing categories and who decides

The model predicts risk, rather than all four workflow actions. Its prediction supports the coordinator’s decision; it does not automatically trigger an action.

| Next step | Decided by | Relationship to the label |
|---|---|---|
| Send to responsible team | Routing rule; coordinator confirms | Responsible-team routing is separate from the risk label |
| Request missing information | Information checks; coordinator confirms and requests clarification | Resolved before checkpoint 1 |
| Follow up / expedite | Model suggests; coordinator decides | A predicted `at_risk = True` supports this action |
| Coordinator review | Low-confidence flag or unusual circumstances | Confidence handling will be defined in Exercise 09 |

A predicted `False` supports proceeding normally, but the coordinator can still follow up when other information warrants it.

## 4. Evaluation groups

**Early-warning assessments** occur before the 08:00 start deadline. There are 2,516 assessments in this group, with 408 labelled at risk (16.2%). The proposed 90% recall target applies to this group only.

**Already-overdue assessments** occur at or after the deadline. All 63 are labelled at risk because assessments occur before team completion. They are reported separately because recognizing an existing delay is different from predicting one early.

These percentages describe reference labels, not model performance.

## 5. Edge cases

- **Already overdue:** The task is unfinished at or after the deadline. Staff need to address the delay, but the assessment does not count toward early-warning recall.
- **Completion exactly at 08:00:** The task counts as ready. The constructed boundary test checks 07:59, 08:00, and 08:01, with expected risk labels of False, False, and True.
- **Information issue at intake:** This records a previous issue, not information still missing during assessment. Clarification is complete before checkpoint 1.
- **Checkpoint 2:** Only tasks still unfinished five business days before the start date receive this assessment. Results describe that selected group.
- **Late despite substantial lead time:** Workload, processing duration, and hidden delays can contribute. Lead time alone does not establish the cause.

## 6. Leakage safeguards

Model inputs are limited to fields assigned the `model_input` role in the data dictionary and known at assessment time. Labels, completion outcomes, the overdue flag, simulation-only values, and audit explanations are excluded.

The notebook checks label consistency, the deadline boundary, assessment timing, and the exclusion of outcome fields. It also independently recomputes days until start and team workload. The results are recorded in `outputs/leakage_checks.csv`.

Strong predictors are not automatically leakage. Days until start and employee type are available at assessment time, and their relationships with lateness reflect the simulation’s assumptions. Simple baselines will test whether a more complex model adds value.

These checks provide evidence against leakage but do not establish that all possible leakage is absent. Later data splits will keep every request and assessment for one fictional employee together.

## 7. Label-quality limits

The labels reflect simulated outcomes based on invented processing times, workload rules, and delay probabilities. They are not verified decisions from an actual HR team.

Hidden delays create uncertainty because the model cannot observe every factor affecting completion. They do not make the outcome labels incorrect. Results assess tasks within this fictional simulation and cannot establish performance on real onboarding records.