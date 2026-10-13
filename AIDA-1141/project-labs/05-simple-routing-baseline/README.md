# AIDA 1141 Project Exercise 05 – Simple Routing Baseline

## Use-case question

How well do simple, transparent rules identify early-warning assessments at risk of missing the start-date deadline, compared with a majority baseline?

## Intended staff decision

The coordinator decides whether to follow up or expedite an onboarding task. These baselines suggest which tasks may need attention and provide a comparison point for the later model.

## Steps completed

1. Checked the data against the Exercise 02 and 04 documentation.
2. Created and saved an employee-level split, approximately 60/20/20, stratified by employee type and late-task count.
3. Selected rule thresholds on training early-warning assessments using a 90% recall target.
4. Compared four baselines on validation data and reported overdue assessments separately.
5. Saved predictions and documented why the baselines provide a useful starting point.

## Result

The split contains 299 training, 103 validation, and 98 test employees. The global rule flags assessments with seven or fewer business days remaining and achieved 95.2% validation recall and 34.9% precision, flagging 229 of 505 early-warning assessments (45.3%) across 171 of 397 tasks.

The employee-type rule, with thresholds of nine, seven, and six business days for permanent, temporary, and seasonal employees, achieved 94.0% recall with the same assessment flag count and 175 tasks flagged, showing no improvement on this validation split. The majority baseline achieved 83% accuracy while catching no at-risk assessments, and both days rules flagged all 21 overdue validation assessments.

- [Notebook](simple_baseline.ipynb)
- [Employee split](outputs/employee_split.csv)
- [Split summary](outputs/split_summary.csv)
- [Rule thresholds](outputs/rule_thresholds.csv)
- [Baseline comparison](outputs/baseline_comparison.csv)
- [Validation predictions](outputs/baseline_predictions_validation.csv)

## Split and evaluation plan

Each employee’s tasks and assessments remain in one split. Late-task counts are used only to improve split balance, never as rule or model inputs.

Training data is used to choose thresholds, while validation supports comparisons in Exercises 05–09. Test data is reserved for one final evaluation after the model and review threshold are fixed in Exercise 09. Reruns stop if the rebuilt split differs from the saved allocation.

## Why this is a fair starting point

The rules use documented inputs available at assessment time and can be explained without a model. Thresholds are selected on training data, with performance compared on separate validation employees.

Later models will use the same split, early-warning group, and recall target. The days rule provides a useful comparison because days until start is strongly related to the simulated outcome; beating the majority baseline alone would provide limited evidence of improvement.

## What the result means

Both days rules met the validation recall target, but flagged about 45% of early-warning assessments, with roughly one in three flags identifying an at-risk assessment. Exercise 06 will examine whether a model maintains at least 90% validation recall while reducing assessment and unique-task flags relative to the global rule.

## Limitation

The results describe simulated outcomes in a small validation sample with related assessments from the same tasks and employees. Small differences between baselines should therefore be interpreted cautiously, and the permanent-employee threshold rests on 26 at-risk assessments from 12 employees and may be unstable.

## Human reviewer action

Review whether the suggested review volume would be manageable for the fictional coordinator, considering both assessment flags and unique tasks flagged.

## Run instructions

Use the project-root `.venv` (Python 3.14.7) with pandas 3.0.6, NumPy 2.5.3, and ipykernel 7.4.0, installed from the tech guide's package list.

The notebook reads these files from `../02-synthetic-request-records/`:

- `data/requests.csv`
- `data/assessments.csv`
- `data-dictionary.csv`

Open `simple_baseline.ipynb`, select the `.venv` kernel, restart it, and run all cells. Relative paths assume the working directory is this exercise folder.

The notebook creates `outputs/` if needed. It writes `employee_split.csv` on the first run; later runs confirm the rebuilt split matches the saved file and stop if it differs. The other four output files are overwritten on each run.
