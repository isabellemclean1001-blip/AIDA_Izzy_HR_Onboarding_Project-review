# Version 2 Candidate Data – Awaiting Instructor Approval

> **Status: candidate for review.** Nothing here has been used to rerun or resubmit any exercise. Version 1 is unchanged on the `main` branch and preserved under the Git tag `data-v1`. This folder and the files listed below exist only on the `messy-data-v2` branch.

## Why there is a version 2

Instructor feedback was that the synthetic data was too clean for the vision, machine-learning, and EDA work. Version 2 proposes messier but still documented and reproducible data for two generators:

1. **Request records** (AIDA 1141 and AIDA 2156) – a realistic system export with recording problems, office closures, after-hours submissions, and requests still unfinished when the data was extracted.
2. **Kit-card images** (AIDA 2154) – continuous variation, two drawing styles per item, small rotations, background objects, and mild scan-like degradation.

The aim is plausible data that requires real cleaning and method choices, not data tuned to make any method fail. Settings were chosen before any model or method results were examined, and pilot results are reported as they came out.

## What changed, at a glance

| | Version 1 | Version 2 candidate |
|:---|:---|:---|
| Requests | 2,064 tasks for 500 hires in 2026 | 4,364 tasks for 1,073 hires (of 1,150 simulated), January 2025 – extract on 29 September 2026 |
| Calendar | Monday–Friday, no closures, every timestamp within 08:00–16:30 | Simulated office closure dates; 656 requests submitted outside working hours |
| Outcomes | Every request complete | 45 requests have an unknown outcome at the extract and are not eligible for modelling |
| Recording problems | Only in a separate copy of the data | In the main export: 513 logged problems (category variants, extra spaces, blanks, 22 duplicate rows, invalid dates), with an evaluation-only answer key |
| Kit cards | 500 cards; 3 sizes × 3 contrasts, so 45 distinct icon appearances; flat background | 600 cards; continuous size and contrast; 2 development styles per item; ±12° rotation; 352 background objects; paper tint, lighting gradient, noise, blur, JPEG compression |
| Unknown kit expectations | `device_unknown` flag kept the other items' expectations | The same idea, made explicit per item with `expectation_known_<item>` flags |

## Files on this branch

| Path | What it is |
|:---|:---|
| `AIDA-1141/project-labs/02-synthetic-request-records/generate_requests.py` | Request generator, version 2 candidate |
| `AIDA-1141/project-labs/02-synthetic-request-records/data/` | The messy system export used for analysis |
| `AIDA-1141/project-labs/02-synthetic-request-records/evaluation_only/` | Answer key and simulation values; never used to clean, fill, or model the analysis data |
| `AIDA-1141/project-labs/03-data-quality-checks/clean_requests.py` | Shared cleaning code; the revised Exercise 03 and the card generator both use this one implementation |
| `candidate-v2/make_provisional_cleaned.py` | Makes the provisional cleaned file for this review |
| `candidate-v2/provisional/` | Provisional cleaned requests and a record of how they were made (source fingerprints, cleaning version, unresolved fields) |
| `AIDA-2154/project-labs/01-synthetic-image-specification/generate_kit_cards.py` | Kit-card generator, version 2 candidate |
| `AIDA-2154/project-labs/01-synthetic-image-specification/images/`, `manifest.csv`, `icon_instances.csv`, `reference_icons/`, `outputs/` | Candidate cards, labels, reference drawings, example sheet, and generation record |
| `candidate-v2/pilot/` | Check and pilot scripts with their saved results |
| `candidate-v2/requests-data-card-draft.md` | Draft data card for the request records |

The exercise READMEs, data dictionaries, label guides, and notebooks on this branch still describe version 1. They will be updated, and the exercises rerun, only after approval.

## How to reproduce

From the repository root, using the project `.venv` (Python 3.14.7 with pandas, NumPy, Pillow, and opencv-python):

```
cd AIDA-1141/project-labs/02-synthetic-request-records && python generate_requests.py && cd -
python candidate-v2/make_provisional_cleaned.py
cd AIDA-2154/project-labs/01-synthetic-image-specification && python generate_kit_cards.py && cd -
python candidate-v2/pilot/check_requests.py
python candidate-v2/pilot/check_cards.py
```

Each generator uses seed 2026; the same seed, settings, code, input files, and package versions reproduce the same files.

## Request records: key design points

- **Extract:** the export represents the HR system at 17:00 on Tuesday 29 September 2026. Workflow events and assessments stop at that moment; future planned start dates can appear.
- **Outcome rule:** completed → known; unfinished with the deadline passed → known to have missed it; unfinished with the deadline still ahead, or with the start date not yet confirmed → unknown. Unknown outcomes are never filled from the simulation.
- **Only `requests.csv` has recording problems.** Status events and assessments are accurate by construction and can serve as trusted sources for documented repairs.

## Kit cards: key design points

- **Expected items** come from the provisional cleaned requests. Items whose expectation cannot be established are marked unknown and never treated as "not needed".
- **Styles:** all development styles appear in each split; one additional style per item is reserved for an Exercise 07 robustness test and is never drawn here. The test split therefore measures new arrangements and image conditions with familiar styles, not unseen styles.
- **Boxes** are tight around each rotated drawing's non-transparent pixels, calculated before blur, noise, and compression.
- **No overlap:** drawn objects stay at least 14 pixels apart.
- **Size and contrast bands** (small/medium/large, low/medium/high) are recorded for slice analysis.
- **Provisional input:** after approval, the generator will read the official Exercise 03 output, and the cards will be regenerated and revalidated.

## Checks (saved in `candidate-v2/pilot/`)

**Request records (`request_checks.csv`, all passed):** answer key matches the raw export row by row; duplicate counts match; each request's status equals its latest event; present workflow timestamps always parse; confirmed fields are blank while information is incomplete; the unknown-outcome rule holds for every request; nothing in events or assessments falls after the extract; coordinator and team events fall on business days within working hours; checkpoint 1 falls within working hours.

**Cleaning evaluation (`cleaning_evaluation.csv`):** run separately after cleaning; the cleaner never reads the answer key. All 22 duplicate rows were removed. Of the 491 field problems, compared by request ID and field after removing duplicates, 445 were restored. The 46 unresolved are 44 missing intake channels (no trusted source) and 2 impossible submitted start dates, which the rules leave blank rather than guess.

**Kit cards (`card_checks.csv`, all passed):** present labels equal the drawn kit items on every card; at most one of each item per card; expected/present/omitted logic consistent, with unknown expectations left blank; every box inside the content area; no objects closer than 14 pixels; reserved styles never drawn; the input fingerprint and cleaning version are recorded.

**Duplicate appearances:** the 1,561 drawn objects (1,209 kit items and 352 background objects) were compared as exact pixel copies of their rendered appearance after resizing, contrast blending, and rotation, before placement and degradation. None is shared across splits. This is a check, not a guarantee of generalization: the same drawing styles appear in every split.

## Segmentation pilot (training cards only; development evidence)

Five settings were tried on the 360 training cards (920 objects, including background objects). They are all listed in `segmentation_pilot_train.csv`, with every non-ideal case in `segmentation_failures_train.csv`. Validation and test cards were not used.

**Matching rule:** a region touches an object when their boxes intersect. An object is *missed* (no region), *split* (several regions), or matched by one region, which is a *good fit* when the region's box and the object's box overlap with IoU ≥ 0.5. A region is *false* if it touches no object and *merged* if it touches more than one.

| Setting tried | Good fit | Poor fit | Split | Missed | False regions | Merged regions |
|:---|---:|---:|---:|---:|---:|---:|
| A: global median background, threshold 10, close 7 | 70 | 522 | 328 | 0 | 2,183 | 293 |
| B: global median background, threshold 20, close 7 | 290 | 261 | 369 | 0 | 877 | 206 |
| C: global median background, threshold 30, close 7 | 523 | 86 | 308 | 3 | 634 | 116 |
| D: local blurred background, threshold 20, close 7 | 342 | 361 | 217 | 0 | 209 | 154 |
| E: median filter 5, local background, threshold 20, open 3, close 9 | 568 | 340 | 11 | 1 | 2 | 65 |

The version 1 approach (a single background colour and a threshold) now produces many false and split regions. Standard denoising and a local background estimate remove almost all false regions, but about a third of the remaining matches fit poorly and 65 regions merge neighbouring objects. Poor fits are most common for high-contrast objects, possibly because the blurred background estimate includes the objects themselves; this was not investigated further. Segmentation therefore needs real method work in Exercise 04. The single missed object was a faint white hard hat.

**Visibility is separate from label correctness.** An icon can be correctly labelled as drawn but effectively invisible. The human visibility review from AIDA 2154 Exercise 02 will be redone on the new cards and will deliberately include faint white hard hats.

## Questions for the instructor

1. Do these two candidate datasets address the "too clean" feedback, or should anything be added, removed, or toned down?
2. How should already-submitted exercises be handled once the data changes: rerun and resubmit each one, or apply version 2 from a particular exercise onward?
