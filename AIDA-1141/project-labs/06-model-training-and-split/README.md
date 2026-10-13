# AIDA 1141 Project Exercise 06 – Model Training and Split

## Use-case question

Can a logistic regression model identify at-risk early-warning assessments with at least 90% recall while flagging fewer assessments than the Exercise 05 days-until-start rule?

## Intended staff decision

The coordinator decides whether to follow up or expedite an onboarding task. The model suggests which assessments need review, and this exercise compares its suggested review volume with the simple rules.

## Steps completed

1. Reused the fixed employee-level split from Exercise 05 and checked its consistency.
2. Selected nine documented model inputs, excluded `responsible_team` because it duplicates `task_type`, and checked feature roles.
3. Chose a flag threshold using five-fold cross-validation grouped by employee within training data.
4. Refitted the pipeline on all training early-warning assessments and saved the model, threshold, settings, coefficients, and checks.
5. Compared the model with the saved Exercise 05 rules on validation early-warning assessments.

## Result

All 16 data, split, and leakage checks passed, and the reapplied rules matched Exercise 05’s validation predictions. The selected threshold was approximately 0.1254, achieving 90.2% out-of-fold training recall; its full-precision value is saved in the settings.

On validation, the model achieved 92.9% recall (78 of 84) and 45.1% precision, flagging 173 of 505 assessments (34.3%) across 129 tasks. Compared with the global rule, it flagged 56 fewer assessments and 42 fewer unique tasks but missed two additional at-risk assessments.

- [Notebook](model_training.ipynb)
- [Feature list](outputs/feature_list.csv)
- [Leakage checks](outputs/leakage_checks.csv)
- [Model settings](outputs/model_settings.csv)
- [Coefficients](outputs/coefficients.csv)
- [Numeric scaling](outputs/numeric_scaling.csv)
- [Cross-validation folds](outputs/cv_fold_summary.csv)
- [Training out-of-fold predictions](outputs/train_out_of_fold_predictions.csv)
- [Model vs baselines](outputs/model_vs_baselines.csv)
- [Validation predictions](outputs/validation_predictions.csv)
- [Saved model](outputs/model.joblib)

## Split, features, and leakage checks

The model uses the same employee split as Exercise 05 and nine documented assessment-time inputs. Scaling, encoding, and fitting occur within the pipeline using training rows only, and the threshold is selected without validation data.

Test data is used only for split-consistency checks. The checks provide evidence that the workflow respects the training boundary, rather than proof that all possible leakage is absent.

## What the result means

On this validation split, the model met the recall target with fewer flags while missing two more at-risk assessments. Exercise 07 will examine this trade-off and the consequences of different errors.

Days until start had the largest absolute coefficient among the standardized numeric inputs (−5.17 per standard deviation, about 7.5 business days). Coefficients describe associations within the simulation, not causes of delays.

## Limitation

The comparison uses a small validation sample of simulated outcomes, with related assessments from the same tasks and employees. It does not establish reliable improvement on new or real onboarding data.

## Human reviewer action

Review the additional missed at-risk assessments to judge whether the reduction in flags is an acceptable trade-off before reconsidering thresholds in Exercise 09.

## Run instructions

Use the project-root `.venv` (Python 3.14.7) with scikit-learn 1.9.1, pandas 3.0.6, NumPy 2.5.3, SciPy 1.18.1, joblib 1.6.0, and ipykernel 7.4.0. scikit-learn is listed in the tech guide; SciPy and joblib were installed with it. Package versions are also recorded in `model_settings.csv`.

The notebook reads:

- `../02-synthetic-request-records/data/requests.csv`
- `../02-synthetic-request-records/data/assessments.csv`
- `../02-synthetic-request-records/data-dictionary.csv`
- `../05-simple-routing-baseline/outputs/employee_split.csv`
- `../05-simple-routing-baseline/outputs/rule_thresholds.csv`
- `../05-simple-routing-baseline/outputs/baseline_predictions_validation.csv`

Run Exercise 05 first. Open `model_training.ipynb`, select the `.venv` kernel, restart it, and run all cells. Relative paths assume the working directory is this exercise folder.

The notebook creates `outputs/` if needed and overwrites its ten output files on each run. Load `model.joblib` only in a trusted environment with matching package versions.
