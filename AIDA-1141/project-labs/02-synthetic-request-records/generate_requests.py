"""Generate synthetic onboarding request data for the fictional Town of Pinecrest (version 2).

Simulates continuous onboarding from January 2025 with no coordinator intervention,
then writes what the HR system would export on a fixed extract date, including
realistic recording problems. Uses only the Python standard library. Run with:

    python3 generate_requests.py

Outputs:
    data/                 the system export used for analysis (messy, censored at the extract date)
    evaluation_only/      answer key and simulation values; never used to clean or fill analysis data

The same seed, settings, code, and Python version reproduce the same files.
"""

import csv
import math
import random
from collections import Counter
from datetime import date, datetime, time, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Stage 0: Settings (all values are invented simulation assumptions)
# ---------------------------------------------------------------------------

SEED = 2026
N_EMPLOYEES = 1150
SYSTEM_START = date(2025, 1, 6)                 # the intake system went live; no earlier submissions
START_DATE_RANGE = (date(2025, 3, 3), date(2026, 12, 18))
SEASONAL_START_RANGES = [(date(2025, 4, 1), date(2025, 6, 30)), (date(2026, 4, 1), date(2026, 6, 30))]
EXTRACT_AT = datetime(2026, 9, 29, 17, 0)       # the export was taken after work on Tuesday 29 September 2026
DATA_DIR = Path(__file__).parent / "data"
EVAL_DIR = Path(__file__).parent / "evaluation_only"

# Simulated office closure dates observed by the fictional Town of Pinecrest (based on common Alberta
# holidays, including Heritage Day and the National Day for Truth and Reconciliation). Not an official calendar.
HOLIDAYS = {
    date(2025, 1, 1), date(2025, 2, 17), date(2025, 4, 18), date(2025, 5, 19), date(2025, 7, 1),
    date(2025, 8, 4), date(2025, 9, 1), date(2025, 9, 30), date(2025, 10, 13), date(2025, 11, 11),
    date(2025, 12, 25), date(2025, 12, 26),
    date(2026, 1, 1), date(2026, 2, 16), date(2026, 4, 3), date(2026, 5, 18), date(2026, 7, 1),
    date(2026, 8, 3), date(2026, 9, 7), date(2026, 9, 30), date(2026, 10, 12), date(2026, 11, 11),
    date(2026, 12, 25), date(2026, 12, 28),     # Boxing Day 2026 falls on a Saturday; observed Monday
}

DEPARTMENTS = ["Parks", "Transit", "Recreation", "Finance", "Utilities", "Administration"]
DEPARTMENT_WEIGHTS = [0.22, 0.18, 0.18, 0.12, 0.15, 0.15]
FIELD_DEPARTMENTS = {"Parks", "Transit", "Utilities"}
SEASONAL_DEPARTMENTS = {"Parks", "Recreation"}

# Employee type probabilities: (permanent, temporary, seasonal)
TYPE_WEIGHTS_SEASONAL_DEPT = [0.35, 0.15, 0.50]
TYPE_WEIGHTS_OTHER_DEPT = [0.70, 0.25, 0.05]

# Business days of notice before the start date: median and spread of a log-normal draw, clamped to 1-60
NOTICE_MEDIAN = {"permanent": 18, "temporary": 10, "seasonal": 8}
NOTICE_SPREAD = 0.55
LATE_REQUEST_RATE = 0.04  # share of employees whose requests arrive on or after the start date

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
TAIL_RATE = 0.25          # chance of extra unexplained processing days (mean 2)
STUCK_RATE = 0.02         # chance a task gets stuck for 15-30 extra business days
STUCK_DAYS = (15, 30)

# Open tasks a team can handle before it slows down, and periods with fewer staff
TEAM_CAPACITY = {"IT": 32, "Payroll": 16, "Facilities": 13, "Manager": 17}
SUMMER_CAPACITY_FACTOR = 0.7                     # July and August vacations, every team
SHORT_STAFFED = [("Payroll", date(2025, 11, 3), date(2025, 12, 19), 0.6),
                 ("IT", date(2026, 2, 2), date(2026, 3, 13), 0.7)]

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
# Share of submissions made outside working hours (evenings, early mornings, weekends, holidays)
AFTER_HOURS_RATE = {"web_form": 0.22, "email": 0.12, "phone": 0.0}
MISSING_RATE = {"web_form": 0.04, "email": 0.10, "phone": 0.14}
CONFLICT_ITEM_RATE = 0.03        # rule a: item listed on a non-equipment task
CONFLICT_START_DATE_RATE = 0.04  # rule c: start date differs from the employee's other requests

HIDDEN_DELAY_RATE = 0.18
HIDDEN_DELAY_DAYS = (1, 6)
DELAY_REASONS = ["staff_absence", "backlog", "vendor_delay"]

# Recording problems in the exported requests.csv (shares of exported rows unless counts)
CATEGORY_VARIANT_RATE = 0.06
WHITESPACE_RATE = 0.02
MISSING_FIELD_RATE = {"employee_type": 0.01, "intake_channel": 0.01, "hiring_department": 0.01}
DUPLICATE_ROW_RATE = 0.005
IMPOSSIBLE_DATE_COUNT = 6
YEAR_TYPO_COUNT = 4

DAY_START = time(8, 0)
DAY_END = time(16, 30)
DEADLINE_TIME = time(8, 0)
TIME_FORMAT = "%Y-%m-%dT%H:%M"

rng = random.Random(SEED)


# ---------------------------------------------------------------------------
# Business-day helpers (Monday-Friday, excluding the closure dates in HOLIDAYS)
# ---------------------------------------------------------------------------

def is_business_day(d):
    return d.weekday() < 5 and d not in HOLIDAYS


def next_business_day(d):
    while not is_business_day(d):
        d += timedelta(days=1)
    return d


def add_business_days(d, n):
    """Move n business days forward (n > 0) or backward (n < 0) from date d."""
    step = 1 if n >= 0 else -1
    remaining = abs(n)
    while remaining:
        d += timedelta(days=step)
        if is_business_day(d):
            remaining -= 1
    return d


def business_days_between(a, b):
    """Count business days in [a, b); 0 if b <= a."""
    count, d = 0, a
    while d < b:
        if is_business_day(d):
            count += 1
        d += timedelta(days=1)
    return count


def business_days_until_start(assessed, start):
    """Business days from the assessment day up to the day before the start date.

    Negative when assessed after the start date; 0 on the start date.
    """
    if assessed < start:
        return business_days_between(assessed, start)
    return -business_days_between(start, assessed)


def random_work_time(d):
    """A random time during working hours on business day d."""
    start_min = DAY_START.hour * 60 + DAY_START.minute
    end_min = DAY_END.hour * 60 + DAY_END.minute
    minutes = rng.randint(start_min, end_min)
    return datetime.combine(d, time(minutes // 60, minutes % 60))


def next_working_moment(dt):
    """dt if it falls within working hours on a business day; otherwise the start of the next working day."""
    if is_business_day(dt.date()):
        if dt.time() < DAY_START:
            return datetime.combine(dt.date(), DAY_START)
        if dt.time() <= DAY_END:
            return dt
    return datetime.combine(next_business_day(dt.date() + timedelta(days=1)), DAY_START)


def later_same_or_next_day(dt, min_minutes, max_minutes):
    """A working time a little after dt, rolling to the next business day if past working hours."""
    base = next_working_moment(dt)
    result = base + timedelta(minutes=rng.randint(min_minutes, max_minutes))
    if result.time() > DAY_END or result.date() != base.date():
        next_day = add_business_days(base.date(), 1)
        result = datetime.combine(next_day, DAY_START) + timedelta(minutes=rng.randint(15, 120))
    return result


def after_hours_time(anchor):
    """A submission time outside working hours near the anchor business day."""
    kind = rng.choices(["evening", "early", "closed_day"], [0.55, 0.15, 0.30])[0]
    if kind == "evening":
        minutes = rng.randint(16 * 60 + 31, 22 * 60)
        return datetime.combine(anchor, time(minutes // 60, minutes % 60))
    if kind == "early":
        minutes = rng.randint(6 * 60 + 30, 7 * 60 + 59)
        return datetime.combine(anchor, time(minutes // 60, minutes % 60))
    d = anchor - timedelta(days=1)  # the closest weekend day or holiday before the anchor
    while is_business_day(d):
        d -= timedelta(days=1)
    minutes = rng.randint(9 * 60, 20 * 60)
    return datetime.combine(d, time(minutes // 60, minutes % 60))


def team_capacity(team, d):
    capacity = TEAM_CAPACITY[team]
    if d.month in (7, 8):
        capacity *= SUMMER_CAPACITY_FACTOR
    for short_team, first, last, factor in SHORT_STAFFED:
        if team == short_team and first <= d <= last:
            capacity *= factor
    return capacity


def fmt(value):
    if isinstance(value, datetime):
        return value.strftime(TIME_FORMAT)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, bool):
        return "True" if value else "False"
    return "" if value is None else str(value)


def random_business_day_between(a, b):
    while True:
        d = a + timedelta(days=rng.randint(0, (b - a).days))
        if is_business_day(d):
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

        if emp_type == "seasonal":  # spring surge each year
            start = random_business_day_between(*rng.choice(SEASONAL_START_RANGES))
        else:
            start = random_business_day_between(*START_DATE_RANGE)

        if rng.random() < LATE_REQUEST_RATE:
            notice = -rng.randint(0, 3)  # requests arrive on or after the start date
        else:
            draw = rng.lognormvariate(math.log(NOTICE_MEDIAN[emp_type]), NOTICE_SPREAD)
            notice = min(60, max(1, round(draw)))
        first_submission = add_business_days(start, -notice)
        first_submission = max(next_business_day(first_submission), SYSTEM_START)

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
    base = CHANNEL_WEIGHTS_FIELD if employee["department"] in FIELD_DEPARTMENTS else CHANNEL_WEIGHTS_OFFICE
    weights = [w * m for w, m in zip(base, CHANNEL_TASK_MULTIPLIER[task_type])]
    channel = rng.choices(CHANNELS, weights)[0]
    anchor = add_business_days(employee["first_submission"], rng.randint(0, 2))
    if rng.random() < AFTER_HOURS_RATE[channel]:
        submitted_at = max(after_hours_time(anchor), datetime.combine(SYSTEM_START, time(0, 0)))
    else:
        submitted_at = random_work_time(anchor)
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
# Stages 4-6: Information check, assignment, team work, outcome (the full simulated history)
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

        # Stage 4: information check by a coordinator during working hours: immediate for a complete request
        # submitted during working hours, otherwise at the start of the next working day
        if req["info_issue_type"] == "none":
            req["info_requested_at"] = None
            req["info_complete_at"] = next_working_moment(req["submitted_at"])
        else:
            req["info_requested_at"] = later_same_or_next_day(req["submitted_at"], 30, 180)
            reply_day = add_business_days(req["info_requested_at"].date(), rng.randint(1, 4))
            req["info_complete_at"] = next_working_moment(
                max(random_work_time(reply_day), req["info_requested_at"] + timedelta(hours=1)))

        # Assignment shortly after information is complete
        req["assigned_at"] = later_same_or_next_day(req["info_complete_at"], 30, 240)

    # Stage 5: simulate team work in time order so workload reflects only the past
    processed_by_team = {team: [] for team in TEAM_CAPACITY}  # (assigned_at, team_completed_at) of earlier tasks
    for req in sorted(requests, key=lambda r: (r["assigned_at"], r["request_id"])):
        team = req["responsible_team"]
        # Other tasks assigned strictly before this assignment and completing strictly after it
        # (tasks assigned or completed at the same timestamp are excluded)
        open_now = sum(1 for assigned, done in processed_by_team[team]
                       if assigned < req["assigned_at"] < done)
        capacity = team_capacity(team, req["assigned_at"].date())
        workload_delay = max(0, round((open_now - capacity) / (capacity * 0.5)))

        base = rng.randint(*BASE_PROCESSING_DAYS[req["task_type"]])
        tail = round(rng.expovariate(0.5)) if rng.random() < TAIL_RATE else 0
        stuck = rng.randint(*STUCK_DAYS) if rng.random() < STUCK_RATE else 0
        if rng.random() < HIDDEN_DELAY_RATE:
            hidden = rng.randint(*HIDDEN_DELAY_DAYS)
            reason = rng.choice(DELAY_REASONS)
        else:
            hidden, reason = 0, "none"

        finish_day = add_business_days(req["assigned_at"].date(), base + tail + stuck + workload_delay + hidden)
        req["team_completed_at"] = random_work_time(finish_day)
        req["completion_confirmed_at"] = random_work_time(
            add_business_days(finish_day, rng.randint(0, 2)))
        if req["completion_confirmed_at"] <= req["team_completed_at"]:
            req["completion_confirmed_at"] = later_same_or_next_day(req["team_completed_at"], 15, 90)

        req["sim_base_processing_days"] = base
        req["sim_tail_extra_days"] = tail
        req["sim_stuck_extra_days"] = stuck
        req["sim_workload_delay_days"] = workload_delay
        req["sim_hidden_delay_days"] = hidden
        req["sim_delay_reason"] = reason
        processed_by_team[team].append((req["assigned_at"], req["team_completed_at"]))

        # Stage 6: outcome against the 08:00 start-date deadline (the full simulation knows it)
        deadline = datetime.combine(req["employee"]["start_date"], DEADLINE_TIME)
        req["deadline"] = deadline
        req["true_ready_by_start"] = req["team_completed_at"] <= deadline
    return requests


def known_at_extract(moment):
    return moment if moment is not None and moment <= EXTRACT_AT else None


def outcome_at_extract(req):
    """Readiness as the system could know it at the extract: True, False, or None (unknown)."""
    if req["team_completed_at"] <= EXTRACT_AT:
        return req["team_completed_at"] <= req["deadline"]
    if req["deadline"] <= EXTRACT_AT:
        return False  # unfinished and the deadline has passed: known to have missed it
    return None        # unfinished and the deadline is still ahead: outcome unknown


def request_events(req):
    """Every status event in the simulated history of one request: (time, event, status after, actor)."""
    events = [(req["submitted_at"], "submitted", "open", "requester")]
    if req["info_requested_at"]:
        events.append((req["info_requested_at"], "info_requested", "waiting_for_information", "coordinator"))
        events.append((req["info_complete_at"], "info_received", "open", "requester"))
    events += [(req["assigned_at"], "assigned_to_team", "in_progress", "coordinator"),
               (req["team_completed_at"], "team_completed", "in_progress", "team"),
               (req["completion_confirmed_at"], "completion_confirmed", "complete", "coordinator")]
    return events


def status_at_extract(req):
    """Status after the latest event recorded by the extract (the same rule as status_events.csv)."""
    return max((e for e in request_events(req) if e[0] <= EXTRACT_AT), key=lambda e: e[0])[2]


# ---------------------------------------------------------------------------
# Status events (derived from the request timestamps, up to the extract)
# ---------------------------------------------------------------------------

def build_status_events(requests):
    events = [(at, req["request_id"], etype, status, actor)
              for req in requests for at, etype, status, actor in request_events(req) if at <= EXTRACT_AT]
    events.sort(key=lambda e: (e[0], e[1]))
    return [
        {"event_id": f"EVT-{n:06d}", "request_id": rid, "event_type": etype,
         "status_after": status, "event_at": at, "actor_role": actor}
        for n, (at, rid, etype, status, actor) in enumerate(events, start=1)
    ]


# ---------------------------------------------------------------------------
# Stage 7: Assessments (inputs use only what is known at assessment time, up to the extract)
# ---------------------------------------------------------------------------

def team_workload_at(requests_by_team, team, moment, exclude_id):
    """Other tasks assigned strictly before the moment and completing strictly after it.

    Tasks assigned or completed at the same timestamp are excluded.
    """
    return sum(1 for r in requests_by_team[team]
               if r["request_id"] != exclude_id and r["assigned_at"] < moment < r["team_completed_at"])


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
            if moment > EXTRACT_AT:
                continue
            if moment < req["assigned_at"]:
                status, status_since = "open", req["info_complete_at"]
            else:
                status, status_since = "in_progress", req["assigned_at"]
            outcome = outcome_at_extract(req)
            raw.append({
                "request_id": req["request_id"],
                "employee_id": req["employee"]["employee_id"],
                "checkpoint": name,
                "assessed_at": moment,
                "business_days_until_start": business_days_until_start(moment.date(), start),
                "current_status": status,
                "business_days_in_current_status": business_days_between(status_since.date(), moment.date()),
                "team_open_workload": team_workload_at(by_team, req["responsible_team"], moment, req["request_id"]),
                "past_deadline_at_assessment": moment >= req["deadline"],
                "at_risk": None if outcome is None else not outcome,
            })
    raw.sort(key=lambda a: (a["assessed_at"], a["request_id"]))
    for n, row in enumerate(raw, start=1):
        row["assessment_id"] = f"ASM-{n:05d}"
    return raw


# ---------------------------------------------------------------------------
# Stage 8: The system export, with recording problems, and the evaluation-only answer key
# ---------------------------------------------------------------------------

REQUEST_FIELDS = [
    "request_id", "employee_id", "task_type", "responsible_team", "submitted_hiring_department",
    "hiring_department", "employee_type", "intake_channel", "submitted_at", "submitted_start_date",
    "confirmed_start_date", "equipment_item", "requester_comment", "info_issue_at_intake",
    "info_issue_type", "info_complete_at", "assigned_at", "team_completed_at",
    "completion_confirmed_at", "status_at_extract", "ready_by_start",
]
EVENT_FIELDS = ["event_id", "request_id", "event_type", "status_after", "event_at", "actor_role"]
ASSESSMENT_FIELDS = [
    "assessment_id", "request_id", "employee_id", "checkpoint", "assessed_at",
    "business_days_until_start", "current_status", "business_days_in_current_status",
    "team_open_workload", "past_deadline_at_assessment", "at_risk",
]
TRUTH_FIELDS = ["request_id", "sim_base_processing_days", "sim_tail_extra_days", "sim_stuck_extra_days",
                "sim_workload_delay_days", "sim_hidden_delay_days", "sim_delay_reason",
                "true_team_completed_at", "true_ready_by_start"]
ISSUE_FIELDS = ["issue_id", "export_row_number", "request_id", "issue_type", "field",
                "recorded_value", "true_value"]


def request_row(req):
    emp = req["employee"]
    info_known = req["info_complete_at"] <= EXTRACT_AT
    return {
        "request_id": req["request_id"],
        "employee_id": emp["employee_id"],
        "task_type": req["task_type"],
        "responsible_team": req["responsible_team"],
        "submitted_hiring_department": req["submitted_hiring_department"],
        # Confirmed values exist only once the information check is complete
        "hiring_department": emp["department"] if info_known else None,
        "employee_type": emp["employee_type"],
        "intake_channel": req["intake_channel"],
        "submitted_at": req["submitted_at"],
        "submitted_start_date": req["submitted_start_date"],
        "confirmed_start_date": emp["start_date"] if info_known else None,
        "equipment_item": req["equipment_item"],
        "requester_comment": req["requester_comment"],
        "info_issue_at_intake": req["info_issue_type"] != "none",
        "info_issue_type": req["info_issue_type"],
        "info_complete_at": known_at_extract(req["info_complete_at"]),
        "assigned_at": known_at_extract(req["assigned_at"]),
        "team_completed_at": known_at_extract(req["team_completed_at"]),
        "completion_confirmed_at": known_at_extract(req["completion_confirmed_at"]),
        "status_at_extract": status_at_extract(req),
        "ready_by_start": outcome_at_extract(req),
    }


CATEGORY_VARIANTS = {
    "task_type": {"payroll_setup": ["Payroll Setup", "payroll setup"],
                  "system_access": ["System Access", "system access"],
                  "workplace_access": ["Workplace Access", "workplace access"],
                  "equipment_setup": ["Equipment Setup", "equipment set-up"],
                  "orientation_scheduling": ["Orientation Scheduling", "orientation"]},
    "responsible_team": {"IT": ["I.T.", "it"], "Payroll": ["payroll"], "Facilities": ["Facilites", "facilities"],
                         "Manager": ["manager", "Mgr"]},
    "hiring_department": {"Parks": ["parks", "Parks Dept", "Prks"], "Transit": ["transit", "Transit Services"],
                          "Recreation": ["Rec", "recreation", "Recreaton"], "Finance": ["finance", "Finanace"],
                          "Utilities": ["Utilties", "utilities"], "Administration": ["Admin", "administration"]},
    "employee_type": {"permanent": ["Permanent", "perm"], "temporary": ["Temporary", "temp"],
                      "seasonal": ["Seasonal", "SEASONAL"]},
    "intake_channel": {"web_form": ["Web Form", "web form", "WEB_FORM", "webform"],
                       "email": ["Email", "e-mail", "E-mail"], "phone": ["Phone", "phone call", "PHONE"]},
}
CATEGORY_VARIANTS["submitted_hiring_department"] = CATEGORY_VARIANTS["hiring_department"]
IMPOSSIBLE_DATES = ["2025-02-30", "2025-04-31", "2025-06-31", "2026-02-29", "2026-04-31", "2026-09-31"]


def record_export(clean_rows):
    """Copy the clean export rows, add recording problems, and return the rows and the answer key."""
    rows = [{k: fmt(v) for k, v in r.items()} for r in clean_rows]
    issues = []  # (row dict, issue_type, field, recorded, true)
    used = set()  # (row index, field) already changed

    def pick(fields, need_value=True):
        """A random (row index, field) not yet changed whose value is not blank."""
        while True:
            i, field = rng.randrange(len(rows)), rng.choice(fields)
            if (i, field) not in used and (rows[i][field] != "" or not need_value):
                used.add((i, field))
                return i, field

    for _ in range(round(CATEGORY_VARIANT_RATE * len(rows))):
        i, field = pick(list(CATEGORY_VARIANTS))
        true = rows[i][field]
        rows[i][field] = rng.choice(CATEGORY_VARIANTS[field][true])
        issues.append((rows[i], "category_variant", field, rows[i][field], true))
    for _ in range(round(WHITESPACE_RATE * len(rows))):
        i, field = pick(list(CATEGORY_VARIANTS))
        true = rows[i][field]
        rows[i][field] = rng.choice([f" {true}", f"{true} ", f"{true}  "])
        issues.append((rows[i], "extra_whitespace", field, rows[i][field], true))
    for field, rate in MISSING_FIELD_RATE.items():
        for _ in range(round(rate * len(rows))):
            i, _ = pick([field])
            true = rows[i][field]
            rows[i][field] = ""
            issues.append((rows[i], "missing_value", field, "", true))
    for bad in IMPOSSIBLE_DATES[:IMPOSSIBLE_DATE_COUNT]:
        i, field = pick(["submitted_at", "submitted_start_date"])
        true = rows[i][field]
        rows[i][field] = bad + ("T" + true.split("T")[1] if field == "submitted_at" else "")
        issues.append((rows[i], "impossible_date", field, rows[i][field], true))
    for _ in range(YEAR_TYPO_COUNT):
        i, field = pick(["submitted_at"])
        true = rows[i][field]
        rows[i][field] = {"2025": "2052", "2026": "2062"}[true[:4]] + true[4:]
        issues.append((rows[i], "year_typo", field, rows[i][field], true))

    # Exact duplicates: an extra copy of a recorded row, placed elsewhere in the export. A copy inherits any
    # problems already in its original; the key logs those against the original row only. Copies can appear
    # before or after their original, so evaluation removes exact duplicates first and then compares field
    # problems by request_id and field, not by row number (row numbers are for auditing the raw export).
    for original in rng.sample(rows, round(DUPLICATE_ROW_RATE * len(rows))):
        copy = dict(original)
        rows.insert(rng.randrange(len(rows) + 1), copy)
        issues.append((copy, "exact_duplicate", "", "", ""))

    row_number = {id(r): i + 2 for i, r in enumerate(rows)}  # header is row 1
    key = sorted(({"export_row_number": row_number[id(r)], "request_id": r["request_id"], "issue_type": t,
                   "field": f, "recorded_value": rec, "true_value": true}
                  for r, t, f, rec, true in issues), key=lambda k: (k["export_row_number"], k["field"]))
    for n, k in enumerate(key, start=1):
        k["issue_id"] = f"ISS-{n:04d}"
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
    rng.seed(SEED)  # start from the same state even if main() runs more than once in one session
    employees = make_employees()
    simulated = build_requests(employees)
    # The export contains only requests submitted by the extract; later ones are not yet in the system
    requests = [r for r in simulated if r["submitted_at"] <= EXTRACT_AT]
    for r in requests:
        r["true_team_completed_at"] = r["team_completed_at"]
    events = build_status_events(requests)
    assessments = build_assessments(requests)
    clean_rows = [request_row(r) for r in requests]
    export_rows, issue_key = record_export(clean_rows)

    DATA_DIR.mkdir(exist_ok=True)
    EVAL_DIR.mkdir(exist_ok=True)
    write_csv(DATA_DIR / "requests.csv", REQUEST_FIELDS, export_rows)
    write_csv(DATA_DIR / "status_events.csv", EVENT_FIELDS, events)
    write_csv(DATA_DIR / "assessments.csv", ASSESSMENT_FIELDS, assessments)
    write_csv(EVAL_DIR / "data_issues.csv", ISSUE_FIELDS, issue_key)
    write_csv(EVAL_DIR / "simulation_truth.csv", TRUTH_FIELDS,
              [{**r, "true_ready_by_start": r["true_ready_by_start"]} for r in requests])

    # Stage 9: summary for the data card and README
    in_system = {r["employee"]["employee_id"] for r in requests}
    outcomes = Counter("unknown" if outcome_at_extract(r) is None else "ready" if outcome_at_extract(r) else "missed"
                       for r in requests)
    labelled = [a for a in assessments if a["at_risk"] is not None]
    early = [a for a in labelled if not a["past_deadline_at_assessment"]]
    print(f"Seed: {SEED}; extract: {EXTRACT_AT:%Y-%m-%d %H:%M}")
    print(f"Employees simulated: {len(employees)}; with requests in the export: {len(in_system)}")
    print(f"Requests in the export: {len(requests)} (+{len(export_rows) - len(requests)} duplicate rows); "
          f"submitted {min(r['submitted_at'] for r in requests):%Y-%m-%d} to "
          f"{max(r['submitted_at'] for r in requests):%Y-%m-%d}")
    print("Status at extract:", dict(Counter(status_at_extract(r) for r in requests)))
    print("Readiness at extract:", dict(outcomes))
    print(f"Submitted outside working hours: "
          f"{sum(next_working_moment(r['submitted_at']) != r['submitted_at'] for r in requests)}")
    print(f"Status events: {len(events)}; assessments: {len(assessments)} "
          f"({Counter(a['checkpoint'] for a in assessments)['checkpoint_2']} at checkpoint_2; "
          f"{len(assessments) - len(labelled)} with unknown outcome)")
    print(f"Early-warning labelled assessments: {len(early)}, at risk: {sum(a['at_risk'] for a in early)} "
          f"({sum(a['at_risk'] for a in early) / len(early):.1%})")
    print(f"Stuck tasks: {sum(r['sim_stuck_extra_days'] > 0 for r in requests)}; "
          f"tasks with workload delay: {sum(r['sim_workload_delay_days'] > 0 for r in requests)}")
    print("Recording issues:", dict(Counter(k["issue_type"] for k in issue_key)))
    print(f"Files written to {DATA_DIR} and {EVAL_DIR}")


if __name__ == "__main__":
    main()
