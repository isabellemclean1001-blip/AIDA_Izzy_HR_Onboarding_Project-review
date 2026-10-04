# Data Card – Synthetic Onboarding Request Records

## 1. Purpose and intended use

This dataset represents fictional onboarding tasks for the Town of Pinecrest workflow described in the [Exercise 01 problem brief](../01-workflow-question/problem-brief.md). AIDA 1141 will use it to evaluate an at-risk model, and AIDA 2156 will explore request volume, completeness, and processing times. All records are synthetic and are not intended for real HR decisions.

## 2. What the files contain

| File | One row represents | Rows |
|:---|:---|---:|
| `requests.csv` | One onboarding task | 2,064 |
| `status_events.csv` | One workflow event, including status changes and team completion | 8,788 |
| `assessments.csv` | One risk checkpoint for a task | 2,579 |
| `simulation_truth.csv` | Simulation values for a task, excluded from model inputs | 2,064 |
| `requests_with_errors.csv` | One task record, including deliberate errors and duplicate copies | 2,072 |
| `injected_errors.csv` | One deliberately planted error | 31 |

Field definitions and roles are in [data-dictionary.csv](data-dictionary.csv).

## 3. How the data was generated

The `generate_requests.py` script uses only Python’s standard library and a fixed seed of 2026, producing identical files when rerun with the same script and settings. It creates 500 fictional employees with 2–5 tasks each, always including payroll setup and system access. It simulates submitted information, missing or conflicting details, information checks, assignment, and team processing.

Tasks are processed in assignment order. Processing time combines a randomly selected base duration, an additional delay calculated from team workload at assignment, and sometimes a hidden delay. No coordinator follow-up or expediting is simulated.

To regenerate the files, run:

`python3 generate_requests.py`

## 4. Key definitions

- **Deadline:** A task is ready if the team finishes at or before 08:00 on the confirmed start date. Coordinator confirmation may happen later.
- **Calendar:** Business days are Monday–Friday, with no holidays. Working hours are 08:00–16:30, using one fictional fixed local clock without daylight-saving adjustments.
- **Days until start:** Counts weekdays from the assessment date through the day before the start date, including the assessment date. This is a date-based count, not full working days remaining. On the start date it is zero; afterward it is negative.
- **Time in status:** Counts weekdays from the date the current status began through the day before assessment.
- **Checkpoint 1:** Happens when information is complete, before assignment. The status is `open`.
- **Checkpoint 2:** Happens at 08:00 five business days before the start date, only if it falls after checkpoint 1 and the team has not finished. The days-until-start value is always 5.
- **Team workload:** Counts tasks assigned to that team but not yet team-completed at assessment time. Finished tasks awaiting coordinator confirmation are excluded.
- **Conflict rule (a):** An equipment item is listed on a non-equipment task.
- **Conflict rule (c):** A submitted start date differs from the employee’s reference start date in the simulation. This represents a date inconsistency the coordinator would check with the requester.
- **Resolution:** The simulation represents the coordinator resolving issues with the requester. Confirmed start dates and hiring departments contain the resolved values; submitted values are preserved.
- **Missing versus not applicable:** A blank required value represents missing information. `not_applicable` means no equipment item is needed for that task and avoids tools interpreting `N/A` as missing.

## 5. Labels and outcomes

`at_risk` indicates whether a task would finish after the 08:00 deadline without additional intervention. Labels come from simulated completion outcomes, not decisions made by real staff. Because the simulation contains no follow-up intervention, both checkpoints share the same label, which is always the opposite of `ready_by_start`.

Assessments occur before team completion. Assessments at or after the deadline have `past_deadline_at_assessment = True` and are always labelled at risk. Early-warning assessments occur strictly before the deadline and will be evaluated separately; the proposed 90% recall target applies to this group.

When splitting for modelling, keep all of one employee's requests and assessments in the same set. Model inputs should be limited to fields with the role `model_input` in the data dictionary; outcomes, labels, and simulation-only fields must be excluded.

## 6. Dataset summary (seed 2026)

| Measure | Value |
|:---|:---|
| Employees | 500: 264 permanent, 106 temporary, 130 seasonal |
| Tasks per employee | 2: 5 employees · 3: 86 · 4: 249 · 5: 160 |
| Employee start dates | February 23–September 30, 2026; seasonal starts are April–June |
| Request submissions | January 21–September 21, 2026 |
| Team completion dates | January 22–October 1, 2026 |
| Information issues | 136 missing · 115 conflict · 15 both · 1,798 none |
| Assessments | 2,579: 2,064 at checkpoint 1 and 515 at checkpoint 2 |
| At risk – all assessments | 471 of 2,579 (18.3%) |
| At risk – early-warning only | 408 of 2,516 (16.2%) |
| At risk – by checkpoint | Checkpoint 1: 19.1% · checkpoint 2: 15.0% |
| Already-overdue assessments | 63 |
| Tasks not ready by start | 394 of 2,064 (19.1%) |

These percentages describe simulated outcomes, not model performance.

## 7. Simulation assumptions (all invented)

The percentages below are generation probabilities, rather than guaranteed proportions in the output.

| Setting | Value |
|:---|:---|
| Department selection | Parks 22% · Transit 18% · Recreation 18% · Finance 12% · Utilities 15% · Administration 15% |
| Employee type | Parks/Recreation: 35% permanent, 15% temporary, 50% seasonal; other departments: 70%, 25%, 5% |
| Notice | Permanent 8–30 business days · temporary 3–15 · seasonal 2–12 |
| Late submissions | A 3% employee-level probability sets the submission anchor on or after the start date; individual tasks arrive 0–2 business days after that anchor |
| Optional tasks | Orientation 85%; equipment 80% office / 45% field; workplace access 75% field / 45% office |
| Field departments | Parks, Transit, and Utilities; remaining departments use the office settings |
| Base processing | Equipment 3–6 business days · system access 2–4 · payroll 2–5 · workplace access 2–5 · orientation 1–4 |
| Team capacity setting | IT 30 open tasks · Payroll 14 · Facilities 12 · Manager 16 |
| Workload delay | Calculated once at assignment as `max(0, round((open tasks − capacity) / (capacity × 0.5)))` business days |
| Base channel weights | Field: 40% web form, 35% email, 25% phone; office: 65%, 28%, 7% |
| Channel adjustments | Payroll favours web forms, orientation favours email, and workplace access favours phone through task-specific multipliers |
| Missing information | Web form 4% · email 10% · phone 14%; one eligible field is blanked when selected |
| Conflicts | Rule (a): 3% probability for non-equipment tasks; rule (c): 4% probability when the submitted start date is present |
| Hidden delay | 18% probability; 1–6 additional business days, labelled staff absence, backlog, or vendor delay |
| Information resolution | Reply date selected 1–3 business days after submission, with information completion kept after the clarification request |

## 8. Deliberate data-quality errors

Deliberate errors appear only in `requests_with_errors.csv`; the original files remain untouched. The answer key in `injected_errors.csv` identifies each error and its CSV row number, counting the header as row 1.

| Error type | Count |
|:---|---:|
| Duplicate rows | 8 |
| Impossible dates | 5 |
| Misspelled categories | 6 |
| Invalid channel (`fax`) | 4 |
| Extra blanks | 8 |

Designed intake issues in the original data are separate from these planted errors.

## 9. Privacy and safety

No real employee, employer, or City of Red Deer records were used. Records contain fictional IDs rather than names, ages, gender, SIN numbers, banking details, or tax information. Comments in the `requester_comment` field are generic synthetic phrases and are not used as a model input.

## 10. Limitations

- Rates, durations, and department patterns are invented. Differences between task types reflect the generator’s assumptions, not real HR findings.
- No follow-up intervention is simulated, so the data cannot measure whether expediting improves completion.
- The simulation uses one Monday–Friday calendar without holidays, shifts, or separate department schedules.
- Start-date conflicts are identified using the generator’s reference values. A real coordinator would need supporting information or requester confirmation.
- Hidden delay reasons are randomly assigned labels, not detailed simulations of absences, backlogs, or vendor behaviour.
- Checkpoint 2 only includes unfinished tasks, so its records are a selected group rather than a separate sample of all requests.
- Results cannot establish how a model would perform on real onboarding data.
