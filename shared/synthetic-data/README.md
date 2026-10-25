# Synthetic Data – Version 2

This folder holds **data version 2**, used for the three final projects. It was created after instructor feedback that version 1 was too clean, and reviewed by the instructor before use.

**Version 1 is unchanged.** The project exercises submitted earlier used version 1, which stays in their original folders and under the Git tag `data-v1`:

- Requests: `AIDA-1141/project-labs/02-synthetic-request-records/`
- Kit cards: `AIDA-2154/project-labs/01-synthetic-image-specification/`

Every result should state its data version, so version 1 and version 2 results are never mixed.

## What is here

| Folder | Contents |
|:---|:---|
| `requests/` | Request generator, the messy system export (`data/`), the evaluation-only answer key and simulation values (`evaluation_only/`), data card, and data dictionary |
| `cleaning/` | Shared cleaning rules (`clean_requests.py`, version 1.0), the script that makes the official cleaned file, and its output with a record of how it was made |
| `kit-cards/` | Kit-card generator, 600 card images, labels, reference drawings, and a README with field definitions |
| `checks/` | Consistency checks, the cleaning evaluation, and a training-only segmentation pilot, with saved results in `checks/results/` |

## How to reproduce

From the repository root, using the project `.venv` (Python 3.14.7 with pandas, NumPy, Pillow, and opencv-python), run in this order:

```
python shared/synthetic-data/requests/generate_requests.py
python shared/synthetic-data/cleaning/make_cleaned.py
python shared/synthetic-data/kit-cards/generate_kit_cards.py
python shared/synthetic-data/checks/check_requests.py
python shared/synthetic-data/checks/check_cards.py
```

Each step uses fixed seeds; the same settings, code, input files, and package versions reproduce the same files.

## Rules for using this data

- Analyses use `requests/data/` (raw) or `cleaning/output/requests_cleaned.csv` (cleaned), never `requests/evaluation_only/`. The answer key and simulation values exist only to evaluate choices afterwards.
- Unknown outcomes at the extract date stay unknown; they are never filled from the simulation.
- Values with no trusted source stay unresolved after cleaning rather than being guessed.
- For the kit cards, keep the test split out of development decisions, and treat visibility as a separate human-review question from label correctness.

See `requests/data-card.md`, `requests/data-dictionary.csv`, and `kit-cards/README.md` for definitions, assumptions, and limitations.
