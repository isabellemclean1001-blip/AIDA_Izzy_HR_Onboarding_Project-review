"""Data version 2: label and layout checks on the kit cards, and a training-only segmentation pilot.

The pilot uses TRAINING cards only. Its settings were tried during development, so its results are
development evidence, not held-out performance. Run from anywhere after generating the cards:

    python shared/synthetic-data/checks/check_cards.py

Writes checks/results/card_checks.csv, segmentation_pilot_train.csv, and segmentation_failures_train.csv.
"""
import json
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

SD = Path(__file__).resolve().parent.parent        # shared/synthetic-data
CARDS = SD / "kit-cards"
OUT = SD / "checks" / "results"
OUT.mkdir(exist_ok=True)
ICONS = ["access_badge", "safety_vest", "hard_hat", "laptop", "phone"]
MARGIN, HEADER, SIZE = 14, 36, (480, 320)

manifest = pd.read_csv(CARDS / "manifest.csv", dtype=str, keep_default_na=False)
objects = pd.read_csv(CARDS / "icon_instances.csv")
info = json.loads((CARDS / "outputs/generation_info.json").read_text())

# ---------------------------------------------------------------- label and layout checks
kit = objects[objects["role"] == "kit_item"]
drawn = kit.groupby(["card_id", "object"]).size().unstack(fill_value=0).reindex(
    index=manifest["card_id"], columns=ICONS, fill_value=0)
logic_ok = True
for i in ICONS:
    known = manifest[f"expectation_known_{i}"] == "1"
    expected, present, omitted = (manifest[f"expected_{i}"], manifest[f"present_{i}"] == "1",
                                  manifest[f"omitted_{i}"] == "1")
    logic_ok &= (expected[~known] == "").all()                                   # unknown -> blank, never 0
    logic_ok &= known[present].all() and (expected[present] == "1").all()        # drawn only if known expected
    logic_ok &= ((expected == "1") & known & ~present == omitted).all()         # omitted = known expected, not drawn
too_close = 0
for _, card in objects.groupby("card_id"):
    boxes = card[["x0", "y0", "x1", "y1"]].to_numpy()
    for a in range(len(boxes)):
        for b in range(a + 1, len(boxes)):
            p, q = boxes[a], boxes[b]
            if not (p[2] + MARGIN <= q[0] or q[2] + MARGIN <= p[0] or p[3] + MARGIN <= q[1] or q[3] + MARGIN <= p[1]):
                too_close += 1
checks = {
    "present_<item> equals the kit items drawn, on every card": all(
        (drawn[i].to_numpy() == manifest[f"present_{i}"].astype(int).to_numpy()).all() for i in ICONS),
    "At most one of each kit item per card": int(drawn.to_numpy().max()) <= 1,
    "Expected / present / omitted logic consistent; unknown expectations stay blank": bool(logic_ok),
    "Every box lies inside the content area": bool(((objects["x0"] >= MARGIN) & (objects["x1"] <= SIZE[0] - MARGIN)
                                                    & (objects["y0"] >= HEADER + MARGIN)
                                                    & (objects["y1"] <= SIZE[1] - MARGIN)).all()),
    "Object pairs closer than the 14-pixel margin": too_close,
    "Reserved style c never drawn": bool((objects["style"] != "c").all()),
    "Rendered appearances shared across splits (exact pixel match before degradation)":
        info["drawings_shared_across_splits"],
    "Input fingerprint and cleaning version recorded": bool(info["input_sha256"])
                                                       and info["input_record"]["cleaning_version"],
}
pd.Series(checks, name="result").to_csv(OUT / "card_checks.csv")
print(pd.Series(checks, name="result").to_string())

# ---------------------------------------------------------------- segmentation pilot (training cards only)
# Matching rule: a region "touches" an object when the region's bounding box intersects the object's
# tight box. Per object: missed (no region), one region, or split (several regions). Per region: false
# (touches no object) or merged (touches more than one object). A single matching region is a good fit
# when its box overlaps the object's box with IoU >= 0.5.
CONTENT = (slice(37, 318), slice(2, 478))
CONFIGS = [  # every setting tried, in order
    {"name": "A: global median background, threshold 10, close 7", "median": 0, "background": "global", "threshold": 10, "open": 0, "close": 7},
    {"name": "B: global median background, threshold 20, close 7", "median": 0, "background": "global", "threshold": 20, "open": 0, "close": 7},
    {"name": "C: global median background, threshold 30, close 7", "median": 0, "background": "global", "threshold": 30, "open": 0, "close": 7},
    {"name": "D: local blurred background, threshold 20, close 7", "median": 0, "background": "local", "threshold": 20, "open": 0, "close": 7},
    {"name": "E: median filter 5, local background, threshold 20, open 3, close 9", "median": 5, "background": "local", "threshold": 20, "open": 3, "close": 9},
]
MIN_REGION_PIXELS = 30


def regions(path, cfg):
    image = cv2.imread(str(path))
    if cfg["median"]:
        image = cv2.medianBlur(image, cfg["median"])
    content = image[CONTENT].astype(float)
    background = (cv2.GaussianBlur(content, (0, 0), 25) if cfg["background"] == "local"
                  else np.median(content.reshape(-1, 3), axis=0))
    mask = (np.linalg.norm(content - background, axis=2) > cfg["threshold"]).astype(np.uint8)
    if cfg["open"]:
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((cfg["open"], cfg["open"]), np.uint8))
    if cfg["close"]:
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (cfg["close"],) * 2))
    _, _, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    x_off, y_off = CONTENT[1].start, CONTENT[0].start
    return [(s[0] + x_off, s[1] + y_off, s[0] + s[2] + x_off, s[1] + s[3] + y_off)
            for s in stats[1:] if s[4] >= MIN_REGION_PIXELS]


def touches(r, o):
    return r[0] < o[2] and r[2] > o[0] and r[1] < o[3] and r[3] > o[1]


def iou(r, o):
    inter = max(0, min(r[2], o[2]) - max(r[0], o[0])) * max(0, min(r[3], o[3]) - max(r[1], o[1]))
    return inter / ((r[2] - r[0]) * (r[3] - r[1]) + (o[2] - o[0]) * (o[3] - o[1]) - inter)


train = manifest[manifest["split"] == "train"]
train_objects = objects[objects["split"] == "train"]
summary, failures = [], []
for cfg in CONFIGS:
    counts = {"missed": 0, "one_region_good_fit": 0, "one_region_poor_fit": 0, "split": 0,
              "false_regions": 0, "merged_regions": 0}
    for card in train.itertuples():
        found = regions(CARDS / "images" / card.file_name, cfg)
        objs = train_objects[train_objects["card_id"] == card.card_id]
        boxes = [(o.x0, o.y0, o.x1, o.y1) for o in objs.itertuples()]
        for o, box in zip(objs.itertuples(), boxes):
            hit = [r for r in found if touches(r, box)]
            outcome = ("missed" if not hit else "split" if len(hit) > 1
                       else "one_region_good_fit" if iou(hit[0], box) >= 0.5 else "one_region_poor_fit")
            counts[outcome] += 1
            if outcome != "one_region_good_fit":
                failures.append({"config": cfg["name"], "card_id": card.card_id, "role": o.role, "object": o.object,
                                 "style": o.style, "size_band": o.size_band, "contrast_band": o.contrast_band,
                                 "outcome": outcome})
        for r in found:
            n = sum(touches(r, b) for b in boxes)
            counts["false_regions"] += n == 0
            counts["merged_regions"] += n > 1
    summary.append({"config": cfg["name"], "training_cards": len(train), "objects": len(train_objects), **counts})
pd.DataFrame(summary).to_csv(OUT / "segmentation_pilot_train.csv", index=False)
pd.DataFrame(failures).to_csv(OUT / "segmentation_failures_train.csv", index=False)
print(pd.DataFrame(summary).to_string(index=False))
