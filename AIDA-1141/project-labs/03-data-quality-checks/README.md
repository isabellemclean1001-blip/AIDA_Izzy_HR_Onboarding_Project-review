# AIDA 1141 Project Exercise 03 – Data Quality Checks

## Use-case question

Are the synthetic onboarding request records usable before analysis?

## Intended staff decision

Before relying on request records for risk assessment, staff need to identify which values are valid, which can be repaired, and which still require human review.

## Steps completed

1. Reran `generate_requests.py` from Exercise 02 and confirmed all files and counts matched the data card; Git showed no changes, so the data was reproduced exactly.
2. Loaded the deliberately altered request records and the data dictionary from Exercise 02.
3. Checked ID formats, missing values, invalid categories, impossible and weekend dates, exact duplicates, and conflicting request IDs.
4. Separated designed intake gaps and conflicts from data-quality problems.
5. Compared the findings with the planted-error answer key only after detection.
6. Applied conservative repairs and documented the handling of each finding.
7. Rechecked the cleaned records and compared them with the original synthetic dataset by request ID.

## Result

The checks identified 510 findings: 31 data-quality findings and 479 designed intake findings. All 31 planted errors were detected, with no additional data-quality findings outside the answer key. Of the planted errors, 21 were resolved and 10 remained unresolved.

- [Notebook](data_quality_checks.ipynb)
- [Quality report](outputs/quality_report.csv)
- [Individual findings](outputs/quality_issues.csv)
- [Correction mapping](outputs/correction_mapping.csv)
- [Cleaned requests](outputs/requests_cleaned.csv)

## What the result means

The checks detected all planted problems in this dataset, but some original values could not be recovered without guessing. The cleaned file documents repairs and unresolved issues; later modelling exercises will use the original clean files from Exercise 02.

## Limitation

Detection and repair accuracy could be evaluated because this synthetic dataset has an answer key and an untouched reference file, which would not normally be available for operational data.

## Human reviewer action

Review the 10 unresolved repairs and the correction mapping before using the cleaned records.

## Run instructions

Use the project-root `.venv` (Python 3.14.7) with pandas 3.0.6 and ipykernel 7.4.0, installed from the tech guide's package list, and select it as the notebook kernel.

The notebook reads the following files from Exercise 02:

- `../02-synthetic-request-records/data/requests_with_errors.csv`
- `../02-synthetic-request-records/data/requests.csv`
- `../02-synthetic-request-records/data/status_events.csv`
- `../02-synthetic-request-records/data/injected_errors.csv`
- `../02-synthetic-request-records/data-dictionary.csv`

If the generated data is missing, run `generate_requests.py` from the Exercise 02 folder.

Open `data_quality_checks.ipynb`, select the `.venv` kernel, restart the kernel, and run all cells. The working directory should be this exercise folder. The `outputs/` folder is included in the repository.

The notebook writes four files to `outputs/`: `quality_report.csv`, `quality_issues.csv`, `correction_mapping.csv`, and `requests_cleaned.csv`. These files are overwritten on each run.
