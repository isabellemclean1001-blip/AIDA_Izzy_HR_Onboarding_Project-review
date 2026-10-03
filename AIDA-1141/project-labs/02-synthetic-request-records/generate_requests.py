"""Generate synthetic onboarding request data for the fictional Town of Pinecrest.

Simulates about nine months of onboarding tasks with no coordinator
intervention, then writes the files described in data-dictionary.csv to ./data.
Uses only the Python standard library. Run with:

    python3 generate_requests.py

The same SEED always produces the same files.
"""

import csv
import random
from collections import Counter
from datetime import date, datetime, time, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Stage 0: Settings (all values are invented simulation assumptions)
# ---------------------------------------------------------------------------

SEED = 2026
N_EMPLOYEES = 500
# Employee start dates (always weekdays). Seasonal hires cluster in spring.
START_DATE_RANGE = (date(2026, 2, 23), date(2026, 9, 30))
SEASONAL_START_DATE_RANGE = (date(2026, 4, 1), date(2026, 6, 30))
# No request is submitted before this date (submissions are start date minus notice)
EARLIEST_SUBMISSION = date(2026, 1, 5)
OUTPUT_DIR = Path(__file__).parent / "data"

DEPARTMENTS = ["Parks", "Transit", "Recreation", "Finance", "Utilities", "Administration"]
DEPARTMENT_WEIGHTS = [0.22, 0.18, 0.18, 0.12, 0.15, 0.15]
FIELD_DEPARTMENTS = {"Parks", "Transit", "Utilities"}
SEASONAL_DEPARTMENTS = {"Parks", "Recreation"}

# Employee type probabilities: (permanent, temporary, seasonal)
TYPE_WEIGHTS_SEASONAL_DEPT = [0.35, 0.15, 0.50]
TYPE_WEIGHTS_OTHER_DEPT = [0.70, 0.25, 0.05]

# Business days of notice before the start date (first request submitted)
NOTICE_RANGE = {"permanent": (8, 30), "temporary": (3, 15), "seasonal": (2, 12)}
LATE_REQUEST_RATE = 0.03  # share of employees whose requests arrive on or after the start date

ROUTING_RULE = {
    "equipment_setup": "IT",
    "system_access": "IT",
    "payroll_setup": "Payroll",
    "workplace_access": "Facilities",
    "orientation_scheduling": "Manager",
}

# Normal business days each task type takes (min, max)
BASE_PROCESSING_DAYS = {
    "equipment_setup": (3, 6),
    "system_access": (2, 4),
    "payroll_setup": (2, 5),
    "workplace_access": (2, 5),
    "orientation_scheduling": (1, 4),
}

# Open tasks a team can handle before it slows down
TEAM_CAPACITY = {"IT": 30, "Payroll": 14, "Facilities": 12, "Manager": 16}

CHANNELS = ["web_form", "email", "phone"]
# Field departments phone or email more often; office departments use the web form
CHANNEL_WEIGHTS_FIELD = [0.40, 0.35, 0.25]
CHANNEL_WEIGHTS_OFFICE = [0.65, 0.28, 0.07]
# Task-type multipliers applied to (web_form, email, phone) before normalizing
CHANNEL_TASK_MULTIPLIER = {
    "payroll_setup": (1.6, 0.8, 0.5),           # usually entered through the HR web form
    "orientation_scheduling": (0.8, 1.5, 1.0),  # managers often arrange this by email
    "workplace_access": (0.9, 1.0, 1.5),        # keys and site access often requested by phone
    "equipment_setup": (1.0, 1.0, 1.0),
    "system_access": (1.0, 1.0, 1.0),
}
MISSING_RATE = {"web_form": 0.04, "email": 0.10, "phone": 0.14}
CONFLICT_ITEM_RATE = 0.03        # rule a: item listed on a non-equipment task
CONFLICT_START_DATE_RATE = 0.04  # rule c: start date differs from the employee's other requests

HIDDEN_DELAY_RATE = 0.18
HIDDEN_DELAY_DAYS = (1, 6)
DELAY_REASONS = ["staff_absence", "backlog", "vendor_delay"]

ERROR_COUNTS = {
    "duplicate_row": 8,
    "impossible_date": 5,
    "misspelled_category": 6,
    "invalid_channel": 4,
    "extra_blank": 8,
}

DAY_START = time(8, 0)
DAY_END = time(16, 30)
DEADLINE_TIME = time(8, 0)
TIME_FORMAT = "%Y-%m-%dT%H:%M"

rng = random.Random(SEED)


# ---------------------------------------------------------------------------
# Business-day helpers (Monday-Friday, no holidays)
# ---------------------------------------------------------------------------

def is_weekday(d):
    return d.weekday() < 5


def next_weekday(d):
    while not is_weekday(d):
        d += timedelta(days=1)
    return d


def add_business_days(d, n):
    """Move n weekdays forward (n > 0) or backward (n < 0) from date d."""
    step = 1 if n >= 0 else -1
    remaining = abs(n)
    while remaining:
        d += timedelta(days=step)
        if is_weekday(d):
            remaining -= 1
    return d


def weekdays_between(a, b):
    """Count weekdays in [a, b); 0 if b <= a."""
    count, d = 0, a
    while d < b:
        if is_weekday(d):
            count += 1
        d += timedelta(days=1)
    return count


def business_days_until_start(assessed, start):
    """Weekdays from the assessment day up to the day before the start date.

    Negative when assessed after the start date; 0 on the start date.
    """
    if assessed < start:
        return weekdays_between(assessed, start)
    return -weekdays_between(start, assessed)


def random_work_time(d):
    """A random time during working hours on date d."""
    start_min = DAY_START.hour * 60 + DAY_START.minute
    end_min = DAY_END.hour * 60 + DAY_END.minute
    minutes = rng.randint(start_min, end_min)
    return datetime.combine(d, time(minutes // 60, minutes % 60))


def later_same_or_next_day(dt, min_minutes, max_minutes):
    """A time a little after dt, rolling to the next weekday if past working hours."""
    result = dt + timedelta(minutes=rng.randint(min_minutes, max_minutes))
    if result.time() > DAY_END or result.date() != dt.date():
        next_day = add_business_days(dt.date(), 1)
        result = datetime.combine(next_day, DAY_START) + timedelta(minutes=rng.randint(15, 120))
    return result


def fmt(value):
    if isinstance(value, datetime):
        return value.strftime(TIME_FORMAT)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, bool):
        return "True" if value else "False"
    return "" if value is None else str(value)


def random_weekday_between(a, b):
    while True:
        d = a + timedelta(days=rng.randint(0, (b - a).days))
        if is_weekday(d):
            return d


# ---------------------------------------------------------------------------
# Stage 1: Employees
# ---------------------------------------------------------------------------

def make_employees():
    employees = []
    for i in range(1, N_EMPLOYEES + 1):
        dept = rng.choices(DEPARTMENTS, DEPARTMENT_WEIGHTS)[0]
        weights = TYPE_WEIGHTS_SEASONAL_DEPT if dept in SEASONAL_DEPARTMENTS else TYPE_WEIGHTS_OTHER_DEPT
        emp_type = rng.choices(["permanent", "temporary", "seasonal"], weights)[0]

        if emp_type == "seasonal":  # spring surge
            start = random_weekday_between(*SEASONAL_START_DATE_RANGE)
        else:
            start = random_weekday_between(*START_DATE_RANGE)

        if rng.random() < LATE_REQUEST_RATE:
            notice = -rng.randint(0, 3)  # requests arrive on or after the start date
        else:
            notice = rng.randint(*NOTICE_RANGE[emp_type])
        first_submission = add_business_days(start, -notice)
        first_submission = max(next_weekday(first_submission), EARLIEST_SUBMISSION)

        employees.append({
            "employee_id": f"EMP-{i:04d}",
            "department": dept,
            "employee_type": emp_type,
            "start_date": start,
            "first_submission": first_submission,
        })
    return employees


# ---------------------------------------------------------------------------
# Stage 2: Tasks for each employee
# ---------------------------------------------------------------------------

def tasks_for(employee):
    field = employee["department"] in FIELD_DEPARTMENTS
    tasks = ["payroll_setup", "system_access"]
    if rng.random() < 0.85:
        tasks.append("orientation_scheduling")
    if rng.random() < (0.45 if field else 0.80):
        tasks.append("equipment_setup")
    if rng.random() < (0.75 if field else 0.45):
        tasks.append("workplace_access")
    return tasks


# ---------------------------------------------------------------------------
# Stage 3: What the requester submitted
# ---------------------------------------------------------------------------

def submitted_details(employee, task_type):
    submitted_at = random_work_time(add_business_days(employee["first_submission"], rng.randint(0, 2)))
    base = CHANNEL_WEIGHTS_FIELD if employee["department"] in FIELD_DEPARTMENTS else CHANNEL_WEIGHTS_OFFICE
    weights = [w * m for w, m in zip(base, CHANNEL_TASK_MULTIPLIER[task_type])]
    channel = rng.choices(CHANNELS, weights)[0]
    start = employee["start_date"]
    is_equipment = task_type == "equipment_setup"

    submitted_start = start
    submitted_dept = employee["department"]
    item = rng.choice(["laptop", "phone"]) if is_equipment else "not_applicable"
    missing = conflict = False

    if rng.random() < MISSING_RATE[channel]:
        missing = True
        options = ["start_date", "department"] + (["equipment_item"] if is_equipment else [])
        blank = rng.choice(options)
        if blank == "start_date":
            submitted_start = None
        elif blank == "department":
            submitted_dept = None
        else:
            item = None

    if not is_equipment and rng.random() < CONFLICT_ITEM_RATE:  # rule a
        conflict = True
        item = rng.choice(["laptop", "phone"])
    if submitted_start is not None and rng.random() < CONFLICT_START_DATE_RATE:  # rule c
        conflict = True
        submitted_start = add_business_days(start, rng.choice([-5, 5, 10]))

    issue_type = "both" if missing and conflict else "missing" if missing else "conflict" if conflict else "none"
    comment = make_comment(employee, submitted_start is not None and submitted_start != start)
    return {
        "submitted_at": submitted_at,
        "intake_channel": channel,
        "submitted_start_date": submitted_start,
        "submitted_hiring_department": submitted_dept,
        "equipment_item": item,
        "info_issue_type": issue_type,
        "requester_comment": comment,
    }


def make_comment(employee, date_differs):
    if date_differs and rng.random() < 0.6:
        return rng.choice(["Start date moved up", "Start date may change"])
    if rng.random() < 0.25:
        options = ["Please set up before first day", "Urgent - starting soon"]
        if employee["employee_type"] == "seasonal":
            options.append("Same setup as last season")
        return rng.choice(options)
    return ""


# ---------------------------------------------------------------------------
# Stages 4-6: Information check, assignment, team work, outcome
# ---------------------------------------------------------------------------

def build_requests(employees):
    requests = []
    for emp in employees:
        for task_type in tasks_for(emp):
            req = {"employee": emp, "task_type": task_type,
                   "responsible_team": ROUTING_RULE[task_type]}
            req.update(submitted_details(emp, task_type))
            requests.append(req)

    requests.sort(key=lambda r: r["submitted_at"])
    for n, req in enumerate(requests, start=1):
        req["request_id"] = f"REQ-{n:05d}"

        # Stage 4: information check
        if req["info_issue_type"] == "none":
            req["info_requested_at"] = None
            req["info_complete_at"] = req["submitted_at"]
        else:
            req["info_requested_at"] = later_same_or_next_day(req["submitted_at"], 30, 180)
            reply_day = add_business_days(req["submitted_at"].date(), rng.randint(1, 3))
            req["info_complete_at"] = max(random_work_time(reply_day),
                                          req["info_requested_at"] + timedelta(hours=1))

        # Assignment shortly after information is complete
        req["assigned_at"] = later_same_or_next_day(req["info_complete_at"], 30, 240)

    # Stage 5: simulate team work in time order so workload reflects only the past
    completed_by_team = {team: [] for team in TEAM_CAPACITY}
    for req in sorted(requests, key=lambda r: r["assigned_at"]):
        team = req["responsible_team"]
        open_now = sum(1 for done in completed_by_team[team] if done > req["assigned_at"])
        capacity = TEAM_CAPACITY[team]
        workload_delay = max(0, round((open_now - capacity) / (capacity * 0.5)))

        base = rng.randint(*BASE_PROCESSING_DAYS[req["task_type"]])
        if rng.random() < HIDDEN_DELAY_RATE:
            hidden = rng.randint(*HIDDEN_DELAY_DAYS)
            reason = rng.choice(DELAY_REASONS)
        else:
            hidden, reason = 0, "none"

        finish_day = add_business_days(req["assigned_at"].date(), base + workload_delay + hidden)
        req["team_completed_at"] = random_work_time(finish_day)
        req["completion_confirmed_at"] = random_work_time(
            add_business_days(finish_day, rng.randint(0, 2)))
        if req["completion_confirmed_at"] <= req["team_completed_at"]:
            req["completion_confirmed_at"] = later_same_or_next_day(req["team_completed_at"], 15, 90)

        req["sim_base_processing_days"] = base
        req["sim_workload_delay_days"] = workload_delay
        req["sim_hidden_delay_days"] = hidden
        req["sim_delay_reason"] = reason
        completed_by_team[team].append(req["team_completed_at"])

        # Stage 6: outcome against the 08:00 start-date deadline
        deadline = datetime.combine(req["employee"]["start_date"], DEADLINE_TIME)
        req["deadline"] = deadline
        req["ready_by_start"] = req["team_completed_at"] <= deadline
    return requests


# ---------------------------------------------------------------------------
# Status events (derived from the request timestamps)
# ---------------------------------------------------------------------------

def build_status_events(requests):
    events = []
    for req in requests:
        events.append((req["submitted_at"], req["request_id"], "submitted", "open", "requester"))
        if req["info_requested_at"]:
            events.append((req["info_requested_at"], req["request_id"], "info_requested",
                           "waiting_for_information", "coordinator"))
            events.append((req["info_complete_at"], req["request_id"], "info_received", "open", "requester"))
        events.append((req["assigned_at"], req["request_id"], "assigned_to_team", "in_progress", "coordinator"))
        events.append((req["team_completed_at"], req["request_id"], "team_completed", "in_progress", "team"))
        events.append((req["completion_confirmed_at"], req["request_id"], "completion_confirmed",
                       "complete", "coordinator"))
    events.sort(key=lambda e: (e[0], e[1]))
    return [
        {"event_id": f"EVT-{n:06d}", "request_id": rid, "event_type": etype,
         "status_after": status, "event_at": at, "actor_role": actor}
        for n, (at, rid, etype, status, actor) in enumerate(events, start=1)
    ]


# ---------------------------------------------------------------------------
# Stage 7: Assessments (inputs use only what is known at assessment time)
# ---------------------------------------------------------------------------

def team_workload_at(requests_by_team, team, moment):
    return sum(1 for r in requests_by_team[team]
               if r["assigned_at"] <= moment < r["team_completed_at"])


def build_assessments(requests):
    by_team = {team: [] for team in TEAM_CAPACITY}
    for req in requests:
        by_team[req["responsible_team"]].append(req)

    raw = []
    for req in requests:
        start = req["employee"]["start_date"]
        checkpoints = [("checkpoint_1", req["info_complete_at"])]
        cp2 = datetime.combine(add_business_days(start, -5), DEADLINE_TIME)
        if req["info_complete_at"] < cp2 < req["team_completed_at"]:
            checkpoints.append(("checkpoint_2", cp2))

        for name, moment in checkpoints:
            if moment < req["assigned_at"]:
                status, status_since = "open", req["info_complete_at"]
            else:
                status, status_since = "in_progress", req["assigned_at"]
            raw.append({
                "request_id": req["request_id"],
                "employee_id": req["employee"]["employee_id"],
                "checkpoint": name,
                "assessed_at": moment,
                "business_days_until_start": business_days_until_start(moment.date(), start),
                "current_status": status,
                "business_days_in_current_status": weekdays_between(status_since.date(), moment.date()),
                "team_open_workload": team_workload_at(by_team, req["responsible_team"], moment),
                "past_deadline_at_assessment": moment >= req["deadline"],
                "at_risk": not req["ready_by_start"],
            })
    raw.sort(key=lambda a: (a["assessed_at"], a["request_id"]))
    for n, row in enumerate(raw, start=1):
        row["assessment_id"] = f"ASM-{n:05d}"
    return raw


# ---------------------------------------------------------------------------
# Stage 8: Rows for output files, plus the deliberate-error version
# ---------------------------------------------------------------------------

REQUEST_FIELDS = [
    "request_id", "employee_id", "task_type", "responsible_team", "submitted_hiring_department",
    "hiring_department", "employee_type", "intake_channel", "submitted_at", "submitted_start_date",
    "confirmed_start_date", "equipment_item", "requester_comment", "info_issue_at_intake",
    "info_issue_type", "info_complete_at", "assigned_at", "team_completed_at",
    "completion_confirmed_at", "ready_by_start",
]
EVENT_FIELDS = ["event_id", "request_id", "event_type", "status_after", "event_at", "actor_role"]
ASSESSMENT_FIELDS = [
    "assessment_id", "request_id", "employee_id", "checkpoint", "assessed_at",
    "business_days_until_start", "current_status", "business_days_in_current_status",
    "team_open_workload", "past_deadline_at_assessment", "at_risk",
]
TRUTH_FIELDS = ["request_id", "sim_base_processing_days", "sim_workload_delay_days",
                "sim_hidden_delay_days", "sim_delay_reason"]
ERROR_FIELDS = ["request_id", "error_type", "field", "source_row_number"]


def request_row(req):
    emp = req["employee"]
    return {
        "request_id": req["request_id"],
        "employee_id": emp["employee_id"],
        "task_type": req["task_type"],
        "responsible_team": req["responsible_team"],
        "submitted_hiring_department": req["submitted_hiring_department"],
        "hiring_department": emp["department"],
        "employee_type": emp["employee_type"],
        "intake_channel": req["intake_channel"],
        "submitted_at": req["submitted_at"],
        "submitted_start_date": req["submitted_start_date"],
        "confirmed_start_date": emp["start_date"],
        "equipment_item": req["equipment_item"],
        "requester_comment": req["requester_comment"],
        "info_issue_at_intake": req["info_issue_type"] != "none",
        "info_issue_type": req["info_issue_type"],
        "info_complete_at": req["info_complete_at"],
        "assigned_at": req["assigned_at"],
        "team_completed_at": req["team_completed_at"],
        "completion_confirmed_at": req["completion_confirmed_at"],
        "ready_by_start": req["ready_by_start"],
    }


MISSPELLINGS = {
    "task_type": {"payroll_setup": "payrol_setup", "system_access": "sytem_access",
                  "workplace_access": "workplace_acess", "equipment_setup": "equipment_set_up",
                  "orientation_scheduling": "orientaton_scheduling"},
    "responsible_team": {"Facilities": "Facilites", "Payroll": "Payrol", "IT": "I.T.", "Manager": "Manger"},
}


def inject_errors(clean_rows):
    """Copy the clean rows, plant a counted set of problems, and return the answer key."""
    rows = [{k: fmt(v) for k, v in r.items()} for r in clean_rows]
    targets = rng.sample(range(len(rows)), sum(n for k, n in ERROR_COUNTS.items() if k != "duplicate_row"))
    planted = []  # (row dict, error_type, field)

    def take(n):
        return [rows[targets.pop()] for _ in range(n)]

    for row in take(ERROR_COUNTS["impossible_date"]):
        field = rng.choice(["submitted_at", "submitted_start_date"])
        row[field] = rng.choice(["2026-02-30", "2026-04-31", "2026-06-31"]) + (
            "T10:15" if field == "submitted_at" else "")
        planted.append((row, "impossible_date", field))
    for row in take(ERROR_COUNTS["misspelled_category"]):
        field = rng.choice(["task_type", "responsible_team"])
        row[field] = MISSPELLINGS[field][row[field]]
        planted.append((row, "misspelled_category", field))
    for row in take(ERROR_COUNTS["invalid_channel"]):
        row["intake_channel"] = "fax"
        planted.append((row, "invalid_channel", "intake_channel"))
    for row in take(ERROR_COUNTS["extra_blank"]):
        field = rng.choice(["employee_type", "intake_channel", "task_type"])
        row[field] = ""
        planted.append((row, "extra_blank", field))

    planted_ids = {id(r) for r, _, _ in planted}
    candidates = [r for r in rows if id(r) not in planted_ids]
    for original in rng.sample(candidates, ERROR_COUNTS["duplicate_row"]):
        copy = dict(original)
        rows.insert(rows.index(original) + 1, copy)
        planted.append((copy, "duplicate_row", ""))

    row_number = {id(r): i + 2 for i, r in enumerate(rows)}  # header is row 1
    key = [{"request_id": r["request_id"], "error_type": etype, "field": field,
            "source_row_number": row_number[id(r)]}
           for r, etype, field in planted]
    key.sort(key=lambda k: k["source_row_number"])
    return rows, key


def write_csv(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: fmt(row[k]) for k in fields})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    employees = make_employees()
    requests = build_requests(employees)
    events = build_status_events(requests)
    assessments = build_assessments(requests)
    request_rows = [request_row(r) for r in requests]
    error_rows, error_key = inject_errors(request_rows)

    OUTPUT_DIR.mkdir(exist_ok=True)
    write_csv(OUTPUT_DIR / "requests.csv", REQUEST_FIELDS, request_rows)
    write_csv(OUTPUT_DIR / "status_events.csv", EVENT_FIELDS, events)
    write_csv(OUTPUT_DIR / "assessments.csv", ASSESSMENT_FIELDS, assessments)
    write_csv(OUTPUT_DIR / "simulation_truth.csv", TRUTH_FIELDS, requests)
    write_csv(OUTPUT_DIR / "requests_with_errors.csv", REQUEST_FIELDS, error_rows)
    write_csv(OUTPUT_DIR / "injected_errors.csv", ERROR_FIELDS, error_key)

    # Stage 9: summary for the data card and README
    at_risk = sum(a["at_risk"] for a in assessments)
    early = [a for a in assessments if not a["past_deadline_at_assessment"]]
    print(f"Seed: {SEED}")
    print(f"Employees: {len(employees)}")
    print(f"Requests (tasks): {len(requests)}")
    print(f"Status events: {len(events)}")
    print(f"Assessments: {len(assessments)} "
          f"({Counter(a['checkpoint'] for a in assessments)['checkpoint_2']} at checkpoint_2)")
    print(f"At-risk assessments: {at_risk} ({at_risk / len(assessments):.1%})")
    early_risk = sum(a["at_risk"] for a in early)
    print(f"Already-overdue assessments: {len(assessments) - len(early)}")
    print(f"Early-warning assessments: {len(early)}, at risk: {early_risk} ({early_risk / len(early):.1%})")
    for cp in ("checkpoint_1", "checkpoint_2"):
        group = [a for a in assessments if a["checkpoint"] == cp]
        risk = sum(a["at_risk"] for a in group)
        print(f"  {cp}: {risk}/{len(group)} at risk ({risk / len(group):.1%})")
    print("Tasks per employee:", dict(sorted(Counter(Counter(
        r["employee"]["employee_id"] for r in requests).values()).items())))
    print(f"Tasks not ready by start: {sum(not r['ready_by_start'] for r in requests)} "
          f"({sum(not r['ready_by_start'] for r in requests) / len(requests):.1%})")
    print("Not ready by task type:")
    for task in ROUTING_RULE:
        group = [r for r in requests if r["task_type"] == task]
        late = sum(not r["ready_by_start"] for r in group)
        print(f"  {task}: {late}/{len(group)} ({late / len(group):.1%})")
    print("Employee types:", dict(Counter(e["employee_type"] for e in employees)))
    print("Information issues:", dict(Counter(r["info_issue_type"] for r in requests)))
    print("Planted errors:", dict(Counter(k["error_type"] for k in error_key)))
    print(f"Files written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
