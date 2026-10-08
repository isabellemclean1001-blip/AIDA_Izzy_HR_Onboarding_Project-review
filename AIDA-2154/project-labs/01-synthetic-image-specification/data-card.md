# Data Card – Synthetic Onboarding-Kit Cards

## 1. Purpose and intended use

These cards are computer-generated images representing fictional employees’ first-day kits for the Town of Pinecrest. AIDA 2154 will use them to test whether a classical vision method can identify which icons appear when size, position, and contrast vary. They support a limited vision experiment and are not intended for real HR decisions.

## 2. What the files contain

| File or folder | One row or file represents | Count |
|:---|:---|---:|
| `images/` | One kit card (PNG, 480 × 320 pixels) | 500 |
| `manifest.csv` | One card: split, linked IDs, expected / present / omitted items | 500 |
| `icon_instances.csv` | One icon drawn on a card, with its size, contrast, and rendering box | 1,007 |
| `reference_icons/` | One clean, high-contrast copy of each icon | 5 |
| `outputs/example_cards.png` | Example grid of training cards | 1 |

The boxes in `icon_instances.csv` include transparent margins around the drawings; they are rendering boxes rather than tight object outlines.

## 3. How the images were generated

The `generate_kit_cards.py` script reads the clean `requests.csv` from AIDA 1141 Exercise 02 and creates one card per fictional employee. It determines the expected items using the kit rules below, then randomly leaves some items off to represent omissions. Pillow draws the remaining icons with varied sizes, contrast levels, and positions.

The generator uses seed 2026. Rerunning it with the same source records, script, and environment produces identical files.

To regenerate the files, run this command from the exercise folder:

`python generate_kit_cards.py`

## 4. Kit rules (invented assumptions)

| Icon | Expected when | Source field |
|:---|:---|:---|
| Access badge | Employee has a `workplace_access` task | `task_type` |
| Safety vest | Hiring department is Parks, Transit, or Utilities | `hiring_department` |
| Hard hat | Hiring department is Parks, Transit, or Utilities | `hiring_department` |
| Laptop | `equipment_setup` task lists `laptop` | `equipment_item` |
| Phone | `equipment_setup` task lists `phone` | `equipment_item` |

These rules are invented for the fictional Town of Pinecrest and do not represent real municipal policy. The manifest links each card to its employee ID and, where applicable, workplace-access and equipment request IDs.

Four equipment requests have a blank item, recorded as `device_unknown = True`. Their laptop and phone expectations are unresolved and will be excluded from missing-item evaluation, with human clarification required. Their visual presence labels remain valid because the generator records what it draws.

## 5. Visual variation

| Setting | Levels |
|:---|:---|
| Size | Small 38 px · medium 64 px · large 90 px |
| Contrast | High (full colour) · medium (55% icon colour) · low (25% icon colour), blended toward the card background |
| Position | Random within the content area below the header, with a gap between icons |

Rotation, noise, backgrounds, overlapping or partly hidden icons, and unexpected extra items are not varied. These conditions will be documented as untested in Exercise 07.

## 6. Train / validation / test split

| Split | Cards | Cards with an omission | Omitted items | Empty kits | Device unknown |
|:---|---:|---:|---:|---:|---:|
| Train | 300 | 83 | 97 | 14 | 3 |
| Validation | 100 | 27 | 32 | 8 | 1 |
| Test | 100 | 27 | 32 | 5 | 0 |

The fixed 60/20/20 split assigns each employee’s card to one group. It is approximately stratified by field department and whether the card contains an omission; it does not explicitly balance individual icons, contrast levels, or omitted-item counts. No unknown-device cards fall in the test set.

Training cards support method development, and validation cards support tuning. Test cards are held back until final evaluation. The example grid uses training cards only, and any later variations of a card will remain in its original split.

## 7. Dataset summary (seed 2026)

| Icon | Expected | Present | Omitted |
|:---|---:|---:|---:|
| Access badge | 322 | 263 | 59 |
| Safety vest | 267 | 235 | 32 |
| Hard hat | 267 | 239 | 28 |
| Laptop | 148 | 134 | 14 |
| Phone | 164 | 136 | 28 |

| Measure | Value |
|:---|:---|
| Icons shown per card | 0: 50 · 1: 136 · 2: 131 · 3: 123 · 4: 60 |
| Empty kits (nothing expected) | 27 |
| Device unknown (equipment task with blank item) | 4 |
| Omission setting | Each expected item has a 15% probability of being left off |

These are simulated counts produced under invented settings, not evidence about real kits or packing error rates. A blank card may represent either a kit with nothing expected or a card where all expected items were omitted.

## 8. Privacy and safety

No real employee, employer, or City of Red Deer records were used. The icons are generated shapes, and the badge contains a blank photo area without a face or name. Card images contain no text or personal images, and the task does not involve OCR.

## 9. Limitations

- The kit rules and 15% omission probability are invented assumptions.
- The icons are clean, flat drawings, so results cannot establish performance on real kit photographs.
- Per-icon test omission counts are small, so per-icon results require caution.
- Low-contrast icons require human visibility checks before being treated as fair detection examples.
- Detection describes what appears on a card; it does not verify the contents of a physical kit.
