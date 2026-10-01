# Your HR Onboarding Project Guide

**Project repository:** [AIDA_Izzy_HR_Onboarding_Project](https://github.com/stem-ai-studio-classroom/AIDA_Izzy_HR_Onboarding_Project)  
**Courses connected by this project:** AIDA 1141, AIDA 2156 (Exploratory Data Analysis), and AIDA 2154 (Computer Vision)

## What you are building

You will investigate one small, fictional business workflow: **staff receive onboarding requests, review them, route them to the right next step, and track whether the request is complete**. Explain it with a workflow diagram and a few screen views. If included, the demo is a small local Streamlit app using only synthetic records; you are not expected to build a production HR application.

Complete your work individually. Use synthetic records and computer-generated images only. Do not use real employee information, actual identity documents, employer/client records, or real photographs. A person must review any suggested category, status, or route.

The same context links your work across the courses, but each course asks a different question and requires its own evidence. **There are three separate final projects, each worth 25% in its course, with separate course rubrics and separate D2L final submissions.** This connected project does not combine the three grades or replace any regular course lab or knowledge check.

## Before you start: follow these steps

1. **Accept the private GitHub invitation.** Sign in to GitHub and accept the invitation to `AIDA_Izzy_HR_Onboarding_Project`. This is the one repository for your cross-course project exercises and integrated project work.
2. **Clone the project repository once.** In a terminal, run:

   ```text
   git clone https://github.com/stem-ai-studio-classroom/AIDA_Izzy_HR_Onboarding_Project.git
   cd AIDA_Izzy_HR_Onboarding_Project
   git status
   ```

   Keep this local folder for all of your project exercises and integrated project work. Do not create multiple competing copies. Use the **one project-wide Python environment** in [TECH-STACK-AND-TOOLS.md](TECH-STACK-AND-TOOLS.md) for all 30 exercises and all three course strands; do not create a separate environment for each course or exercise.
3. **Keep regular course labs in their assigned course repositories.** For each official weekly lab, follow that lab’s D2L instructions and use the assigned private course repository. Do not submit this project repository instead of an official lab repository. Complete the official lab exactly as assigned and meet its normal D2L due date, even when its case or required files differ from this project.
4. **Read the D2L instructions before every submission.** D2L is the source for the official lab title, due date, required files, final-project instructions, and any project-checkpoint assignment. This guide does not change those instructions or dates.
5. **Start with the small scope.** Write the project question and draw the one onboarding workflow before building screens or models. Keep a feature only when it helps explain intake, routing, tracking, or human review.
6. **Use only synthetic data.** Record how each synthetic table or image was generated. Do not put credentials, personal data, or confidential files in GitHub.
7. **Work in the matching folder below.** Each exercise has a small, named deliverable. Keep its code, data or data-generation recipe, output, and explanation together in that exercise folder.
8. **Commit and push meaningful progress.** After completing an exercise, use the same project-root Python environment described in [TECH-STACK-AND-TOOLS.md](TECH-STACK-AND-TOOLS.md). Then use Git:

   ```text
   git status
   git add AIDA-1141/project-labs/01-workflow-question
   git commit -m "AIDA 1141 project lab 01: define workflow question"
   git push
   ```

   Change the path and commit message to match your exercise. Do not make an empty commit just to show activity. If Git reports a problem, stop and use your course Git instructions or ask for help rather than deleting or force-pushing work.
9. **Verify the push.** Open the repository on GitHub and check that the folder, files, and latest commit are visible. A saved file on your computer is not yet evidence in GitHub.
10. **Submit the direct folder link in D2L.** In the matching project-exercise/checkpoint dropbox, paste the link to the completed GitHub folder (the page URL should include the folder path), plus the latest commit ID and a one-sentence summary. Submit any additional export D2L requests. Use the due date posted for that project exercise. Do not put this link into an unrelated regular-lab dropbox. If you cannot find the matching project dropbox, ask your instructor which D2L item to use; do not guess.

## What every one of the 30 project exercises must contain

For **each** numbered exercise, create its own folder containing:

- `README.md`: the use-case question, intended staff decision, steps you completed, result, what the result means, one limitation, and one action a human reviewer should take;
- the runnable notebook or source code used for the work;
- the small synthetic input data, or the script and instructions that generate it;
- the requested table, plot, image, diagram, or other evidence named for that exercise;
- brief run instructions, including required packages or environment where relevant; and
- a meaningful Git commit pushed to this project repository.

Do not copy a finished answer from another student. You should be able to explain what you did and why. If a course lab or final-project instruction requires additional files, include those too.

## AIDA 1141 — 10 structured-data / AI project exercises

These exercises build evidence for the AIDA 1141 part of the project. They do not replace the regular AIDA 1141 labs or knowledge checks.

| No. / folder | Onboarding use case and your task | Exercise-specific deliverable |
|---|---|---|
| 01 `01-workflow-question` | Define what happens when a fictional onboarding request arrives and must be routed. Identify the staff user, the decision, and what is outside scope. | `problem-brief.md` with one measurable question, intended user/decision, success measure, exclusions, and a one-page workflow diagram. |
| 02 `02-synthetic-request-records` | Create a small synthetic table of requests with clearly defined fields. Do not invent personal attributes. | Synthetic CSV or generator; `data-dictionary.csv`; and `data-card.md` stating row meaning, label source, generation method, and limitations. |
| 03 `03-data-quality-checks` | Check whether the synthetic request records are usable before analysis. Include missing, invalid, and duplicate examples. | Re-runnable validation code plus a quality report/table showing checks, counts, handling decisions, and unresolved issues. |
| 04 `04-routing-label-definition` | Define a small set of staff-routing categories and decide how a synthetic example receives its label. Check that label rules do not expose the answer as an input feature. | Label guide, labelled sample, and a short leakage/label-quality note with at least two edge cases. |
| 05 `05-simple-routing-baseline` | Build a transparent first baseline for suggesting a request category or next step. Compare it to a simple majority or documented rules baseline as appropriate. | Runnable baseline, saved predictions, comparison table, and a short explanation of why this is a fair starting point. |
| 06 `06-model-training-and-split` | Prepare the data and train one course-appropriate model. Keep evaluation data separate from model fitting. | Reproducible training script/notebook, documented split and features, saved model or results, and a check for leakage. |
| 07 `07-evaluation-measures` | Evaluate routing suggestions using measures suited to the categories and the cost of a wrong route. | Confusion matrix and required course metrics, with a note explaining which errors matter most to the fictional staff team. |
| 08 `08-error-and-slice-review` | Inspect wrong or uncertain suggestions and compare performance across relevant non-sensitive operational slices, such as request category or intake channel. | Error-review table with representative synthetic cases, slice results where sample sizes allow, and a cautious interpretation. |
| 09 `09-review-queue-and-threshold` | Decide which cases should be routed automatically as suggestions and which must go to a person for review. | Threshold/decision comparison, example review queue, and explicit human-review rule for low-confidence, ambiguous, or high-impact cases. |
| 10 `10-aida1141-evidence-brief` | Bring the structured-data evidence together and state what it does and does not support for the proposed workflow. | Reproducible course report, model/solution card, final recommendation, limitations, monitoring or follow-up evidence needed, and links to Exercises 01–09. |

## AIDA 2156 — Exploratory Data Analysis: 10 project exercises

These exercises build a reproducible evidence trail about synthetic onboarding workload and process time. They do not replace the regular AIDA 2156 labs or knowledge checks.

| No. / folder | Onboarding use case and your task | Exercise-specific deliverable |
|---|---|---|
| 01 `01-intake-volume-profile` | Explore how many fictional requests arrive by request type and intake channel. Define the unit represented by one row. | Data profile, count/summary table, one labelled plot, and a note about whether the sample is sufficient for the question. |
| 02 `02-completeness-patterns` | Examine which synthetic fields are missing and whether missingness clusters by request type or channel. | Missingness table/visualization, documented handling choices, and a note distinguishing an empty value from a true zero or “not applicable.” |
| 03 `03-processing-time-distributions` | Describe how long requests take from receipt to completion, overall and by broad request category. | Summary statistics and distribution plot; explain skew, center/spread, and what the numbers do not prove. |
| 04 `04-category-and-channel-relationships` | Explore whether request categories appear in different proportions across fictional intake channels. | Contingency table and appropriate plot, plus a careful association interpretation that does not claim causation. |
| 05 `05-weekly-workload-patterns` | Explore synthetic request arrival and completion counts over time to see whether workload fluctuates. | Time-based table and plot, documented date assumptions, and a note on whether the time window supports a trend claim. |
| 06 `06-process-step-bottlenecks` | Compare the synthetic duration of steps such as initial review, assignment, and completion. | Step-level summary and plot that identifies the largest observed delay, plus alternative explanations to investigate. |
| 07 `07-outlier-and-sensitivity-review` | Inspect unusually short or long processing times and see whether a reasonable analysis choice changes the summary. | Outlier review log and a before/after sensitivity table or plot; document any retained or excluded records and why. |
| 08 `08-operational-segment-comparison` | Compare workload or completion time across non-sensitive operational groupings, such as request type or channel. | Group summary with group sizes, uncertainty/caveat notes, and a statement against interpreting small groups as reliable rankings. |
| 09 `09-staff-workload-visual` | Choose a clear visual that could help a fictional HR team lead monitor incoming, in-progress, and completed work. | One-page dashboard or a small set of labelled plots, with a caption for each measure and a note about refresh frequency/data limits. |
| 10 `10-aida2156-exploration-report` | Combine the exploration into a decision-focused report for the same workflow. | Reproducible notebook/report, key figures and tables, data-quality and sensitivity findings, a decision brief, limitations, and links to Exercises 01–09. |

## AIDA 2154 — Computer Vision: 10 project exercises

**Scope checkpoint:** Before doing the vision exercises beyond a tiny synthetic feasibility sample, confirm with your instructor that computer-generated onboarding-card images and the proposed task fit AIDA 2154 and the project workload. Never use scans or photographs of real employee documents. If this image question does not fit, pause and use the synthetic vision question you and your instructor agree on; keep the connection to the onboarding workflow only where it makes sense.

The proposed image task is limited to computer-generated, non-personal mock intake cards, icons, or status panels. It asks whether a course-appropriate vision method can help organize a visual element for staff review. It is not identity recognition, document verification, OCR of real forms, or an automated hiring/onboarding decision.

| No. / folder | Onboarding use case and your task | Exercise-specific deliverable |
|---|---|---|
| 01 `01-synthetic-image-specification` | Define the visual question and create a tiny set of computer-generated examples with documented classes. | Image data card, label guide, synthetic-image generator or source files, train/validation/test manifest, and a human-review note. |
| 02 `02-image-quality-and-preprocessing` | Inspect dimensions, colour channels, file integrity, and visual variation in the synthetic examples. | Reproducible quality/preprocessing script, before/after image examples, summary table, and written preprocessing rationale. |
| 03 `03-visual-feature-inspection` | Explore a course-taught visual feature or filtering step that might distinguish the synthetic icon/status examples. | Runnable feature/filter experiment, labelled visual outputs, parameter notes, and a short account of failure cases. |
| 04 `04-region-segmentation-or-matching` | Test a course-appropriate segmentation or matching method on a generated status icon or panel. | Method and parameter record, overlay/output examples, small success/failure table, and explanation of when a person must check it. |
| 05 `05-vision-baseline` | Establish a simple, transparent vision baseline for the agreed synthetic image task. | Runnable baseline, predictions, baseline metric(s), and a note describing the comparison the baseline enables. |
| 06 `06-vision-model-experiment` | Train or apply one course-appropriate vision method to the synthetic image set. | Reproducible experiment, documented model/settings, saved predictions, and the evidence required by the AIDA 2154 lab/checkpoint instructions. |
| 07 `07-variation-and-robustness` | Examine how benign synthetic changes such as scale, orientation, contrast, or background affect the method, using changes taught in the course. | Controlled variation table or visual grid, metric comparison where suitable, and an interpretation of what variation was not tested. |
| 08 `08-localization-or-output-review` | If localization is part of the approved course method, locate the relevant synthetic visual element; otherwise perform the agreed course-appropriate output analysis. | Example overlays/annotations or equivalent output evidence, review notes for difficult cases, and clear distinction between a suggestion and a verified result. |
| 09 `09-vision-error-analysis` | Inspect correct and incorrect outputs, including relevant synthetic image-condition slices. | Confusion/error evidence as appropriate to the task, representative failure images, slice/sample-size caveats, and suggested human-review handling. |
| 10 `10-aida2154-vision-report` | Summarize the approved vision experiment and explain whether it supports any limited role in the proposed workflow. | Reproducible course report, dataset documentation, baseline/method comparison, evaluation and error examples, limitations, responsible-use note, and human-review rule. |

## How to submit each exercise in D2L

For each project exercise, use its matching D2L project-exercise/checkpoint dropbox:

1. Push the completed exercise folder to this private project repository.
2. Open that exact folder on GitHub and copy its URL. Check that the URL names the correct course and exercise folder.
3. Paste the URL in the matching D2L project-exercise/checkpoint submission.
4. Include the latest commit ID and a short note stating what you completed and one limitation you found.
5. Attach an export only when the D2L instructions request it.
6. Submit by the due date shown for that D2L item. The due dates for regular course labs remain their normal published dates and are not extended by this project.

Each exercise should be reviewable from its own folder and commit history. Your instructor can check whether the required artifacts are present, whether the work is reproducible, and whether you explain the result and its limits. D2L is the official place for grades and formal feedback. These project exercises do not add a course grading weight; any score follows the approved course assessment structure and the instructions posted in D2L.

## End-of-project deliverables

When the three course strands are complete, the project repository should include the 30 exercise folders and the following integrated, course-separated final materials:

```text
AIDA_Izzy_HR_Onboarding_Project/
  .gitignore
  requirements.txt
  README.md
  AC-STUDENT-PROJECT-GUIDE.md
  TECH-STACK-AND-TOOLS.md
  shared/
    project-charter.md
    workflow-map/
    screen-mockups/
    synthetic-data/
      README.md
      generators/
    database/
      schema.sql
      seed_synthetic_data.py
      export_csv.py
    app/
      streamlit_app.py
  AIDA-1141/
    project-labs/
      01-workflow-question/ ... 10-aida1141-evidence-brief/
    final-project/
      README.md
      analysis/
      outputs/
      report.md
      decision-brief.md
  AIDA-2156/
    project-labs/
      01-intake-volume-profile/ ... 10-aida2156-exploration-report/
    final-project/
      README.md
      analysis/
      figures/
      report.md
      decision-brief.md
  AIDA-2154/
    project-labs/
      01-synthetic-image-specification/ ... 10-aida2154-vision-report/
    final-project/
      README.md
      data/
      analysis/
      outputs/
      report.md
      decision-brief.md
  final-integration/
    project-summary.md
    workflow-and-screen-storyboard/
    limitations-and-next-evidence.md
    demonstration-notes.md
    individual-reflection.md
    ai-use-declaration.md
```

For **each separate course final project**, prepare the files required by that course’s D2L instructions and rubric. At minimum, be ready to provide:

- a course-specific report answering that course’s question, using that course’s methods and evidence;
- runnable or inspectable analysis and setup/run instructions;
- the relevant synthetic-data or image documentation;
- results, figures/tables, evaluation and errors or uncertainty appropriate to that course;
- a decision brief that says what the evidence supports and what it cannot support;
- limitations, responsible-use considerations, and a clear human-review rule; and
- any course-required declaration, reflection, demonstration materials, or defence preparation.

The shared integration folder connects the three strands with one project question, a workflow diagram, and optional screen/storyboard views. The screen mockups explain the evidence; they are not a requirement to build a full application. Submit the three final projects separately through their respective D2L assignments, each at the official 25% course weight and according to its own rubric and directions. The project repository link does not replace a required D2L upload or export.

## Final check before each course submission

- I completed every required regular course lab and knowledge check separately.
- I used only the private repository and folder requested for this item.
- My project exercise files are pushed, visible on GitHub, and linked from the matching D2L submission.
- The code or notebook and documented data can be inspected or rerun.
- My report answers the question for this course; I have not used another course’s evidence as a substitute.
- I used synthetic data/images only and did not commit private information or credentials.
- My recommendation includes limitations and human review.
- I followed that course’s current D2L rubric, required format, submission instructions, and due date.
