# Data Card – Synthetic Onboarding Request Records (Version 2)

> **Draft – version 2 candidate, awaiting instructor approval.**

## 1. Purpose and intended use

This dataset represents fictional onboarding tasks for the Town of Pinecrest workflow described in the [Exercise 01 problem brief](../01-workflow-question/problem-brief.md). AIDA 1141 uses it to clean records, define labels, and evaluate an at-risk model; AIDA 2156 uses it to explore request volume, completeness, timing, and processing steps. All records are synthetic and are not intended for real HR decisions.

Version 2 is a proposed replacement following instructor feedback that the data should reflect messier real-world records. Version 1 remains unchanged while this candidate is reviewed; it is preserved under the Git tag `data-v1`.

## 2. What the files contain

The files are in two folders with different purposes.

**`data/` – the system export used for analysis.** It represents what the HR system would export on the extract date, including recording problems in `requests.csv`.

| File | One row represents | Rows |
|:---|:---|---:|
| `data/requests.csv` | One onboarding task as exported, including duplicate rows | 4,386 (4,364 distinct tasks) |
| `data/status_events.csv` | One workflow event recorded by the extract date | 18,491 |
| `data/assessments.csv` | One risk checkpoint recorded by the extract date | 5,413 |

**`evaluation_only/` – never used to clean, fill, or model the analysis data.** These files record what the simulation knows but the system export does not, so cleaning and other choices can be evaluated afterwards.

| File | One row represents | Rows |
|:---|:---|---:|
| `evaluation_only/data_issues.csv` | One recording problem added to `requests.csv`, with its recorded and true value | 513 |
| `evaluation_only/simulation_truth.csv` | Simulation values for one task, including its full future completion time | 4,364 |

Field definitions and roles are in [data-dictionary.csv](data-dictionary.csv).

## 3. How the data was generated

The `generate_requests.py` script uses only Python's standard library and a fixed seed of 2026. The same seed, settings, code, and Python version reproduce the same files.

The generator works in two layers, similar to a real system:

1. **What happened.** It simulates 1,150 fictional hires with start dates from March 2025 to December 2026, their onboarding tasks, information checks, assignment, and team processing, with no coordinator follow-up or expediting.
2. **What was recorded.** It exports the records as the system would show them at **17:00 on Tuesday 29 September 2026**. Requests submitted later are not yet in the system, unfinished requests have no completion time, and `requests.csv` receives recording problems such as inconsistent categories, blanks, duplicates, and invalid dates.

To regenerate the files, run:

`python3 generate_requests.py`

## 4. Key definitions

- **Extract date:** 17:00 on Tuesday 29 September 2026. Workflow events and assessments are included only up to the extract timestamp. Future planned start dates may appear, and recording errors can introduce invalid or future-dated values.
- **Calendar:** Business days are Monday–Friday, excluding the simulated office closure dates observed by the fictional Town of Pinecrest. These dates are based on common Alberta holidays, including Heritage Day and the National Day for Truth and Reconciliation, and are listed in `generate_requests.py`. They are not an official calendar. Working hours are 08:00–16:30, using one fictional fixed local clock without daylight-saving adjustments.
- **After-hours submissions:** Requesters can submit web forms and emails in the evening, early morning, on weekends, or on closure dates. Coordinators and teams work only during working hours on business days.
- **Information check:** A coordinator checks a complete request immediately if it arrives during working hours, otherwise at the start of the next working day. Requests with missing or conflicting information are completed once the requester replies.
- **Confirmed values:** `confirmed_start_date` and `hiring_department` hold the values resolved by the information check. They are blank until that check is complete.
- **Deadline:** A task is ready if the team finishes at or before 08:00 on the confirmed start date. Coordinator confirmation may happen later.
- **Days until start:** Counts business days from the assessment date through the day before the start date, including the assessment date. On the start date it is zero; afterward it is negative.
- **Time in status:** Counts business days from the date the current status began through the day before assessment.
- **Checkpoint 1:** Happens when information is complete, before assignment. The status is `open`.
- **Checkpoint 2:** Happens at 08:00 five business days before the start date, only if it falls after checkpoint 1 and the team has not finished.
- **Team workload:** Counts other tasks for the same team assigned strictly before the timestamp and completing strictly after it. Tasks assigned or completed at the same timestamp are excluded. The same rule is used in the simulation and in `assessments.csv`.
- **Status at extract:** The status after the request's latest event recorded by the extract, using the same rules as `status_events.csv`. A team-finished task awaiting coordinator confirmation remains `in_progress` with `team_completed_at` filled.
- **Conflict rule (a):** An equipment item is listed on a non-equipment task.
- **Conflict rule (c):** A submitted start date differs from the employee's reference start date in the simulation.
- **Missing versus not applicable:** `not_applicable` means no equipment item is needed for that task. Blank fields may represent unresolved intake information, a workflow step not yet reached, an unknown outcome at extraction, or an injected recording problem. Their meaning depends on the field and process status; they are not all cleaning errors.

## 5. Labels and outcomes

`at_risk` indicates whether a task would finish after the 08:00 deadline without additional intervention. At the extract date, each task falls into one of three groups:

| Situation at the extract | `ready_by_start` | `at_risk` | Eligible for modelling |
|:---|:---|:---|:---|
| Team completed | True or False from the completion time | Opposite of `ready_by_start` | Potentially – requires an assessment and usable assessment-time inputs |
| Unfinished, deadline already passed | False (known to have missed it) | True | Potentially – requires an assessment and usable assessment-time inputs |
| Unfinished, deadline still ahead or start date not yet confirmed | Blank (unknown) | Blank (unknown) | No |

Unknown outcomes are never filled in. The simulation's future completion times are kept only in `evaluation_only/simulation_truth.csv` and must not be used to label, clean, or model the analysis data.

Because no follow-up is simulated, both checkpoints of one task share the same label. Assessments at or after the deadline have `past_deadline_at_assessment = True` and are always labelled at risk when the outcome is known. Early-warning assessments occur strictly before the deadline and are evaluated separately; the proposed 90% recall target applies to labelled early-warning assessments, with any exclusions documented.

When splitting for modelling, keep all of one employee's requests and assessments in the same set. Model inputs should be limited to fields with the role `model_input` in the data dictionary, after cleaning.

## 6. Dataset summary (seed 2026)

| Measure | Value |
|:---|:---|
| Employees with requests in the export | 1,073 of 1,150 simulated: 572 permanent, 227 temporary, 274 seasonal |
| Tasks per employee (in the export) | 1: 1 employee · 2: 17 · 3: 195 · 4: 556 · 5: 304 |
| Employee start dates (confirmed) | 3 March 2025 – 2 December 2026; seasonal starts April–June 2025 (122) and 2026 (152) |
| Request submissions | 6 January 2025 – 29 September 2026 |
| Submitted outside working hours | 656 tasks |
| Team completion dates | 8 January 2025 – 29 September 2026 |
| Information issues | 282 missing · 269 conflict · 18 both · 3,795 none |
| Status at extract | 4,313 complete · 45 in progress · 5 open · 1 waiting for information |
| Readiness at extract | 3,402 ready · 917 not ready · 45 unknown |
| Assessments | 5,413: 4,363 at checkpoint 1 and 1,050 at checkpoint 2; 49 with an unknown outcome |
| At risk – labelled assessments | 1,140 of 5,364 (21.3%) |
| At risk – early-warning only | 949 of 5,173 (18.3%) |
| Already-overdue assessments | 191 |

These percentages describe simulated outcomes, not model performance.

## 7. Simulation assumptions (all invented)

The percentages below are generation probabilities, rather than guaranteed proportions in the output.

| Setting | Value |
|:---|:---|
| Hires and start dates | 1,150 hires; start dates 3 March 2025 – 18 December 2026; seasonal hires start April–June of either year |
| Department selection | Parks 22% · Transit 18% · Recreation 18% · Finance 12% · Utilities 15% · Administration 15% |
| Employee type | Parks/Recreation: 35% permanent, 15% temporary, 50% seasonal; other departments: 70%, 25%, 5% |
| Notice | Log-normal business days before the start date, median 18 permanent · 10 temporary · 8 seasonal, clamped to 1–60 |
| Late submissions | 4% employee-level probability that the submission anchor falls on or after the start date; after-hours timing can shift individual submissions, so this does not guarantee which requests arrive late |
| System start | No request is submitted before 6 January 2025 |
| Optional tasks | Orientation 85%; equipment 80% office / 45% field; workplace access 75% field / 45% office |
| After-hours submissions | Web form 22% · email 12% · phone 0%; evening 55%, early morning 15%, weekend or closure date 30% |
| Base processing | Equipment 3–6 business days · system access 2–4 · payroll 2–5 · workplace access 2–5 · orientation 1–4 |
| Extra processing | 25% chance of additional days from a rounded exponential draw with an underlying mean of 2 (so the added days can be zero); 2% chance of being stuck for 15–30 extra business days |
| Team capacity | IT 32 · Payroll 16 · Facilities 13 · Manager 17 tasks; reduced to 70% in July and August; Payroll at 60% from 3 November to 19 December 2025; IT at 70% from 2 February to 13 March 2026 |
| Workload delay | Calculated once at assignment as `max(0, round((other tasks − capacity) / (capacity × 0.5)))` business days, using the capacity on the assignment date |
| Hidden delay | 18% probability; 1–6 additional business days, labelled staff absence, backlog, or vendor delay |
| Channels | Field: 40% web form, 35% email, 25% phone; office: 65%, 28%, 7%; task-specific multipliers favour web forms for payroll, email for orientation, and phone for workplace access |
| Missing information at intake | Web form 4% · email 10% · phone 14% |
| Conflicts | Rule (a): 3% for non-equipment tasks; rule (c): 4% when the submitted start date is present |
| Information resolution | Reply 1–4 business days after the clarification request |

**Calibration.** Team capacities, notice periods, and the extra-processing rate were adjusted from an earlier draft whose late rate was much higher, as a judgement about plausibility for this fictional workflow; there is no external benchmark, and the earlier draft runs were not saved. The adjustments were made before any model was trained and were not chosen to produce a particular model score.

## 8. Recording problems in `requests.csv`

Only `requests.csv` receives recording problems. `status_events.csv` and `assessments.csv` are accurate by construction, so they can serve as trusted sources for documented repairs; for example, a corrupted `submitted_at` can be recovered from the request's `submitted` event.

| Problem | Count | Fields |
|:---|---:|:---|
| Category variant (case, spelling, abbreviation) | 262 | Task type, responsible team, departments, employee type, channel |
| Missing value | 132 | Employee type, intake channel, confirmed hiring department (44 each) |
| Extra whitespace | 87 | The same category fields |
| Exact duplicate row | 22 | Whole row |
| Impossible date (for example, 2026-02-29) | 6 | Submission time or submitted start date |
| Year typo (for example, 2062) | 4 | Submission time |

These are separate from the designed intake issues (missing or conflicting submitted information), which are part of the simulated workflow.

**Using the answer key.** `evaluation_only/data_issues.csv` lists every recording problem with its row in the raw export, the recorded value, and the true value. Cleaning must use documented rules and the records in `data/`, never the answer key. Afterwards, the key can measure how many problems were detected and repaired:

1. Remove exact duplicates first. A duplicate copy can appear before or after its original and inherits any problem in it; the key logs field problems against the original row only.
2. Then compare field problems by `request_id` and field, not by row number. Row numbers are for auditing the raw export.
3. Values with no trusted source, such as a missing intake channel, should remain unresolved rather than guessed.

## 9. Privacy and safety

No real employee, employer, or City of Red Deer records were used. Records contain fictional IDs rather than names, ages, gender, SIN numbers, banking details, or tax information. Comments in the `requester_comment` field are generic synthetic phrases and are not used as a model input.

## 10. Limitations

- Rates, durations, capacities, and closure dates are invented. Differences between task types, teams, or periods reflect the generator's assumptions, not real HR findings.
- No follow-up intervention is simulated, so the data cannot measure whether expediting improves completion.
- Team capacity is evaluated once at assignment; staffing changes during processing do not alter that task's duration.
- Two simulated spring periods can show whether a pattern recurs within this simulation, but cannot establish real seasonality or a persistent trend.
- Recording problems are limited to `requests.csv` and to the kinds listed in section 8; real systems can contain other kinds of record problems.
- Start-date conflicts are identified using the generator's reference values. A real coordinator would need supporting information or requester confirmation.
- Hidden delay reasons are randomly assigned labels, not detailed simulations of absences, backlogs, or vendor behaviour.
- Checkpoint 2 only includes unfinished tasks, so its records are a selected group rather than a separate sample of all requests.
- Completed-only duration summaries exclude unfinished requests and may underrepresent longer processing times. Unknown outcomes are excluded from modelling, so the labelled subset may differ from all submitted requests.
- Results cannot establish how a model would perform on real onboarding data.

## 11. Version history

| Version | Summary | Where |
|:---|:---|:---|
| 1 | 500 hires in 2026; no closures or after-hours activity; every request complete; deliberate errors only in a separate copy | Git tag `data-v1` |
| 2 | Continuous hiring from 2025; closure dates and after-hours submissions; extract date with unfinished requests; recording problems in the main export with an evaluation-only answer key | Branch `messy-data-v2` (candidate for instructor approval) |
