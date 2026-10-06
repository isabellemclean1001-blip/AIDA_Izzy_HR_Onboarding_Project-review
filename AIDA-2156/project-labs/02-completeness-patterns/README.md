# AIDA 2156 Project Exercise 02 – Completeness Patterns

## Use-case question

Which intake fields are missing, and how do missing-information rates vary by task type and intake channel?

## Intended staff decision

This analysis helps the fictional HR team lead identify where requests arrive with missing information so that clarification and follow-up can be planned.

## Steps completed

1. Loaded the original synthetic `requests.csv` and `assessments.csv` files from AIDA 1141 Exercise 02.
2. Distinguished blanks, `not_applicable` values, and numeric zeros.
3. Counted blanks and `not_applicable` values by field, including the missing-item rate among equipment requests.
4. Compared missing-information rates by intake channel and task type.
5. Created a labelled chart and saved the grouped summary table.
6. Checked assessment fields for zeros, negative values, and blanks.
7. Documented handling choices and limitations.

## Result

Submitted hiring departments were blank in 80 requests (3.9%), and submitted start dates were blank in 67 (3.2%). Equipment items were missing in four requests, representing 1.3% of equipment requests. Missing-information rates varied more across channels—web form 3.8%, email 11.2%, and phone 11.4%—than across task types, which ranged from 7.0% to 8.7%.

- [Notebook](completeness_patterns.ipynb)
- [Missingness by group](outputs/missingness_by_group.csv)
- [Plot](outputs/missingness_plot.png)

## What the result means

Email and phone requests have higher missing-information rates than web forms in this generated dataset. Blanks, `not_applicable`, and zeros have different meanings and were preserved accordingly; conflicting information was not counted as missing unless a required field was also blank.

## Limitation

The channel pattern reflects the generator’s invented missing-information probabilities and cannot establish completeness patterns in real HR intake.

## Human reviewer action

Review whether the simulated missing-information probabilities are reasonable for the fictional municipal workflow before carrying these assumptions into later analysis.

## Run instructions

Use the project-root `.venv` (Python 3.14.7) with pandas 3.0.6, Matplotlib 3.11.2, and ipykernel 7.4.0, installed from the tech guide's package list.

The notebook reads `requests.csv` and `assessments.csv` from:

`../../../AIDA-1141/project-labs/02-synthetic-request-records/data/`

If the files are missing, run `generate_requests.py` from the AIDA 1141 Exercise 02 folder.

Open `completeness_patterns.ipynb`, select the `.venv` kernel, restart it, and run all cells. The relative paths assume the working directory is this exercise folder.

The notebook creates `outputs/` if needed and writes `missingness_by_group.csv` and `missingness_plot.png`. These files are overwritten on each run.
