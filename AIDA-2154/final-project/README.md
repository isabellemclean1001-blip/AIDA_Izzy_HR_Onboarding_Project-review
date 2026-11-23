# AIDA 2154 Final Professional Project – Checking Onboarding-Kit Cards with Computer Vision

> **Status: in progress.** Working plan; scope, methods, and deliverables to be confirmed with the instructor.

## Course focus

Complete a computer-vision project with documented data, reproducible work, evaluation, limitations, responsible-use analysis, and a recommendation.

## Question

On computer-generated onboarding-kit cards for the fictional Town of Pinecrest, can a vision method identify which first-day kit items appear well enough to flag possibly missing items for a coordinator to check? Where does it fail, and when must a person check the card?

A flag is a suggestion for review. Detection never confirms that a physical kit is complete; the coordinator decides what to do.

## Data

**Data version 2**, in [`shared/synthetic-data/kit-cards/`](../../shared/synthetic-data/kit-cards/): 600 generated cards with continuous size and contrast, two drawing styles per item, small rotations, background objects, and scan-like image effects, split into 360 training, 120 validation, and 120 test cards. Expected items come from the official cleaned requests. The test split is kept out of all development decisions.

Earlier project exercises (`../project-labs/`) used **data version 1** and remain unchanged as an earlier checkpoint. Results from the two versions are not mixed.

## Planned approach

1. Check image quality, and redo the human visibility review on the new cards, including faint white hard hats.
2. **Find objects with segmentation:** denoise each card, estimate its local background, threshold the difference, and clean the mask with morphology, building on the data version 2 segmentation pilot. Each region becomes a candidate object with a box.
3. **Baseline:** describe each region with simple colour and shape measurements and classify it with a transparent classifier as one of the five kit items or a background object.
4. **Main method (transfer learning):** crop each region and classify it with a small pretrained convolutional neural network (for example, ResNet-18 or MobileNet from Torchvision), fine-tuned on training-card crops.
5. **Card decision:** an item counts as present if any region on the card is classified as that item; known expected items that are not found are flagged for the coordinator to check.
6. **Compare both methods** on the same splits and measures: missing-item recall (primary), per-item precision, recall, and F1, card exact-match rate, and coordinator flag rate. Choose settings on the validation split only.
7. **Examine errors**, such as faint items that were missed, nearby objects merged into one region, poor-fitting regions, and background objects mistaken for kit items, with results by size and contrast band.
8. **Test robustness**, including the drawing style reserved for that purpose.
9. **Evaluate the chosen approach once on the test split.**
10. Complete a responsible-use analysis, model card, human-review rule, and recommendation.

Because every prediction comes from a located region, the results show where items were found as well as which items were present. A whole-card neural network may be added as an extra comparison if time allows. The method choice is to be confirmed with the instructor.

The work builds on AIDA 2154 Exercises 01–03 and the data version 2 segmentation pilot.

## Planned deliverables

- Analysis notebooks (`analysis/`) and saved results (`outputs/`)
- `report.md`: data, methods, baseline and method comparison, evaluation, error examples, and limitations
- Model card and responsible-use note
- `decision-brief.md`: recommendation and human-review rule
- Demonstration for the final technical defence

For each analysis included: the question, data version, method, key finding, limitation, and steps to reproduce.

## Checkpoints

| Week | Checkpoint |
|:---|:---|
| 10 (2–6 Nov) | Gate 3: working prototype (bring early project work) |
| 12 (16–20 Nov) | Gate 4: validation evidence; review preliminary findings, errors, risks, and limitations |
| 14 (30 Nov–4 Dec) | Gate 5: release candidate, in-class presentation, partner review, and model-card revision |
| 15 (7–9 Dec) | Gate 6: release readiness and documentation check |
| Final-examination period (14–18 Dec) | Submit, demonstrate, and complete the individual technical defence |

## Reproducing notebook 04 (transfer learning)

Notebook 04 needs two extra packages and a pretrained weights file, on top of the project environment (`.venv`, Python 3.14).

**Packages** (CPU only; no GPU is used), installed into `.venv` from the repository root:

```bash
.venv/bin/python -m pip install torch==2.15.0 torchvision==0.29.2
```

**Pretrained weights:** MobileNetV3-Small ImageNet weights, `mobilenet_v3_small-047dcff4.pth` (10,306,551 bytes). They are not stored in this repository. Torchvision caches them in its hub folder, which the notebook finds through `torch.hub.get_dir()`; in the tested setup this was `~/.cache/torch/hub/checkpoints/`. Notebook 04 stops unless the file's SHA-256 checksum is `047dcff4addef86ea5bc2eff13c9614dc11f47ab1160d0a71a25e7db994f4e1f`. Download them once, from the repository root:

```bash
.venv/bin/python -c "from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights; mobilenet_v3_small(weights=MobileNet_V3_Small_Weights.IMAGENET1K_V1)"
```

**Certificate note:** if the download fails with `CERTIFICATE_VERIFY_FAILED`, Python could not verify the server's certificate with its configured trusted certificates. One workaround (used for this project on macOS with python.org's Python 3.14, tested with `certifi` 2026.10.23) is to install the `certifi` certificate bundle into `.venv`:

```bash
.venv/bin/python -m pip install certifi
```

and then run the download with that bundle, which applies only to this one command:

```bash
SSL_CERT_FILE="$(.venv/bin/python -m certifi)" .venv/bin/python -c "from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights; mobilenet_v3_small(weights=MobileNet_V3_Small_Weights.IMAGENET1K_V1)"
```

**Run order:** notebooks 02 and 03 first, then notebook 04 (Restart and Run All; about 7 minutes on the tested Mac with four CPU threads). Results are reproducible in the tested environment; other package versions or hardware may give slightly different numbers.

## Boundaries

This project uses only computer-generated, non-personal images. It is not identity recognition, document verification, or an automated onboarding decision. Its analysis is distinct from the AIDA 1141 and AIDA 2156 final projects, which share the same workflow but answer different questions.