# Kit Cards – Data Version 2

Computer-generated onboarding-kit cards for the AIDA 2154 final project. Each card shows icons for the first-day items packed for one fictional employee; some expected items are deliberately left off to simulate packing mistakes. All images and labels are synthetic and non-personal. Version 1 cards remain unchanged in `AIDA-2154/project-labs/01-synthetic-image-specification/` and under the Git tag `data-v1`.

## How the cards are made

`generate_kit_cards.py` (seed 2026; Pillow and NumPy) reads the official cleaned requests (`../cleaning/output/requests_cleaned.csv`) and records that file's fingerprint and cleaning version in `outputs/generation_info.json`. Run it from the repository root:

`python shared/synthetic-data/kit-cards/generate_kit_cards.py`

The same seed, settings, code, input file, and package versions reproduce the same files.

## Files

| File | One row or file represents |
|:---|:---|
| `images/KIT-####.jpg` | One 480 × 320 card (600 cards) |
| `manifest.csv` | One card: split, expected items, presence labels, omissions, and image-quality settings |
| `icon_instances.csv` | One drawn object: kit item or background object, its appearance settings, and its box |
| `reference_icons/` | One clean, upright, high-contrast copy of each development style and background object |
| `outputs/example_cards.png` | Example training cards with their labels |
| `outputs/generation_info.json` | Seed, input fingerprint, cleaning record, and duplicate-check counts |

## Design

- **Employees:** 600 chosen reproducibly from employees whose confirmed start date is on or before 14 September 2026, two weeks before the request extract, so all their tasks are recorded. One card per employee.
- **Expected items:** access badge if the employee has a workplace-access task; safety vest and hard hat if the confirmed department is a field department (Parks, Transit, Utilities); laptop or phone from the equipment request. If an expectation cannot be established from the cleaned records (for example, a blank equipment item), it is marked unknown and never treated as "not needed". Only items known to be expected can be packed.
- **Omissions:** each known expected item is left off with probability 0.15.
- **Appearance:** continuous height (38–100 pixels) and contrast (0.22–1.0, the share of the drawing's colour kept against the paper), rotation of −12° to +12°, and one of two development styles per item.
- **Styles:** all development styles appear in each split; one additional style per item is reserved for a robustness test and is never drawn here. The test split therefore measures new arrangements and image conditions with familiar styles, not unseen styles.
- **Background objects:** 0–2 per card (coffee mug, pen, or notebook), labelled `background_object`.
- **Layout:** objects never overlap; drawn boxes stay at least 14 pixels apart. On a crowded card, an object is shrunk within its size range until it fits, and the recorded height is the one drawn.
- **Boxes:** tight around each rotated drawing's non-transparent pixels, calculated before any image degradation.
- **Image quality (per card):** paper tint, a lighting gradient, Gaussian noise, blur on about 40% of cards, and JPEG compression at quality 60–92.
- **Split:** 360 training, 120 validation, 120 test cards, stratified by field department and whether any item was omitted. Keep the test cards out of all development decisions.

## Fields

**`manifest.csv`**

| Field | Meaning |
|:---|:---|
| `card_id`, `employee_id`, `file_name`, `split` | Card, employee, image file, and split |
| `access_request_id`, `equipment_request_id` | Source requests, when present |
| `hiring_department`, `field_department` | Confirmed department and whether it is a field department (blank if unresolved) |
| `expectation_known_<item>` | 1 if the records establish whether the item is expected; 0 if unknown |
| `expected_<item>` | 1 expected, 0 not expected, blank when the expectation is unknown |
| `present_<item>` | 1 if the item is drawn on the card (the vision label); 0 otherwise |
| `omitted_<item>` | 1 if the item is known to be expected but was not drawn |
| `n_expected_known`, `n_present`, `n_omitted`, `n_background_objects` | Counts per card |
| `paper_r`, `paper_g`, `paper_b`, `gradient`, `gradient_angle_deg`, `noise_sigma`, `blur_radius`, `jpeg_quality` | Image-quality settings for the card |

Items: `access_badge`, `safety_vest`, `hard_hat`, `laptop`, `phone`.

**`icon_instances.csv`**

| Field | Meaning |
|:---|:---|
| `card_id`, `split` | Card and split |
| `role` | `kit_item` or `background_object` |
| `object`, `style` | Item or background-object name, and drawing style (`a` or `b`; background objects use `a`) |
| `height_px`, `size_band` | Drawn height before rotation, and its band: small (< 52), medium (52–76), large (≥ 77) |
| `contrast`, `contrast_band` | Contrast setting and its band: low (< 0.40), medium (0.40 to < 0.75), high (≥ 0.75) |
| `rotation_deg` | Rotation in degrees |
| `x0`, `y0`, `x1`, `y1` | Tight box in card pixel coordinates (end values excluded) |

## Labels and visibility

Presence labels record what the generator drew, so they are correct by construction. A correctly labelled icon can still be hard or impossible for a person to see, especially faint white hard hats. Visibility is checked separately by human review, not assumed from the labels.

## Limitations

Rates, kit rules, styles, and image effects are invented. Results describe these generated cards, not real kits, photographs, or scans. Exact duplicate checks find identical rendered drawings across splits, but passing them does not show that a method generalizes to new designs.
