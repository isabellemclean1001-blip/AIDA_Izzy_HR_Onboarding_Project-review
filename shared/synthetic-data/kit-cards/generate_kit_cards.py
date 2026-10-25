"""Generate synthetic onboarding-kit card images for AIDA 2154 (data version 2).

Location: shared/synthetic-data/kit-cards/. Version 1 cards remain unchanged in
AIDA-2154/project-labs/01-synthetic-image-specification/ and under the Git tag data-v1.

Each selected fictional employee gets one kit card showing icons for the first-day items
packed in their kit. Expected items come from the cleaned AIDA 1141 request records; some
expected items are left off on purpose to simulate packing mistakes. Version 2 adds
continuous size and contrast, small rotations, two drawing styles per item, a few
background objects, and mild scan-like image degradation (paper tint, lighting gradient,
noise, blur, JPEG compression).

All images and labels are computer-generated. Rates are invented settings, not evidence
about real onboarding kits.

Run from anywhere:  python shared/synthetic-data/kit-cards/generate_kit_cards.py
Requires: Pillow and NumPy. The same seed, settings, code, input file, and package
versions reproduce the same files.
"""

import csv
import hashlib
import json
import random
from collections import Counter
from datetime import date
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------- settings
SEED = 2026
HERE = Path(__file__).resolve().parent                  # shared/synthetic-data/kit-cards
# Official cleaned request records, made by the shared cleaning code (../cleaning/clean_requests.py). The record
# of how the file was made (source, cleaning version, unresolved fields, fingerprints) sits next to it.
CLEANED_REQUESTS = HERE.parent / "cleaning" / "output" / "requests_cleaned.csv"
CLEANED_INFO = CLEANED_REQUESTS.with_name(CLEANED_REQUESTS.stem + "_info.json")
IMAGE_DIR = HERE / "images"
REFERENCE_DIR = HERE / "reference_icons"
OUTPUT_DIR = HERE / "outputs"

N_CARDS = 600
# Cards are made only for employees who started at least two weeks before the request extract,
# so all of their onboarding tasks are in the records
LATEST_START_DATE = date(2026, 9, 14)

ICONS = ["access_badge", "safety_vest", "hard_hat", "laptop", "phone"]
BACKGROUND_OBJECTS = ["coffee_mug", "pen", "notebook"]
DEVELOPMENT_STYLES = ["a", "b"]   # appear in every split
RESERVED_STYLE = "c"              # one extra style per icon, reserved for Exercise 07; never drawn here
FIELD_DEPARTMENTS = {"Parks", "Transit", "Utilities"}
OMISSION_RATE = 0.15              # chance each known expected item is left off the card (invented)
BACKGROUND_OBJECT_COUNTS = ([0, 1, 2], [0.50, 0.35, 0.15])

CARD_SIZE = (480, 320)            # width, height in pixels
PAPER_RGB = (236, 236, 230)       # base paper colour; each card's tint varies around it
PAPER_TINT = 8                    # maximum change per colour channel
CARD_BORDER = (120, 120, 120)
HEADER_HEIGHT = 36
HEADER_COLOUR = (90, 110, 130)
MARGIN = 14                       # gap between objects and from card edges

ICON_HEIGHT_RANGE = (38, 100)     # pixels, before rotation
OBJECT_HEIGHT_RANGE = (30, 80)
CONTRAST_RANGE = (0.22, 1.0)      # share of the drawing's colour kept vs the paper
ROTATION_RANGE = (-12.0, 12.0)    # degrees
SIZE_BANDS = [(52, "small"), (77, "medium"), (10**6, "large")]    # height < limit -> band (v1 levels 38/64/90)
CONTRAST_BANDS = [(0.40, "low"), (0.75, "medium"), (10.0, "high")]
SUPERSAMPLE = 4                   # draw large, then shrink for smooth edges

# Image degradation per card (scan-like), applied after all objects are drawn and boxes recorded
GRADIENT_RANGE = (0.0, 0.12)      # brightness varies by up to +/- this share across the card
NOISE_SIGMA_RANGE = (0.0, 6.0)    # Gaussian noise, in 0-255 colour units
BLUR_RATE, BLUR_RADIUS_RANGE = 0.40, (0.3, 1.0)
JPEG_QUALITY_RANGE = (60, 92)

SPLIT_PATTERN = ["train", "train", "train", "validation", "test"]  # 60 / 20 / 20


# ---------------------------------------------------------------- drawings
# Each function draws one style of one item on a transparent square canvas of side s.

def draw_access_badge(d, s, style):
    if style == "c":   # reserved: horizontal red badge
        d.rounded_rectangle([0.05 * s, 0.25 * s, 0.95 * s, 0.80 * s], radius=0.06 * s, fill=(180, 50, 50))
        d.rectangle([0.12 * s, 0.34 * s, 0.40 * s, 0.70 * s], fill=(245, 245, 245))
        d.rectangle([0.48 * s, 0.40 * s, 0.86 * s, 0.45 * s], fill=(245, 245, 245))
        d.rectangle([0.48 * s, 0.55 * s, 0.76 * s, 0.60 * s], fill=(245, 245, 245))
        return
    colour = (40, 90, 170) if style == "a" else (40, 140, 90)
    d.rounded_rectangle([0.22 * s, 0.12 * s, 0.78 * s, 0.95 * s], radius=0.06 * s, fill=colour)
    if style == "a":
        d.rounded_rectangle([0.42 * s, 0.03 * s, 0.58 * s, 0.17 * s], radius=0.03 * s, fill=(70, 70, 70))  # clip
    else:
        d.ellipse([0.45 * s, 0.16 * s, 0.55 * s, 0.24 * s], fill=(0, 0, 0, 0))   # lanyard hole
        d.rectangle([0.22 * s, 0.86 * s, 0.78 * s, 0.95 * s], fill=(20, 90, 60))  # colour band
    d.rectangle([0.34 * s, 0.28 * s, 0.66 * s, 0.56 * s], fill=(245, 245, 245))   # blank photo area
    d.rectangle([0.32 * s, 0.64 * s, 0.68 * s, 0.69 * s], fill=(245, 245, 245))   # text lines
    d.rectangle([0.32 * s, 0.75 * s, 0.58 * s, 0.80 * s], fill=(245, 245, 245))


def draw_safety_vest(d, s, style):
    body = [(0.18 * s, 0.10 * s), (0.38 * s, 0.10 * s), (0.50 * s, 0.38 * s), (0.62 * s, 0.10 * s),
            (0.82 * s, 0.10 * s), (0.90 * s, 0.92 * s), (0.10 * s, 0.92 * s)]
    if style == "c":   # reserved: orange vest with a zip and no stripes
        d.polygon(body, fill=(235, 110, 20))
        d.rectangle([0.485 * s, 0.38 * s, 0.515 * s, 0.92 * s], fill=(90, 90, 90))
        return
    d.polygon(body, fill=(245, 130, 30) if style == "a" else (190, 220, 40))
    stripe = (200, 200, 200) if style == "a" else (215, 215, 225)
    d.rectangle([0.13 * s, 0.55 * s, 0.87 * s, 0.62 * s], fill=stripe)
    d.rectangle([0.11 * s, 0.74 * s, 0.89 * s, 0.81 * s], fill=stripe)
    if style == "b":   # vertical shoulder stripes
        d.rectangle([0.25 * s, 0.12 * s, 0.31 * s, 0.55 * s], fill=stripe)
        d.rectangle([0.69 * s, 0.12 * s, 0.75 * s, 0.55 * s], fill=stripe)


def draw_hard_hat(d, s, style):
    if style == "c":   # reserved: orange hat with a full brim
        d.chord([0.20 * s, 0.22 * s, 0.80 * s, 0.94 * s], start=180, end=360, fill=(240, 120, 30))
        d.ellipse([0.02 * s, 0.52 * s, 0.98 * s, 0.70 * s], fill=(215, 95, 20))
        return
    dome, trim = ((240, 200, 30), (215, 175, 20)) if style == "a" else ((248, 248, 248), (180, 180, 185))
    d.chord([0.16 * s, 0.18 * s, 0.84 * s, 0.98 * s], start=180, end=360, fill=dome)
    d.rectangle([0.46 * s, 0.20 * s, 0.54 * s, 0.58 * s], fill=trim)              # ridge
    d.rounded_rectangle([0.05 * s, 0.56 * s, 0.95 * s, 0.68 * s], radius=0.04 * s, fill=trim)  # brim


def draw_laptop(d, s, style):
    frame, screen, base = {"a": ((60, 60, 70), (110, 150, 200), (80, 80, 90)),
                           "b": ((170, 170, 180), (40, 50, 70), (150, 150, 160)),
                           "c": ((25, 25, 25), (80, 170, 110), (45, 45, 45))}[style]
    d.rounded_rectangle([0.14 * s, 0.18 * s, 0.86 * s, 0.68 * s], radius=0.04 * s, fill=frame)
    d.rectangle([0.20 * s, 0.24 * s, 0.80 * s, 0.62 * s], fill=screen)
    d.polygon([(0.06 * s, 0.82 * s), (0.14 * s, 0.70 * s), (0.86 * s, 0.70 * s), (0.94 * s, 0.82 * s)], fill=base)
    if style == "c":   # reserved: keyboard lines
        for y in (0.73, 0.77):
            d.line([(0.18 * s, y * s), (0.82 * s, y * s)], fill=(110, 110, 110), width=max(1, round(0.01 * s)))


def draw_phone(d, s, style):
    body, screen = {"a": ((60, 60, 70), (110, 150, 200)), "b": ((240, 240, 240), (50, 55, 65)),
                    "c": ((60, 60, 70), (60, 170, 170))}[style]
    d.rounded_rectangle([0.30 * s, 0.06 * s, 0.70 * s, 0.94 * s], radius=0.07 * s, fill=body)
    if style == "b":
        d.rounded_rectangle([0.30 * s, 0.06 * s, 0.70 * s, 0.94 * s], radius=0.07 * s,
                            outline=(150, 150, 155), width=max(1, round(0.02 * s)))
    d.rectangle([0.34 * s, 0.15 * s, 0.66 * s, 0.80 * s], fill=screen)
    if style == "a":
        d.ellipse([0.46 * s, 0.84 * s, 0.54 * s, 0.90 * s], fill=(150, 150, 160))   # button
    if style == "c":   # reserved: notch at the top of the screen
        d.rectangle([0.44 * s, 0.15 * s, 0.56 * s, 0.19 * s], fill=body)


def draw_coffee_mug(d, s, style):
    d.ellipse([0.62 * s, 0.32 * s, 0.90 * s, 0.70 * s], outline=(120, 80, 50), width=max(1, round(0.06 * s)))
    d.rounded_rectangle([0.18 * s, 0.22 * s, 0.70 * s, 0.88 * s], radius=0.06 * s, fill=(140, 95, 60))


def draw_pen(d, s, style):
    d.polygon([(0.20 * s, 0.86 * s), (0.72 * s, 0.14 * s), (0.82 * s, 0.22 * s), (0.30 * s, 0.94 * s)],
              fill=(30, 60, 140))
    d.polygon([(0.20 * s, 0.86 * s), (0.30 * s, 0.94 * s), (0.14 * s, 0.98 * s)], fill=(60, 60, 60))


def draw_notebook(d, s, style):
    d.rectangle([0.24 * s, 0.08 * s, 0.80 * s, 0.94 * s], fill=(120, 130, 160))
    for k in range(6):
        y = (0.16 + k * 0.14) * s
        d.ellipse([0.19 * s, y, 0.29 * s, y + 0.06 * s], outline=(70, 70, 70), width=max(1, round(0.015 * s)))


DRAWERS = {"access_badge": draw_access_badge, "safety_vest": draw_safety_vest, "hard_hat": draw_hard_hat,
           "laptop": draw_laptop, "phone": draw_phone, "coffee_mug": draw_coffee_mug, "pen": draw_pen,
           "notebook": draw_notebook}


def band(value, bands):
    return next(name for limit, name in bands if value < limit)


def render_object(name, style, height, contrast, rotation, paper):
    """RGBA drawing of one item: blended toward the card's paper colour, then rotated."""
    big = Image.new("RGBA", (height * SUPERSAMPLE, height * SUPERSAMPLE), (0, 0, 0, 0))
    DRAWERS[name](ImageDraw.Draw(big), height * SUPERSAMPLE, style)
    img = big.resize((height, height), Image.LANCZOS)
    background = Image.new("RGB", img.size, paper)
    out = Image.blend(background, img.convert("RGB"), contrast)
    out.putalpha(img.getchannel("A"))
    return out.rotate(rotation, resample=Image.BICUBIC, expand=True)


# ---------------------------------------------------------------- kit contents

def load_kits():
    """Expected first-day items per eligible employee, with a known/unknown flag for each item."""
    with open(CLEANED_REQUESTS, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    by_employee = {}
    for r in rows:
        by_employee.setdefault(r["employee_id"], []).append(r)

    kits = {}
    for employee_id, tasks in sorted(by_employee.items()):
        starts = {t["confirmed_start_date"] for t in tasks if t["confirmed_start_date"]}
        if len(starts) != 1 or date.fromisoformat(starts.pop()) > LATEST_START_DATE:
            continue
        departments = {t["hiring_department"] for t in tasks if t["hiring_department"]}
        types = {t["task_type"] for t in tasks}
        expected, known = {}, {}
        access = [t for t in tasks if t["task_type"] == "workplace_access"]
        equipment = [t for t in tasks if t["task_type"] == "equipment_setup"]

        expected["access_badge"], known["access_badge"] = int("workplace_access" in types), True
        if len(departments) == 1:   # field departments need safety gear
            field = departments.copy().pop() in FIELD_DEPARTMENTS
            for item in ("safety_vest", "hard_hat"):
                expected[item], known[item] = int(field), True
        else:                       # department unresolved: whether safety gear is needed is unknown
            for item in ("safety_vest", "hard_hat"):
                expected[item], known[item] = None, False
        items = {t["equipment_item"] for t in equipment}
        if not equipment:
            for item in ("laptop", "phone"):
                expected[item], known[item] = 0, True
        elif items <= {"laptop", "phone"} and len(items) == 1:
            for item in ("laptop", "phone"):
                expected[item], known[item] = int(item in items), True
        else:                       # equipment requested but the device is unresolved
            for item in ("laptop", "phone"):
                expected[item], known[item] = None, False

        kits[employee_id] = {
            "hiring_department": departments.copy().pop() if len(departments) == 1 else "",
            "expected": expected, "known": known,
            "access_request_id": access[0]["request_id"] if access else "",
            "equipment_request_id": equipment[0]["request_id"] if equipment else "",
        }
    return kits


def place_objects(rng, objects, paper):
    """Render each object with random size, contrast, style, and rotation, and place it without overlap.

    Objects never overlap: drawn boxes keep at least MARGIN apart. On a crowded card an object is
    shrunk (within its size range) until it fits; the recorded height is the one actually drawn.
    """
    placed = []
    for name, role in objects:
        style = rng.choice(DEVELOPMENT_STYLES) if role == "kit_item" else "a"
        height = rng.randint(*(ICON_HEIGHT_RANGE if role == "kit_item" else OBJECT_HEIGHT_RANGE))
        contrast = round(rng.uniform(*CONTRAST_RANGE), 3)
        rotation = round(rng.uniform(*ROTATION_RANGE), 1)
        low = (ICON_HEIGHT_RANGE if role == "kit_item" else OBJECT_HEIGHT_RANGE)[0]
        while True:
            img = render_object(name, style, height, contrast, rotation, paper)
            # Box: tight around the rotated drawing's non-transparent pixels, before any image degradation
            bx0, by0, bx1, by1 = img.getchannel("A").getbbox()
            w, h = img.size
            position = None
            for _ in range(2000):
                x0 = rng.randint(MARGIN - bx0, CARD_SIZE[0] - MARGIN - bx1)
                y0 = rng.randint(HEADER_HEIGHT + MARGIN - by0, CARD_SIZE[1] - MARGIN - by1)
                box = (x0 + bx0, y0 + by0, x0 + bx1, y0 + by1)
                if all(not boxes_touch(box, q["box"]) for q in placed):
                    position = (x0, y0)
                    break
            if position or height == low:
                break
            height = max(low, int(height * 0.85))   # a crowded card: shrink this object and try again
        if position is None:
            raise RuntimeError("Could not place objects without overlap; enlarge the card or shrink objects.")
        x0, y0 = position
        canvas = (x0, y0, x0 + w, y0 + h)
        placed.append({"name": name, "role": role, "style": style, "height": height, "contrast": contrast,
                       "rotation": rotation, "img": img, "canvas": canvas,
                       "box": (x0 + bx0, y0 + by0, x0 + bx1, y0 + by1)})
    return placed


def boxes_touch(a, b):
    """True if two boxes overlap or sit closer than MARGIN."""
    return not (a[2] + MARGIN <= b[0] or b[2] + MARGIN <= a[0] or a[3] + MARGIN <= b[1] or b[3] + MARGIN <= a[1])


def draw_card(placed, paper):
    card = Image.new("RGB", CARD_SIZE, paper)
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, CARD_SIZE[0] - 1, HEADER_HEIGHT], fill=HEADER_COLOUR)
    d.rectangle([0, 0, CARD_SIZE[0] - 1, CARD_SIZE[1] - 1], outline=CARD_BORDER, width=2)
    for p in placed:
        card.paste(p["img"], p["canvas"][:2], p["img"])
    return card


def degrade(card, rng, np_rng):
    """Scan-like degradation: lighting gradient, noise, optional blur. Returns the image and its settings."""
    settings = {"gradient": round(rng.uniform(*GRADIENT_RANGE), 3), "gradient_angle_deg": rng.randint(0, 359),
                "noise_sigma": round(rng.uniform(*NOISE_SIGMA_RANGE), 2),
                "blur_radius": round(rng.uniform(*BLUR_RADIUS_RANGE), 2) if rng.random() < BLUR_RATE else 0.0,
                "jpeg_quality": rng.randint(*JPEG_QUALITY_RANGE)}
    pixels = np.asarray(card, dtype=np.float32)
    h, w = pixels.shape[:2]
    angle = np.deg2rad(settings["gradient_angle_deg"])
    yy, xx = np.mgrid[0:h, 0:w]
    position = (xx / (w - 1) - 0.5) * np.cos(angle) + (yy / (h - 1) - 0.5) * np.sin(angle)  # about -0.7..0.7
    pixels *= (1 + 2 * settings["gradient"] * position)[:, :, None]
    pixels += np_rng.normal(0, settings["noise_sigma"], pixels.shape) if settings["noise_sigma"] > 0 else 0
    out = Image.fromarray(np.clip(np.rint(pixels), 0, 255).astype(np.uint8))
    if settings["blur_radius"] > 0:
        out = out.filter(ImageFilter.GaussianBlur(settings["blur_radius"]))
    return out, settings


# ---------------------------------------------------------------- split

def assign_splits(rng, cards):
    """Fixed 60/20/20 split, stratified by field department and whether any item was omitted."""
    strata = {}
    for c in cards:
        strata.setdefault((c["field_department"], c["n_omitted"] > 0), []).append(c)
    ordered = []
    for key in sorted(strata, key=str):
        group = strata[key]
        rng.shuffle(group)
        ordered.extend(group)
    for i, c in enumerate(ordered):
        c["split"] = SPLIT_PATTERN[i % len(SPLIT_PATTERN)]


# ---------------------------------------------------------------- outputs

def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_reference_icons():
    """A clean, upright, high-contrast copy of each development style and background object."""
    REFERENCE_DIR.mkdir(exist_ok=True)
    for name in ICONS + BACKGROUND_OBJECTS:
        for style in (DEVELOPMENT_STYLES if name in ICONS else ["a"]):
            tile = Image.new("RGB", (64, 64), PAPER_RGB)
            img = render_object(name, style, 64, 1.0, 0.0, PAPER_RGB)
            tile.paste(img, (0, 0), img)
            prefix = "" if name in ICONS else "background_"
            tile.save(REFERENCE_DIR / f"{prefix}{name}_{style}.png" if name in ICONS
                      else REFERENCE_DIR / f"{prefix}{name}.png")


def save_example_grid(cards, path):
    """Contact sheet of example training cards with their labels."""
    font = ImageFont.load_default()
    thumb_w, thumb_h, gap, line_h, caption_lines = 240, 160, 10, 13, 5
    cell_w, cell_h = thumb_w + gap, thumb_h + caption_lines * line_h + gap
    cols, rows = 3, (len(cards) + 2) // 3
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for i, c in enumerate(cards):
        x, y = (i % cols) * cell_w, (i // cols) * cell_h
        sheet.paste(Image.open(IMAGE_DIR / c["file_name"]).resize((thumb_w, thumb_h), Image.LANCZOS), (x, y))
        present = ", ".join(i.replace("_", " ") for i in ICONS if c[f"present_{i}"]) or "no kit icons"
        omitted = ", ".join(i.replace("_", " ") for i in ICONS if c[f"omitted_{i}"]) or "none"
        unknown = ", ".join(i.replace("_", " ") for i in ICONS if not c[f"expectation_known_{i}"])
        lines = [(line, (0, 0, 0)) for line in wrap_text(d, f"{c['card_id']}: {present}", font, thumb_w - 8)]
        lines += [(line, (170, 0, 0) if c["n_omitted"] else (90, 90, 90))
                  for line in wrap_text(d, f"omitted: {omitted}", font, thumb_w - 8)]
        if unknown:
            lines += [(line, (0, 90, 170)) for line in wrap_text(d, f"expectation unknown: {unknown}", font, thumb_w - 8)]
        for n, (line, colour) in enumerate(lines[:caption_lines]):
            d.text((x + 4, y + thumb_h + 3 + n * line_h), line, fill=colour, font=font)
    sheet.save(path)


def wrap_text(d, text, font, max_width):
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if current and d.textlength(trial, font=font) > max_width:
            lines.append(current)
            current = word
        else:
            current = trial
    return lines + [current]


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows({k: ("" if row[k] is None else row[k]) for k in fields} for row in rows)


def main():
    rng = random.Random(SEED)
    np_rng = np.random.default_rng(SEED)
    IMAGE_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    kits = load_kits()
    selected = sorted(rng.sample(sorted(kits), N_CARDS))   # reproducible choice of employees
    cards, instances, render_hashes = [], [], []
    for n, employee_id in enumerate(selected, start=1):
        kit = kits[employee_id]
        card_id = f"KIT-{n:04d}"
        paper = tuple(int(v + rng.randint(-PAPER_TINT, PAPER_TINT)) for v in PAPER_RGB)
        # Only items known to be expected can be packed; unknown expectations are never treated as "not needed"
        packable = [i for i in ICONS if kit["known"][i] and kit["expected"][i] == 1]
        shown = [i for i in packable if rng.random() >= OMISSION_RATE]
        n_background = rng.choices(*BACKGROUND_OBJECT_COUNTS)[0]
        objects = [(i, "kit_item") for i in shown] + [(rng.choice(BACKGROUND_OBJECTS), "background_object")
                                                       for _ in range(n_background)]
        rng.shuffle(objects)   # placement order does not follow the item list
        placed = place_objects(rng, objects, paper)
        image, quality = degrade(draw_card(placed, paper), rng, np_rng)
        file_name = f"{card_id}.jpg"
        image.save(IMAGE_DIR / file_name, quality=quality["jpeg_quality"])

        card = {"card_id": card_id, "employee_id": employee_id, "access_request_id": kit["access_request_id"],
                "equipment_request_id": kit["equipment_request_id"], "file_name": file_name,
                "hiring_department": kit["hiring_department"],
                "field_department": "" if not kit["hiring_department"] else kit["hiring_department"] in FIELD_DEPARTMENTS,
                "paper_r": paper[0], "paper_g": paper[1], "paper_b": paper[2], **quality,
                "n_background_objects": n_background}
        for i in ICONS:
            card[f"expectation_known_{i}"] = int(kit["known"][i])
            card[f"expected_{i}"] = kit["expected"][i]          # blank when the expectation is unknown
            card[f"present_{i}"] = int(i in shown)
            card[f"omitted_{i}"] = int(i in packable and i not in shown)
        card["n_expected_known"] = len(packable)
        card["n_present"], card["n_omitted"] = len(shown), len(packable) - len(shown)
        cards.append(card)

        for p in placed:
            x0, y0, x1, y1 = p["box"]
            render_hashes.append((card_id, p["name"], hashlib.sha256(p["img"].tobytes()).hexdigest()))
            instances.append({"card_id": card_id, "role": p["role"], "object": p["name"], "style": p["style"],
                              "height_px": p["height"], "size_band": band(p["height"], SIZE_BANDS),
                              "contrast": p["contrast"], "contrast_band": band(p["contrast"], CONTRAST_BANDS),
                              "rotation_deg": p["rotation"], "x0": x0, "y0": y0, "x1": x1, "y1": y1})

    assign_splits(rng, cards)
    split_of = {c["card_id"]: c["split"] for c in cards}
    for inst in instances:
        inst["split"] = split_of[inst["card_id"]]

    card_fields = (["card_id", "employee_id", "access_request_id", "equipment_request_id", "file_name", "split",
                    "hiring_department", "field_department"]
                   + [f"expectation_known_{i}" for i in ICONS] + [f"expected_{i}" for i in ICONS]
                   + [f"present_{i}" for i in ICONS] + [f"omitted_{i}" for i in ICONS]
                   + ["n_expected_known", "n_present", "n_omitted", "n_background_objects",
                      "paper_r", "paper_g", "paper_b", "gradient", "gradient_angle_deg", "noise_sigma",
                      "blur_radius", "jpeg_quality"])
    write_csv(HERE / "manifest.csv", cards, card_fields)
    write_csv(HERE / "icon_instances.csv", instances,
              ["card_id", "split", "role", "object", "style", "height_px", "size_band", "contrast",
               "contrast_band", "rotation_deg", "x0", "y0", "x1", "y1"])
    save_reference_icons()

    # Duplicate check: identical rendered drawings (before degradation) shared across splits
    by_hash = {}
    for card_id, name, h in render_hashes:
        by_hash.setdefault(h, set()).add(split_of[card_id])
    cross_split = sum(1 for splits in by_hash.values() if len(splits) > 1)

    info = {"seed": SEED, "n_cards": N_CARDS, "latest_start_date": LATEST_START_DATE.isoformat(),
            "input": str(CLEANED_REQUESTS.relative_to(HERE.parent)), "input_sha256": sha256_of(CLEANED_REQUESTS),
            "input_record": json.loads(CLEANED_INFO.read_text()) if CLEANED_INFO.exists() else None,
            "eligible_employees": len(kits), "rendered_drawings": len(render_hashes),
            "distinct_rendered_drawings": len(by_hash), "drawings_shared_across_splits": cross_split}
    (OUTPUT_DIR / "generation_info.json").write_text(json.dumps(info, indent=2))

    train = [c for c in cards if c["split"] == "train"]
    picks = [c for c in (next((c for c in train if c["n_expected_known"] == 0), None),
                         next((c for c in train if not all(c[f"expectation_known_{i}"] for i in ICONS)), None))
             if c is not None]
    picks += [c for c in train if c["n_omitted"] > 0 and c not in picks][:3]
    picks += [c for c in train if c["n_background_objects"] > 0 and c not in picks][:2]
    picks += [c for c in train if c["n_present"] >= 4 and c not in picks][:2]
    save_example_grid(picks, OUTPUT_DIR / "example_cards.png")

    # ------------------------------------------------------------ summary
    kit_items = [x for x in instances if x["role"] == "kit_item"]
    print(f"Eligible employees: {len(kits)}; cards: {len(cards)}; kit icons: {len(kit_items)}; "
          f"background objects: {len(instances) - len(kit_items)}")
    print("Split:", dict(Counter(c["split"] for c in cards)))
    print("Cards with nothing known to be expected:", sum(c["n_expected_known"] == 0 for c in cards))
    print("Unknown expectations:", {i: sum(not c[f"expectation_known_{i}"] for c in cards) for i in ICONS})
    print(f"{'icon':14}{'expected':>9}{'present':>9}{'omitted':>9}")
    for i in ICONS:
        print(f"{i:14}{sum(c[f'expected_{i}'] == 1 for c in cards):>9}{sum(c[f'present_{i}'] for c in cards):>9}"
              f"{sum(c[f'omitted_{i}'] for c in cards):>9}")
    print("Omitted items by split:",
          {s: sum(c["n_omitted"] for c in cards if c["split"] == s) for s in ("train", "validation", "test")})
    print("Size bands:", dict(Counter(x["size_band"] for x in kit_items)),
          "| contrast bands:", dict(Counter(x["contrast_band"] for x in kit_items)),
          "| styles:", dict(Counter(x["style"] for x in kit_items)))
    print(f"Rendered drawings: {len(render_hashes)}, distinct: {len(by_hash)}, shared across splits: {cross_split}")


if __name__ == "__main__":
    main()
