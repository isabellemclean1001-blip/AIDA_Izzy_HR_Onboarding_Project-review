# Label Guide – Onboarding-Kit Icons

## 1. What is being labelled

Each row in `manifest.csv` represents one card for one fictional employee. Each card has five binary presence labels, recording whether each icon was drawn.

## 2. The icons

| Icon | Reference image | Description |
|:---|:---|:---|
| Access badge | ![Access badge](reference_icons/access_badge.png) | Blue portrait card with a clip and blank photo area |
| Safety vest | ![Safety vest](reference_icons/safety_vest.png) | Orange vest with grey reflective stripes |
| Hard hat | ![Hard hat](reference_icons/hard_hat.png) | Yellow dome with a brim |
| Laptop | ![Laptop](reference_icons/laptop.png) | Dark frame, blue screen, and wide base |
| Phone | ![Phone](reference_icons/phone.png) | Tall dark rectangle with a blue screen |

The laptop and phone share colours but differ in shape. The badge and phone also have similar upright shapes. The grey-blue header resembles some device colours, so methods should analyse the content area below it.

## 3. Label definitions

| Column | Meaning |
|:---|:---|
| `present_<icon>` | 1 if the icon was drawn; 0 otherwise. This is the vision label. |
| `expected_<icon>` | 1 if the kit rules require the item; 0 otherwise, subject to the unknown-device exception below. |
| `omitted_<icon>` | 1 if the item was expected but deliberately left off the card; 0 otherwise. |

Presence describes the image, while expectation comes from the fictional request records and kit rules. An omission occurs when an expected item is not drawn. These reference labels come directly from the generator, rather than predictions made by a vision method.

## 4. What the method outputs and who decides

| Output | Meaning | Next step |
|:---|:---|:---|
| Icon detected | The method suggests that the icon appears | Compare with the expected kit |
| Expected but not detected | An expected icon may be absent or missed by the method | Flag for coordinator review and an actual-kit check |
| Detected but not expected | The method suggests an icon that the kit rules do not require | Flag for coordinator review |
| Unclear | The method cannot confidently determine presence | Flag for coordinator review |

The generator does not draw unexpected extra items, so unexpected detections in this dataset represent false detections by the method rather than actual extra kit contents.

“Unclear” is a method output, not a reference label. Its threshold will be selected using validation data. The method describes the card; the coordinator decides what action to take, and detection never confirms that a physical kit is complete.

## 5. Edge cases

- **Empty kit:** There are 27 cards with nothing expected. These test whether the method incorrectly detects icons on blank cards.
- **All items omitted:** These cards look identical to empty-kit cards. The distinction comes from the expected-item records, not the image.
- **Device unknown:** Four cards have unresolved equipment items. Their `expected_laptop` and `expected_phone` values are 0 but represent unknown expectations. Exclude both device expectations from missing-item evaluation and always flag these cards for clarification. Their presence labels remain valid. None are in the test set.
- **Low contrast:** Faint icons are labelled present because they were drawn. The yellow hard hat is a potentially difficult example. Visibility has only been checked in the nine-card example grid; a wider sample check is part of the human-review note.

## 6. Planned evaluation

The following measures are defined before evaluating the methods:

- **Missing-item recall (primary):** Of all deliberately omitted items, the proportion flagged as missing or unclear, pooled across icons.
- **Missing-item precision:** Of the missing or unclear flags on items with a known expectation of 1, the proportion that are genuinely omitted items.
- **Per-icon presence precision, recall, and F1:** Compare detected presence with `present_<icon>`. Unclear outputs count as no confirmed detection for these measures, and their frequency is reported separately.
- **Card exact-match rate:** The proportion of cards where all five presence labels are correctly identified, with no unclear outputs.
- **Coordinator flag rate:** The proportion of cards receiving at least one missing-item, unexpected-detection, unclear, or unknown-device flag.

Unknown device expectations are excluded from missing-item precision and recall. Small per-icon test counts will be reported alongside results.

The validation set will be used to tune parameters and confidence thresholds. The test set will be held back for one final evaluation. A simple baseline, such as colour counting within the content area, will be compared with a classical method, such as OpenCV template matching. Any optional trained model will use the same split and evaluation measures.

## 7. Label-quality limits

The presence labels accurately record what the generator drew, but expected-item labels depend on invented kit rules. They do not establish actual equipment requirements or physical kit contents.

Rendering boxes include transparent margins rather than tight object boundaries. Low-contrast visibility has only been checked in the example grid, so further human review may identify examples that need adjustment.
