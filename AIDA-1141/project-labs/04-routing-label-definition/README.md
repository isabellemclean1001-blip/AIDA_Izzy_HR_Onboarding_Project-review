# AIDA 1141 Project Exercise 04 – Routing Label Definition

## Use-case question

How does each synthetic assessment receive its at-risk label, and could any selected model input expose the answer?

## Intended staff decision

The coordinator decides whether to follow up or expedite an onboarding task; the label defines the simulated late outcome that the model will try to predict.

## Steps completed

1. Defined the `at_risk` label and distinguished it from the four workflow actions in the label guide.
2. Recomputed the label and overdue flag from timestamps and tested the 08:00 deadline boundary.
3. Checked that selected model inputs exclude labels, outcomes, and simulation-only fields.
4. Independently recomputed days until start and team workload.
5. Inspected strong single-input patterns without treating predictive strength alone as leakage.
6. Documented edge cases and their handling.
7. Created a deliberately varied labelled sample with audit explanations.

## Result

The dataset contains 2,579 assessments, with 471 labelled at risk. The early-warning group contains 2,516 assessments, including 408 at risk (16.2%); the proposed 90% recall target applies to this group, while the 63 at-or-after-deadline assessments are reported separately. All nine implemented checks passed, and a 20-example labelled sample was created.

- [Label guide](label-guide.md)
- [Notebook](label_definition.ipynb)
- [Labelled sample](outputs/labelled_sample.csv)
- [Leakage checks](outputs/leakage_checks.csv)
- [Single-input risk rates](outputs/single_input_risk_rates.csv)

## What the result means

The checks support a consistent label definition and provide evidence that selected inputs respect the assessment-time boundary. Strong predictors such as days until start are legitimate inputs, making comparison with simple baselines in Exercise 05 important.

## Limitation

Labels come from simulated outcomes based on invented assumptions, rather than verified decisions from real HR staff.

## Human reviewer action

Review the labelled sample and edge cases to assess whether predicting missed start deadlines would support the coordinator’s follow-up decision.

## Run instructions

Use the project-root `.venv` (Python 3.14.7) with pandas 3.0.6, NumPy 2.5.3, and ipykernel 7.4.0, installed from the tech guide's package list.

The notebook reads these files from `../02-synthetic-request-records/`:

- `data/requests.csv`
- `data/assessments.csv`
- `data/status_events.csv`
- `data/simulation_truth.csv`
- `data-dictionary.csv`

Open `label_definition.ipynb`, select the `.venv` kernel, restart it, and run all cells. The relative paths assume the working directory is this exercise folder.

The notebook creates `outputs/` if needed and writes `labelled_sample.csv`, `leakage_checks.csv`, and `single_input_risk_rates.csv`. These files are overwritten on each run.
