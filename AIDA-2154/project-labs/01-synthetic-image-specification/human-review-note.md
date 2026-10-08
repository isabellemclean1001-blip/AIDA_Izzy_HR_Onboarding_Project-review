# Human Review Note – Onboarding-Kit Cards

## 1. Role of the coordinator

The vision method suggests which icons appear on a card. The coordinator reviews any flags and decides what action is needed. A detection does not confirm that a physical kit is complete; completion requires human confirmation.

## 2. When a card must be checked

| Situation | Coordinator action |
|:---|:---|
| Expected item not detected | Review the card and check whether the expected item is in the actual kit |
| Unclear detection | Check the card and actual kit rather than treating the uncertain result as confirmation |
| Device unknown | Always request clarification about which device is needed |
| Detected but not expected | Review the detection and the expected-item records to identify the discrepancy. In this dataset, the generator draws no extra items, so this flag indicates a false detection by the method. |

For device-unknown cards, laptop and phone detections are not treated as unexpected because their requirements are unresolved.

## 3. Review of the generated dataset

Before Exercise 02, a reviewer should check a wider sample of training cards, including small and low-contrast examples of each icon, to confirm they are visible to a person. Visibility has only been checked in the nine-card example grid so far.

The reviewer should also check that the invented kit rules are reasonable for the fictional workflow and that the example grid agrees with the manifest. Dataset checks across all splits should confirm file integrity and label consistency without using test images to tune the method. Test cards remain held back until final evaluation.

## 4. What the method must not be used for

The method is limited to synthetic onboarding-kit cards. It must not be used to verify physical kit contents, judge employees, or make automatic onboarding decisions. Any physical-kit check described here represents a proposed staff action; the project does not test real kits.
