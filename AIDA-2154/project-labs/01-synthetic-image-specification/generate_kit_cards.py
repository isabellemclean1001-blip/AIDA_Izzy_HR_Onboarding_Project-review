"""Generate synthetic onboarding-kit card images for AIDA 2154.

Each fictional employee from AIDA 1141 Exercise 02 gets one kit card. The card
shows icons for the first-day items packed in their kit. The expected kit comes
from the employee's request records; some expected items are left off on purpose
to simulate packing mistakes. Icon size, position, and contrast vary per icon.

All images and labels are computer-generated. Rates such as the omission rate are
invented settings, not evidence about real onboarding kits.

Run from this folder:  python generate_kit_cards.py
Requires: Pillow (standard library otherwise).
"""

import csv
import random
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- settings
SEED = 2026
REQUESTS_CSV = Path("../../../AIDA-1141/project-labs/02-synthetic-request-records/data/requests.csv")
IMAGE_DIR = Path("images")
REFERENCE_DIR = Path("reference_icons")
OUTPUT_DIR = Path("outputs")

ICONS = ["access_badge", "safety_vest", "hard_hat", "laptop", "phone"]
FIELD_DEPARTMENTS = {"Parks", "Transit", "Utilities"}
OMISSION_RATE = 0.15            # chance each expected item is left off the card (invented)

CARD_SIZE = (480, 320)          # width, height in pixels
CARD_BACKGROUND = (236, 236, 230)
CARD_BORDER = (120, 120, 120)
HEADER_HEIGHT = 36
HEADER_COLOUR = (90, 110, 130)
MARGIN = 14                     # gap between icons and from card edges

BASE_ICON_SIZE = 64             # icon height at "medium" scale
SCALE_LEVELS = {"small": 0.6, "medium": 1.0, "large": 1.4}
CONTRAST_LEVELS = {"high": 1.0, "medium": 0.55, "low": 0.25}  # share of icon colour kept vs background
SUPERSAMPLE = 4                 # draw large, then shrink for smooth edges

SPLIT_PATTERN = ["train", "train", "train", "validation", "test"]  # 60 / 20 / 20


# ---------------------------------------------------------------- icon drawing
# Each function draws one icon on a transparent square canvas of side s.

def draw_access_badge(d, s):
    d.rounded_rectangle([0.22 * s, 0.12 * s, 0.78 * s, 0.95 * s], radius=0.06 * s, fill=(40, 90, 170))
    d.rounded_rectangle([0.42 * s, 0.03 * s, 0.58 * s, 0.17 * s], radius=0.03 * s, fill=(70, 70, 70))  # clip
    d.rectangle([0.34 * s, 0.26 * s, 0.66 * s, 0.56 * s], fill=(245, 245, 245))                     # blank photo area
    d.rectangle([0.32 * s, 0.66 * s, 0.68 * s, 0.71 * s], fill=(245, 245, 245))                     # text lines
    d.rectangle([0.32 * s, 0.78 * s, 0.58 * s, 0.83 * s], fill=(245, 245, 245))


def draw_safety_vest(d, s):
    body = [(0.18 * s, 0.10 * s), (0.38 * s, 0.10 * s), (0.50 * s, 0.38 * s), (0.62 * s, 0.10 * s),
            (0.82 * s, 0.10 * s), (0.90 * s, 0.92 * s), (0.10 * s, 0.92 * s)]
    d.polygon(body, fill=(245, 130, 30))
    d.rectangle([0.13 * s, 0.55 * s, 0.87 * s, 0.62 * s], fill=(200, 200, 200))  # reflective stripes
    d.rectangle([0.11 * s, 0.74 * s, 0.89 * s, 0.81 * s], fill=(200, 200, 200))


def draw_hard_hat(d, s):
    d.chord([0.16 * s, 0.18 * s, 0.84 * s, 0.98 * s], start=180, end=360, fill=(240, 200, 30))  # dome
    d.rectangle([0.46 * s, 0.20 * s, 0.54 * s, 0.58 * s], fill=(215, 175, 20))                 # ridge
    d.rounded_rectangle([0.05 * s, 0.56 * s, 0.95 * s, 0.68 * s], radius=0.04 * s, fill=(215, 175, 20))  # brim


def draw_laptop(d, s):
    d.rounded_rectangle([0.14 * s, 0.18 * s, 0.86 * s, 0.68 * s], radius=0.04 * s, fill=(60, 60, 70))
    d.rectangle([0.20 * s, 0.24 * s, 0.80 * s, 0.62 * s], fill=(110, 150, 200))   # screen
    d.polygon([(0.06 * s, 0.82 * s), (0.14 * s, 0.70 * s), (0.86 * s, 0.70 * s), (0.94 * s, 0.82 * s)],
              fill=(80, 80, 90))                                                   # base


def draw_phone(d, s):
    d.rounded_rectangle([0.30 * s, 0.06 * s, 0.70 * s, 0.94 * s], radius=0.07 * s, fill=(60, 60, 70))
    d.rectangle([0.34 * s, 0.15 * s, 0.66 * s, 0.80 * s], fill=(110, 150, 200))   # screen
    d.ellipse([0.46 * s, 0.84 * s, 0.54 * s, 0.90 * s], fill=(150, 150, 160))     # button


DRAWERS = {
    "access_badge": draw_access_badge,
    "safety_vest": draw_safety_vest,
    "hard_hat": draw_hard_hat,
    "laptop": draw_laptop,
    "phone": draw_phone,
}


def render_icon(icon, size, contrast):
    """Return an RGBA icon of the given pixel size, with colours blended toward the card background."""
    big = Image.new("RGBA", (size * SUPERSAMPLE, size * SUPERSAMPLE), (0, 0, 0, 0))
    DRAWERS[icon](ImageDraw.Draw(big), size * SUPERSAMPLE)
    img = big.resize((size, size), Image.LANCZOS)
    background = Image.new("RGB", img.size, CARD_BACKGROUND)
    out = Image.blend(background, img.convert("RGB"), CONTRAST_LEVELS[contrast])
    out.putalpha(img.getchannel("A"))
    return out


# ---------------------------------------------------------------- kit contents

def load_expected_kits():
    """Expected first-day items per employee, from the clean Exercise 02 request records."""
    with open(REQUESTS_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    kits = {}
    for r in rows:
        kit = kits.setdefault(r["employee_id"], {
            "hiring_department": r["hiring_department"],
            "expected": set(),
            "device_unknown": False,
            "access_request_id": "",
            "equipment_request_id": "",
        })
        if r["task_type"] == "workplace_access":
            kit["expected"].add("access_badge")
            kit["access_request_id"] = r["request_id"]
        if r["task_type"] == "equipment_setup":
            kit["equipment_request_id"] = r["request_id"]
            if r["equipment_item"] in ("laptop", "phone"):
                kit["expected"].add(r["equipment_item"])
            else:
                kit["device_unknown"] = True  # equipment task with a blank item: device can't be drawn
        if r["hiring_department"] in FIELD_DEPARTMENTS:
            kit["expected"].update({"safety_vest", "hard_hat"})
    return dict(sorted(kits.items()))


def place_icons(rng, icons):
    """Pick a size, contrast, and non-overlapping position for each icon. Returns a list of dicts."""
    placed = []
    for icon in icons:
        scale = rng.choice(list(SCALE_LEVELS))
        contrast = rng.choice(list(CONTRAST_LEVELS))
        size = round(BASE_ICON_SIZE * SCALE_LEVELS[scale])
        for _ in range(1000):
            x0 = rng.randint(MARGIN, CARD_SIZE[0] - MARGIN - size)
            y0 = rng.randint(HEADER_HEIGHT + MARGIN, CARD_SIZE[1] - MARGIN - size)
            box = (x0, y0, x0 + size, y0 + size)
            if all(not boxes_touch(box, p["box"]) for p in placed):
                break
        else:
            raise RuntimeError("Could not place icon without overlap; enlarge the card or shrink icons.")
        placed.append({"icon": icon, "scale": scale, "contrast": contrast, "size": size, "box": box})
    return placed


def boxes_touch(a, b):
    """True if two boxes overlap or sit closer than MARGIN."""
    return not (a[2] + MARGIN <= b[0] or b[2] + MARGIN <= a[0] or a[3] + MARGIN <= b[1] or b[3] + MARGIN <= a[1])


def draw_card(placed):
    card = Image.new("RGB", CARD_SIZE, CARD_BACKGROUND)
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, CARD_SIZE[0] - 1, HEADER_HEIGHT], fill=HEADER_COLOUR)
    d.rectangle([0, 0, CARD_SIZE[0] - 1, CARD_SIZE[1] - 1], outline=CARD_BORDER, width=2)
    for p in placed:
        icon_img = render_icon(p["icon"], p["size"], p["contrast"])
        card.paste(icon_img, p["box"][:2], icon_img)
    return card


# ---------------------------------------------------------------- split

def assign_splits(rng, cards):
    """Fixed 60/20/20 split, stratified by field department and whether any item was omitted."""
    strata = {}
    for c in cards:
        strata.setdefault((c["field_department"], c["n_omitted"] > 0), []).append(c)
    ordered = []
    for key in sorted(strata):
        group = strata[key]
        rng.shuffle(group)
        ordered.extend(group)
    for i, c in enumerate(ordered):
        c["split"] = SPLIT_PATTERN[i % len(SPLIT_PATTERN)]


# ---------------------------------------------------------------- outputs

def save_reference_icons():
    """One clean, high-contrast, medium-size copy of each icon, for the label guide."""
    REFERENCE_DIR.mkdir(exist_ok=True)
    for icon in ICONS:
        tile = Image.new("RGB", (BASE_ICON_SIZE, BASE_ICON_SIZE), CARD_BACKGROUND)
        icon_img = render_icon(icon, BASE_ICON_SIZE, "high")
        tile.paste(icon_img, (0, 0), icon_img)
        tile.save(REFERENCE_DIR / f"{icon}.png")


def save_example_grid(cards, path):
    """Contact sheet of example cards with their labels, for the README and data card."""
    font = ImageFont.load_default()
    thumb_w, thumb_h, gap, line_h, caption_lines = 240, 160, 10, 13, 5
    cell_w, cell_h = thumb_w + gap, thumb_h + caption_lines * line_h + gap
    cols, rows = 3, (len(cards) + 2) // 3
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for i, c in enumerate(cards):
        x, y = (i % cols) * cell_w, (i // cols) * cell_h
        sheet.paste(Image.open(IMAGE_DIR / c["file_name"]).resize((thumb_w, thumb_h), Image.LANCZOS), (x, y))
        present = ", ".join(i.replace("_", " ") for i in ICONS if c[f"present_{i}"]) or "no icons"
        omitted = ", ".join(i.replace("_", " ") for i in ICONS if c[f"omitted_{i}"]) or "none"
        note = " (device unknown)" if c["device_unknown"] else ""
        lines = [(line, (0, 0, 0)) for line in wrap_text(d, f"{c['card_id']}{note}: {present}", font, thumb_w - 8)]
        lines += [(line, (170, 0, 0) if c["n_omitted"] else (90, 90, 90))
                  for line in wrap_text(d, f"omitted: {omitted}", font, thumb_w - 8)]
        for n, (line, colour) in enumerate(lines[:caption_lines]):
            d.text((x + 4, y + thumb_h + 3 + n * line_h), line, fill=colour, font=font)
    sheet.save(path)


def wrap_text(d, text, font, max_width):
    """Split text into lines that fit within max_width pixels."""
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
        w.writerows(rows)


def main():
    rng = random.Random(SEED)
    IMAGE_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    cards, instances = [], []
    for n, (employee_id, kit) in enumerate(load_expected_kits().items(), start=1):
        card_id = f"KIT-{n:04d}"
        expected = [i for i in ICONS if i in kit["expected"]]
        shown = [i for i in expected if rng.random() >= OMISSION_RATE]
        rng.shuffle(shown)  # placement order does not follow the icon list
        placed = place_icons(rng, shown)
        file_name = f"{card_id}.png"
        draw_card(placed).save(IMAGE_DIR / file_name)

        card = {
            "card_id": card_id,
            "employee_id": employee_id,
            "access_request_id": kit["access_request_id"],
            "equipment_request_id": kit["equipment_request_id"],
            "file_name": file_name,
            "hiring_department": kit["hiring_department"],
            "field_department": kit["hiring_department"] in FIELD_DEPARTMENTS,
            "device_unknown": kit["device_unknown"],
        }
        for i in ICONS:
            card[f"expected_{i}"] = int(i in expected)
            card[f"present_{i}"] = int(i in shown)
            card[f"omitted_{i}"] = int(i in expected and i not in shown)
        card["n_expected"], card["n_present"] = len(expected), len(shown)
        card["n_omitted"] = len(expected) - len(shown)
        cards.append(card)

        for p in placed:
            x0, y0, x1, y1 = p["box"]
            instances.append({"card_id": card_id, "icon": p["icon"], "scale_level": p["scale"],
                              "size_px": p["size"], "contrast_level": p["contrast"],
                              "x0": x0, "y0": y0, "x1": x1, "y1": y1})

    assign_splits(rng, cards)
    split_of = {c["card_id"]: c["split"] for c in cards}
    for inst in instances:
        inst["split"] = split_of[inst["card_id"]]

    card_fields = (["card_id", "employee_id", "access_request_id", "equipment_request_id", "file_name", "split", "hiring_department", "field_department",
                    "device_unknown"]
                   + [f"expected_{i}" for i in ICONS] + [f"present_{i}" for i in ICONS]
                   + [f"omitted_{i}" for i in ICONS] + ["n_expected", "n_present", "n_omitted"])
    write_csv("manifest.csv", cards, card_fields)
    write_csv("icon_instances.csv", instances,
              ["card_id", "split", "icon", "scale_level", "size_px", "contrast_level", "x0", "y0", "x1", "y1"])
    save_reference_icons()

    # Examples from training cards only, so validation and test images stay held back.
    # An empty kit, a device-unknown kit, then cards with omissions and mixed variation;
    # a case is skipped if this seed produces no training card for it.
    train = [c for c in cards if c["split"] == "train"]
    picks = [c for c in (next((c for c in train if c["n_expected"] == 0), None),
                         next((c for c in train if c["device_unknown"]), None)) if c is not None]
    picks += [c for c in train if c["n_omitted"] > 0 and c not in picks][:4]
    picks += [c for c in train if c["n_present"] >= 4 and c not in picks][:3]
    save_example_grid(picks, OUTPUT_DIR / "example_cards.png")

    # ------------------------------------------------------------ summary
    print(f"Cards: {len(cards)}  Icon instances: {len(instances)}")
    print("Split:", dict(Counter(c["split"] for c in cards)))
    print("Empty kits (nothing expected):", sum(c["n_expected"] == 0 for c in cards))
    print("Device unknown (blank equipment item):", sum(c["device_unknown"] for c in cards))
    print(f"{'icon':14}{'expected':>9}{'present':>9}{'omitted':>9}")
    for i in ICONS:
        print(f"{i:14}{sum(c[f'expected_{i}'] for c in cards):>9}{sum(c[f'present_{i}'] for c in cards):>9}"
              f"{sum(c[f'omitted_{i}'] for c in cards):>9}")
    print("Omitted items by split:",
          {s: sum(c["n_omitted"] for c in cards if c["split"] == s) for s in ("train", "validation", "test")})
    print("Cards with any omission by split:",
          {s: sum(c["n_omitted"] > 0 for c in cards if c["split"] == s) for s in ("train", "validation", "test")})
    print("Scale levels:", dict(Counter(x["scale_level"] for x in instances)))
    print("Contrast levels:", dict(Counter(x["contrast_level"] for x in instances)))


if __name__ == "__main__":
    main()
