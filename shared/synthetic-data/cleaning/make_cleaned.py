"""Make the official cleaned request file for data version 2.

Run from anywhere:  python shared/synthetic-data/cleaning/make_cleaned.py
Writes cleaning/output/requests_cleaned.csv and requests_cleaned_info.json (how the file was made).
"""
from pathlib import Path

from clean_requests import clean_files

ROOT = Path(__file__).resolve().parent.parent          # shared/synthetic-data
EXPORT = Path("requests/data")                          # recorded relative to ROOT, so the record has no personal paths


def main():
    import os
    os.chdir(ROOT)
    cleaned, info = clean_files(EXPORT / "requests.csv", EXPORT / "status_events.csv",
                                Path("cleaning/output/requests_cleaned.csv"))
    print(f"Cleaning version {info['cleaning_version']}: {info['rows_in']} rows in, {info['rows_out']} out")
    print("Unresolved:", {f: v for f, v in info["unresolved"].items() if v["blank"] or v["unmapped"]})


if __name__ == "__main__":
    main()
