# AIDA 1141 Project Exercise 02 – Synthetic Request Records

## Use-case question

Can a documented synthetic dataset represent the Town of Pinecrest onboarding workflow well enough to support evaluating which tasks are at risk of missing the employee’s start date?

## Intended staff decision

The HR onboarding coordinator reviews a task’s risk flag and decides whether to follow up or expedite it; this dataset represents the information available to support that decision.

## Steps completed

1. Designed the fields and documented their meanings, allowed values, and roles in the data dictionary.
2. Created a seeded Python generator that simulates onboarding tasks without follow-up intervention.
3. Generated six CSV files, including a separate version with deliberate data-quality errors and an answer key.
4. Checked label consistency, assessment timing, completion confirmations, error-row references, and repeat-run reproducibility.
5. Documented the generation process, assumptions, results, and limitations in the data card.

## Result

The generator produced records for 500 fictional employees, 2,064 onboarding tasks, and 2,579 assessments. Of all assessments, 18.3% were labelled at risk, compared with 16.2% of early-warning assessments. These are simulated outcome rates, not model performance.

- [Data card](data-card.md)
- [Data dictionary](data-dictionary.csv)
- [Generator](generate_requests.py)
- [Generated data](data/)

## What the result means

The dataset provides a starting point for AIDA 1141 Exercise 03’s data-quality checks and later model evaluation. AIDA 2156 Exercise 01 will use the same request records to explore volume by task type and intake channel.

## Limitation

All rates and processing durations are invented assumptions, so the patterns reflect the generator’s settings rather than real HR findings.

## Human reviewer action

Review the simulation assumptions in Section 7 of the data card and assess whether they are reasonable for the fictional municipal onboarding workflow.

## Run instructions

Python 3 is required. The generator uses only the standard library, so no additional packages are needed.

From this exercise folder, run:

`python3 generate_requests.py`

The script writes six CSV files to `data/` and prints a summary. Running the same script and settings with seed 2026 reproduces the same files. Existing generated files in `data/` are overwritten.
