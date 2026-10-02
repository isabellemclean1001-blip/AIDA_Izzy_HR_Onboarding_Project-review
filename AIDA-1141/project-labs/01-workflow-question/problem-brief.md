# Problem Brief: AIDA 1141 Project Exercise 01 – Onboarding Request Routing and Follow-Up

## 1. Problem context and staff user

Onboarding tasks can be delayed when handoffs stall or incomplete work is noticed too close to the employee's start date, leaving the new employee without equipment, access, or pay setup on their first day.

The staff user is an HR onboarding coordinator at the fictional Town of Pinecrest. The coordinator reviews requests, confirms the responsible team, and decides which tasks need follow-up. The workflow begins after hiring is finished. 

## 2. The decision and workflow

A hiring manager or HR staff member submits an onboarding request. Each request represents one task, and one fictional employee can have several requests.

Simple routing rules identify the responsible team, which the coordinator confirms. 

| Request type | Example | Responsible team |
|:---|:---|:---:|
| **Equipment setup** | Provide a laptop or phone | IT |
| **System access** | Create an email account or provide software access | IT |
| **Payroll setup** | Set up the employee's pay record before the first pay run | Payroll |
| **Workplace access** | Provide keys, an access card, or a workspace | Facilities |
| **Orientation scheduling** | Arrange a first-day schedule or department orientation | Manager / supervisor |

The model's role is to identify tasks at risk of missing the start date. The coordinator reviews the risk suggestion and decides whether to follow up or expedite the task. 

| Next step | Decided by |
|:---|:---|
| Send to responsible team | Routing rule; coordinator confirms |
| Request missing information | Rule: required fields missing or conflicting |
| Follow up / expedite | Model: task at risk of missing the start date |
| Coordinator review | Low model confidence or unusual case |

The model handles the uncertain question of whether a task is likely to finish on time. Every suggested action requires coordinator confirmation. 

Tasks are assessed at intake (once required information is complete) and, if still incomplete, five business days before the start date. The second checkpoint only applies when it falls after intake, giving each request at most two assessments.

Model inputs include task type, responsible team, hiring department, intake channel, days until start, current status, time in that status, whether information was missing at intake, and current team workload. Only information available at assessment time will be used.

Requests are tracked as open, in progress, waiting for information, or complete, with timestamps for each status change. "In progress" means assigned to the responsible team. Completion requires confirmation from that team and the coordinator.

See [workflow-diagram.md](workflow-diagram.md). It shows intake, routing, risk assessment, staff review, and tracking to completion.

## 3. One measurable question

Can a model identify at least 90% of synthetic task assessments that would miss the employee's start date without intervention, while keeping false alerts manageable and performing better than simple follow-up rules?

The generator will simulate completion outcomes, including unexpected delays that the model cannot see. An assessment is labelled "at risk" if the simulated task would finish after the start date without additional intervention.

These labels describe simulated outcomes, rather than real staff decisions. Training, validation, and test data will be separated by fictional employee. The test set will not be used for training or selecting the alert threshold. 

## 4. Success measure

My proposed starting targets are:

- At least 90% recall: identify nine out of ten assessments labelled at risk.
- At least 60% precision: six out of ten risk alerts correspond to assessments labelled at risk.
- Better recall at a comparable alert volume than simple rules based on days until start or time in the current status.

I will also report a "never at risk" baseline, the overall share of assessments flagged, and results by task type. Missed payroll alerts will receive particular attention because late payroll setup could delay pay. 

These targets may be revised using training and validation results before final testing. If simple rules perform as well as the model, that will still be useful. Completion by the start date will be tracked, but this project will not prove that the model improves it or that synthetic results apply to a real HR department.

## 5. What is out of scope

This project will not include:

- Real employee data, documents, or City of Red Deer records.
- Names, ages, gender, or other personal attributes; employees will have fictional IDs only.
- Sensitive information such as SIN numbers, banking details, or tax forms.
- Connections to real HR, ERP, payroll, or document management systems. 
- Automatic actions or completion without human confirmation.
- Predictions about individual employees; the model assesses tasks, not people.
- Hiring decisions, candidate assessments, or other HR workflows.
- A production-ready application.

The project will use synthetic records, a workflow diagram, and a few screen views. If included, the demo will be a small local Streamlit app.