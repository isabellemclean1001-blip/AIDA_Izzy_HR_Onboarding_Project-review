# AIDA 2156 Project Exercise 01 – Intake Volume Profile

## Use-case question

How many fictional onboarding requests arrive by task type and intake channel?

## Intended staff decision

This analysis helps the fictional HR team lead understand the mix of incoming requests when planning coordinator workload.

## Steps completed

1. Loaded `requests.csv` from AIDA 1141 Exercise 02 and defined one row as one onboarding task.
2. Profiled the dataset, including record counts, unique employees, submission dates, tasks per employee, and missing values in the columns used.
3. Counted requests by task type, intake channel, and task type × channel.
4. Created a labelled stacked bar chart and saved the count table and plot.
5. Considered whether the dataset supports descriptive counts and noted the smaller groups.

## Result

The dataset contains 2,064 tasks for 500 fictional employees. Payroll setup and system access are the most common task types, with 500 requests each, while web forms are the most common channel at 1,096 requests (53.1%). Workplace access has the highest number of phone requests, at 101.

- [Notebook](intake_volume_profile.ipynb)
- [Count table](outputs/intake_counts.csv)
- [Plot](outputs/intake_volume_plot.png)

## What the result means

The counts describe the intake mix within this synthetic workflow. They provide context for later analysis of completeness, processing times, and relationships between task types and channels.

## Limitation

The data is synthetic, so the volumes and channel patterns reflect the generator’s settings rather than real HR intake.

## Human reviewer action

Review whether the task types and intake channels are reasonable for the fictional municipal onboarding workflow.

## Run instructions

Uses the project-root `.venv` (Python 3.14.7) with pandas 3.0.6, Matplotlib 3.11.2, and ipykernel 7.4.0, installed from the tech guide's package list.

The data source, relative to this exercise folder, is:

`../../../AIDA-1141/project-labs/02-synthetic-request-records/data/requests.csv`

If the dataset is missing, run `generate_requests.py` from the AIDA 1141 Exercise 02 folder.

Open `intake_volume_profile.ipynb` in VS Code, select the project `.venv` kernel, and run all cells from the beginning. The relative paths assume the notebook’s working directory is this exercise folder.

The notebook writes `intake_counts.csv` and `intake_volume_plot.png` to `outputs/`.
