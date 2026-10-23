"""VERSION 2 CANDIDATE - make the provisional cleaned request file used by the kit-card generator.

Calls the shared cleaning code that the revised AIDA 1141 Exercise 03 will also use. Run from the repository root:

    python candidate-v2/make_provisional_cleaned.py
"""
import sys
from pathlib import Path

sys.path.insert(0, "AIDA-1141/project-labs/03-data-quality-checks")
from clean_requests import clean_files  # noqa: E402

EXPORT = Path("AIDA-1141/project-labs/02-synthetic-request-records/data")
cleaned, info = clean_files(EXPORT / "requests.csv", EXPORT / "status_events.csv",
                            Path("candidate-v2/provisional/requests_cleaned.csv"))
print(f"Cleaning version {info['cleaning_version']}: {info['rows_in']} rows in, {info['rows_out']} out")
print("Unresolved:", {f: v for f, v in info["unresolved"].items() if v["blank"] or v["unmapped"]})
