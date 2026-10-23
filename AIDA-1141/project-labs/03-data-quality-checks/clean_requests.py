"""Shared cleaning rules for the version 2 synthetic onboarding request export.

One implementation used by every step that needs cleaned requests (AIDA 1141 Exercise 03, and the
AIDA 2154 kit-card generator), so the rules cannot drift apart.

Rules use only the export itself, documented mappings, and the trusted files in data/
(status_events.csv). They never read evaluation_only/: the answer key is for evaluating
cleaning afterwards, not for repairing values. Values with no trusted source stay blank.
"""

import hashlib
import json
from pathlib import Path

import pandas as pd

CLEANING_VERSION = "0.1-provisional"

# Allowed values after cleaning
ALLOWED = {
    "task_type": ["payroll_setup", "system_access", "workplace_access", "equipment_setup", "orientation_scheduling"],
    "responsible_team": ["IT", "Payroll", "Facilities", "Manager"],
    "hiring_department": ["Parks", "Transit", "Recreation", "Finance", "Utilities", "Administration"],
    "submitted_hiring_department": ["Parks", "Transit", "Recreation", "Finance", "Utilities", "Administration"],
    "employee_type": ["permanent", "temporary", "seasonal"],
    "intake_channel": ["web_form", "email", "phone"],
}
# Documented spellings that do not match an allowed value after trimming, lower-casing, and spaces -> "_"
MAPPINGS = {
    "task_type": {"equipment_set-up": "equipment_setup", "orientation": "orientation_scheduling"},
    "responsible_team": {"i.t.": "IT", "facilites": "Facilities", "mgr": "Manager"},
    "hiring_department": {"prks": "Parks", "parks_dept": "Parks", "transit_services": "Transit", "rec": "Recreation",
                          "recreaton": "Recreation", "finanace": "Finance", "utilties": "Utilities",
                          "admin": "Administration"},
    "employee_type": {"perm": "permanent", "temp": "temporary"},
    "intake_channel": {"webform": "web_form", "e-mail": "email", "phone_call": "phone"},
}
MAPPINGS["submitted_hiring_department"] = MAPPINGS["hiring_department"]
EMPLOYEE_LEVEL = ["employee_type", "hiring_department"]  # one value per employee in this workflow
TIME_FORMAT = "%Y-%m-%dT%H:%M"


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def standardize(value, field):
    """Map one recorded category value to its allowed form; blank stays blank; unknown spellings are flagged."""
    if value.strip() == "":
        return ""
    key = value.strip().lower().replace(" ", "_")
    for allowed in ALLOWED[field]:
        if key == allowed.lower():
            return allowed
    return MAPPINGS[field].get(key, f"UNMAPPED:{value}")


def clean(raw, events):
    """Return (cleaned requests, change log). Both inputs are DataFrames read with dtype=str and no NA conversion."""
    log = []
    cleaned = raw.drop_duplicates().copy()
    log.append({"step": "exact_duplicates_removed", "field": "", "rows": len(raw) - len(cleaned)})

    for field in ALLOWED:
        before = cleaned[field].copy()
        cleaned[field] = before.map(lambda v: standardize(v, field))
        log.append({"step": "categories_standardized", "field": field, "rows": int((before != cleaned[field]).sum())})

    # Employee-level fields: fill a blank only when the employee's other rows agree on one value
    for field in EMPLOYEE_LEVEL:
        known = cleaned[cleaned[field] != ""].groupby("employee_id")[field].agg(lambda s: s.unique().tolist())
        single = known[known.map(len) == 1].map(lambda v: v[0])
        blank = cleaned[field] == ""
        filled = cleaned.loc[blank, "employee_id"].map(single)
        cleaned.loc[blank & filled.notna(), field] = filled.dropna()
        log.append({"step": "employee_level_value_filled", "field": field, "rows": int(filled.notna().sum())})

    # Submission time: repair invalid or out-of-range values from the request's 'submitted' event (trusted source)
    parsed = pd.to_datetime(cleaned["submitted_at"], format=TIME_FORMAT, errors="coerce")
    event_time = events[events["event_type"] == "submitted"].set_index("request_id")["event_at"]
    bad = parsed.isna() | (parsed.dt.year > 2026) | (parsed.dt.year < 2025)
    cleaned.loc[bad, "submitted_at"] = cleaned.loc[bad, "request_id"].map(event_time)
    log.append({"step": "submitted_at_repaired_from_events", "field": "submitted_at", "rows": int(bad.sum())})

    # Submitted start date: an impossible date has no trusted source for what was written, so it becomes blank
    parsed_start = pd.to_datetime(cleaned["submitted_start_date"], format="%Y-%m-%d", errors="coerce")
    invalid_start = (cleaned["submitted_start_date"] != "") & parsed_start.isna()
    cleaned.loc[invalid_start, "submitted_start_date"] = ""
    log.append({"step": "invalid_submitted_start_date_blanked", "field": "submitted_start_date",
                "rows": int(invalid_start.sum())})

    return cleaned, pd.DataFrame(log)


def unresolved_counts(cleaned):
    """Blank or unmapped values left in the cleaned fields, by field."""
    counts = {}
    for field in ALLOWED:
        counts[field] = {"blank": int((cleaned[field] == "").sum()),
                         "unmapped": int(cleaned[field].str.startswith("UNMAPPED:").sum())}
    return counts


def clean_files(requests_path, events_path, output_path):
    """Clean the export, write the cleaned file and a JSON record of how it was made, and return both."""
    raw = pd.read_csv(requests_path, dtype=str, keep_default_na=False)
    events = pd.read_csv(events_path, dtype=str, keep_default_na=False)
    cleaned, log = clean(raw, events)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(output_path, index=False)
    info = {
        "cleaning_version": CLEANING_VERSION,
        "source_requests": str(requests_path), "source_requests_sha256": sha256_of(requests_path),
        "source_events": str(events_path), "source_events_sha256": sha256_of(events_path),
        "output": str(output_path), "output_sha256": sha256_of(output_path),
        "rows_in": len(raw), "rows_out": len(cleaned),
        "steps": log.to_dict("records"),
        "unresolved": unresolved_counts(cleaned),
    }
    output_path.with_name(output_path.stem + "_info.json").write_text(json.dumps(info, indent=2))
    return cleaned, info
