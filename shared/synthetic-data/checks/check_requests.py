"""Data version 2: consistency checks on the request export, and a separate evaluation of cleaning.

The cleaning evaluation reads the answer key only AFTER cleaning has run (cleaning/make_cleaned.py);
the cleaner itself never reads evaluation_only/. Run from anywhere:

    python shared/synthetic-data/checks/check_requests.py

Writes checks/results/request_checks.csv, checks/results/cleaning_evaluation.csv, and
checks/results/cleaning_evaluation_info.json (which cleaned file the evaluation measured).
"""
import hashlib
import importlib.util
import json
from pathlib import Path

import pandas as pd

SD = Path(__file__).resolve().parent.parent        # shared/synthetic-data
ROOT = SD / "requests"
OUT = SD / "checks" / "results"
OUT.mkdir(exist_ok=True)
spec = importlib.util.spec_from_file_location("gen", ROOT / "generate_requests.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

EXTRACT = pd.Timestamp(gen.EXTRACT_AT)
read = lambda path: pd.read_csv(path, dtype=str, keep_default_na=False)
raw = read(ROOT / "data/requests.csv")
key = read(ROOT / "evaluation_only/data_issues.csv")
events = pd.read_csv(ROOT / "data/status_events.csv", parse_dates=["event_at"])
assessments = read(ROOT / "data/assessments.csv")
distinct = raw.drop_duplicates()


def working(times):
    """Business day (not a closure date) and 08:00-16:30."""
    minutes = times.dt.hour * 60 + times.dt.minute
    return (times.dt.dayofweek < 5) & ~times.dt.date.isin(gen.HOLIDAYS) & minutes.between(480, 990)


latest = events.sort_values(["request_id", "event_at", "event_id"]).groupby("request_id").tail(1)
latest_status = latest.set_index("request_id")["status_after"]
unfinished = distinct["team_completed_at"] == ""
deadline = pd.to_datetime(distinct["confirmed_start_date"], errors="coerce") + pd.Timedelta(hours=8)
info_incomplete = distinct["info_complete_at"] == ""
staff_events = events[events["event_type"].isin(["info_requested", "assigned_to_team", "team_completed",
                                                 "completion_confirmed"])]["event_at"]
checks = {
    "Answer key matches the raw export row by row": all(
        raw.iloc[int(k.export_row_number) - 2]["request_id"] == k.request_id
        and (not k.field or raw.iloc[int(k.export_row_number) - 2][k.field] == k.recorded_value)
        for k in key.itertuples()),
    "Exact duplicate rows in the export equal the key's duplicate count":
        raw.duplicated().sum() == (key["issue_type"] == "exact_duplicate").sum(),
    "Request status equals the status of its latest event":
        (distinct.set_index("request_id")["status_at_extract"] == latest_status.reindex(distinct["request_id"]).values).all(),
    "Workflow timestamps that are present always parse": all(
        pd.to_datetime(distinct.loc[distinct[c] != "", c], format="%Y-%m-%dT%H:%M", errors="coerce").notna().all()
        for c in ["info_complete_at", "assigned_at", "team_completed_at", "completion_confirmed_at"]),
    "A blank team completion never has status complete":
        (distinct.loc[unfinished, "status_at_extract"] != "complete").all(),
    "Confirmed start date and department blank while information is incomplete":
        (distinct.loc[info_incomplete, ["confirmed_start_date", "hiring_department"]] == "").all().all(),
    "ready_by_start blank exactly when unfinished and the deadline is after the extract or not yet confirmed":
        ((distinct["ready_by_start"] == "") == (unfinished & ((deadline > EXTRACT) | deadline.isna()))).all(),
    "Unfinished with the deadline passed is recorded as not ready":
        (distinct.loc[unfinished & (deadline <= EXTRACT), "ready_by_start"] == "False").all(),
    "No event after the extract": (events["event_at"] <= EXTRACT).all(),
    "No assessment after the extract": (pd.to_datetime(assessments["assessed_at"]) <= EXTRACT).all(),
    "Coordinator and team events on business days, 08:00-16:30": working(staff_events).all(),
    "Checkpoint 1 within working hours": working(pd.to_datetime(
        assessments.loc[assessments["checkpoint"] == "checkpoint_1", "assessed_at"])).all(),
}
cleaned_rows = read(SD / "cleaning/output/requests_cleaned.csv")
checks["Cleaned file: confirmed start date and department blank while information is incomplete"] = (
    cleaned_rows.loc[cleaned_rows["info_complete_at"] == "", ["confirmed_start_date", "hiring_department"]] == "").all().all()
pd.Series(checks, name="passed").to_csv(OUT / "request_checks.csv")

# Cleaning evaluation (separate from cleaning): duplicates by row, field problems by request_id + field
cleaned = read(SD / "cleaning/output/requests_cleaned.csv").set_index("request_id")
fields = key[key["field"] != ""].copy()
fields["restored"] = [cleaned.at[k.request_id, k.field] == k.true_value for k in fields.itertuples()]
evaluation = (fields.groupby(["issue_type", "field"])["restored"].agg(problems="size", restored="sum").reset_index())
evaluation.loc[len(evaluation)] = {"issue_type": "exact_duplicate", "field": "(whole row)",
                                   "problems": int((key["issue_type"] == "exact_duplicate").sum()),
                                   "restored": int(len(raw) - len(cleaned) == (key["issue_type"] == "exact_duplicate").sum())
                                   * int((key["issue_type"] == "exact_duplicate").sum())}
evaluation["unresolved"] = evaluation["problems"] - evaluation["restored"]
evaluation.to_csv(OUT / "cleaning_evaluation.csv", index=False)
sha256_of = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
cleaning_record = json.loads((SD / "cleaning/output/requests_cleaned_info.json").read_text())
(OUT / "cleaning_evaluation_info.json").write_text(json.dumps({
    "evaluates": "cleaning/output/requests_cleaned.csv",
    "cleaned_sha256": sha256_of(SD / "cleaning/output/requests_cleaned.csv"),
    "cleaning_version": cleaning_record["cleaning_version"],
    "answer_key": "requests/evaluation_only/data_issues.csv",
    "answer_key_sha256": sha256_of(ROOT / "evaluation_only/data_issues.csv"),
    "evaluation": "checks/results/cleaning_evaluation.csv",
    "evaluation_sha256": sha256_of(OUT / "cleaning_evaluation.csv"),
}, indent=2) + "\n")

print(pd.Series(checks, name="passed").to_string())
print(evaluation.to_string(index=False))
print(f"Field problems restored: {fields['restored'].sum()} of {len(fields)}")

# Stop with an error if any consistency check failed, so a broken export or cleaned file can't pass quietly
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit("Failed checks:\n- " + "\n- ".join(failed))
