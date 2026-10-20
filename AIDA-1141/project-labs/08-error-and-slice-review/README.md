# AIDA 1141 Project Exercise 08 – Error and Slice Review

## Use-case question

Which validation assessments does the model get wrong or place near its threshold, what do those cases have in common, and does performance differ across operational slices?

## Intended staff decision

The coordinator decides whether to follow up on an onboarding task. This review identifies cases where the model misses risks or creates unnecessary flags, helping reviewers understand where caution is needed.

## Steps completed

1. Loaded the Exercise 06 validation predictions and checked their consistency with Exercise 07.
2. Selected cases from six review groups, including every missed at-risk assessment and examples near the threshold.
3. Compared outcomes with hidden and workload delays using simulation-only audit fields.
4. Compared recall, precision, and flag share across task type, intake channel, checkpoint, and employee type.
5. Documented limited-support results and interpreted the patterns using the course’s error-analysis questions.

## Result

The model missed six at-risk assessments from four tasks, with estimated risks of 0.011–0.123; all six belonged to tasks with hidden delays of 3–6 business days. Among at-risk assessments, it flagged all 52 without hidden delays and 26 of 32 with them (81.2%).

Of the model’s 56 fewer flags compared with the global rule, 54 came from checkpoint 2, where the rule flagged all 108 assessments. Permanent employees had the lowest observed recall, at two of six at-risk assessments, but these represented only three tasks and three employees.

- [Notebook](error_slice_review.ipynb)
- [Error-review cases](outputs/error_review_cases.csv)
- [Delays by outcome](outputs/delays_by_outcome.csv)
- [Recall by hidden delay](outputs/recall_by_hidden_delay.csv)
- [Slice results](outputs/slice_results.csv)
- [Flag difference by group](outputs/flag_difference_by_group.csv)

## Error review and slices

Cases were deliberately selected to illustrate review groups, rather than randomly sampled; some assessments appear in more than one group. Simulation-only fields were added after prediction for analysis and were never model inputs.

All operational slice results are reported. Recall based on fewer than 20 at-risk assessments and precision based on fewer than 20 flagged assessments are marked as having limited support. This reporting rule highlights small denominators, not statistical reliability.

## What the result means

The model’s misses were concentrated in hidden-delay cases, but this association does not establish why individual predictions failed. Most of its reduction in flags came from checkpoint 2.

Slice differences identify questions for further review rather than dependable differences in performance. The 90% recall target applies to early-warning assessments overall, not separately to every slice.

## Limitation

Many slice results depend on few tasks and employees within a small, clustered validation sample of simulated outcomes. Their percentages should not be treated as reliable estimates for real HR workflows.

## Human reviewer action

Review the six missed assessments and the boundary-band examples before setting thresholds and the review policy in Exercise 09.

## Run instructions

Use the project-root `.venv` (Python 3.14.7) with pandas 3.0.6, NumPy 2.5.3, Matplotlib 3.11.2, and ipykernel 7.4.0, installed from the tech guide's package list. Matplotlib is imported by the notebook.

The notebook reads:

- `../06-model-training-and-split/outputs/validation_predictions.csv`
- `../06-model-training-and-split/outputs/model_settings.csv`
- `../07-evaluation-measures/outputs/confusion_matrices_assessments.csv`
- `../02-synthetic-request-records/data/assessments.csv`
- `../02-synthetic-request-records/data/requests.csv`
- `../02-synthetic-request-records/data/simulation_truth.csv`

Run Exercises 06 and 07 first. Open `error_slice_review.ipynb`, select the `.venv` kernel, restart it, and run all cells. Relative paths assume the working directory is this exercise folder.

The notebook creates `outputs/` if needed and overwrites its five output files on each run. It does not refit the model, change thresholds, or evaluate test data.
