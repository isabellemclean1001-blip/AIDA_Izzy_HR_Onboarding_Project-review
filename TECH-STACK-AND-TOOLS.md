# AC Project Technology Stack and Tools

This guide gives the project one manageable, reproducible toolset for AIDA 1141, AIDA 2156, and AIDA 2154. Follow the exact package list and submission requirements in the relevant D2L instructions when they differ from this guide.

## Recommended stack

| Need | Recommended tool | How it is used |
|---|---|---|
| Programming language | **Python 3.12** | Shared foundation for the three project strands. Use the Python version and package pins named by the course starter if it specifies a more exact version. |
| Code editor | **Visual Studio Code** with the Python and Jupyter extensions | Edit scripts and notebooks, choose the correct interpreter, and run the course work locally. |
| Reproducible environments | **One Python virtual environment per course strand** | Keep course package versions separate. Use the provided course requirements file; do not install everything into one global Python environment. |
| Data exchange | **Small synthetic CSV files** and documented image files | Use CSV as the simple, inspectable handoff between data preparation, exploratory analysis, and structured-data analysis. Generate and document all records and images; never use actual employee records or documents. |
| Source control and evidence | **The private GitHub project repository** | Keep the AC-specific project exercises and integrated project here. Commit meaningful changes and submit the direct folder URL and commit ID in the matching D2L item. Regular graded course labs still go to the repository specified in each lab’s D2L instructions. |
| Optional relational storage | **Local MariaDB, only if approved for a specific learning outcome** | Use only a local development instance with synthetic data. Keep the CSV export and setup script so the analysis remains reproducible without a running database. MariaDB is not needed just to make the three analyses connect. |
| Workflow/screens | **A workflow diagram and a few screen mockups** made in a familiar drawing or presentation tool | Explain the intake, suggested route, human review, and tracking steps. Treat screens as illustrations; do not build a web application unless the instructor separately approves that scope. |

Python is the right common starting point: the AIDA 1141 setup already uses Python, VS Code, Jupyter, and scikit-learn, while the AIDA 2156 project materials provide a pinned Python environment and an offline CSV path. Separate virtual environments help prevent one course's library versions from disrupting another's. Python's official documentation describes virtual environments as isolated installations for project-specific packages, and VS Code can detect and select them. See [Python virtual environments](https://docs.python.org/3/tutorial/venv.html) and [Python in VS Code](https://code.visualstudio.com/docs/languages/python).

## Libraries by course

Install only what the specific exercise needs, using the course-provided requirements file where available.

### AIDA 1141 — structured-data analysis

- **pandas** and **NumPy** for loading, checking, and preparing the synthetic request table;
- **scikit-learn** for a course-appropriate baseline/model and evaluation; and
- **Jupyter** for exploration, with a clean run order and explanations, or a Python script when the lab starter expects a script.

### AIDA 2156 — Exploratory Data Analysis

- **pandas** and **NumPy** for data quality checks, summaries, and sensitivity checks;
- **Matplotlib** (and **Seaborn** only if useful/approved) for readable plots; and
- **Jupyter Notebook** or the course-specified script/report format for a reproducible exploration.

Use the CSV fallback unless an exercise explicitly requires an approved database source. The existing AIDA 2156 final-project starter is designed to run offline from CSV; a live database is not a prerequisite.

### AIDA 2154 — Computer Vision

- **OpenCV-Python** and **Pillow** for image inspection, preprocessing, filtering, feature or region work, and saved visual evidence;
- **PyTorch** and **Torchvision** only for the course exercises that require neural-network or transfer-learning work; and
- a documented CPU run command unless the course starter explicitly provides another supported option.

The course project should use only the small, computer-generated, non-personal image set approved at the scope checkpoint. The AIDA 2154 starter packages use OpenCV for image-processing work and PyTorch/Torchvision for the transfer-learning strand; the official [OpenCV-Python tutorials](https://docs.opencv.org/5.0/py_tutorials/py_setup/py_intro/py_intro.html) and [PyTorch transfer-learning tutorial](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html) are suitable references when those methods are part of the assigned course work.

## MariaDB: keep it optional

**Recommendation: keep Python; do not make MariaDB a required dependency for all 30 exercises.** A small CSV file is easier to inspect, share through the private project repository, and rerun for EDA and model analysis. Requiring a database service would add server setup, accounts, connection configuration, and secret handling without being necessary for the current three course questions.

MariaDB can be a useful **optional extension** if the instructor confirms that relational schema design, SQL queries, or persistence is an explicit course outcome for this project. If approved:

1. Install/run MariaDB locally on AC’s computer; do not connect to a live business or institutional database.
2. Use only synthetic records and generated metadata.
3. Keep schema-creation and synthetic-load scripts in Git; keep passwords, connection strings, and local `.env` files out of Git.
4. Keep a documented CSV export as the reproducible fallback for analysis.
5. Use a dedicated local project database and a non-administrator account; do not use a shared/root account.
6. Do not make successful access to MariaDB a prerequisite for the EDA or vision tasks.

If an approved local database connection is needed, MariaDB publishes an official Python connector. Its installation and connection details belong in a separate course-approved setup note, not in a shared credential or a committed connection string. See [MariaDB Connector/Python](https://mariadb.com/docs/connectors/mariadb-connector-python).

## Repository layout and environment files

Keep the project repository organized by course. Use the course-specific environment file where versions differ:

```text
AIDA_Izzy_HR_Onboarding_Project/
  .gitignore
  README.md
  AC-STUDENT-PROJECT-GUIDE.md
  TECH-STACK-AND-TOOLS.md
  shared/
    synthetic-data/
    workflow/
  AIDA-1141/
    requirements.txt
    project-labs/
    final-project/
  AIDA-2156/
    requirements.txt
    project-labs/
    final-project/
  AIDA-2154/
    requirements.txt
    project-labs/
    final-project/
```

Do not commit `.venv/`, Python cache folders, notebook checkpoints, secrets, real employee data, or unapproved datasets. A requirements file records packages, not credentials. Follow any additional course-provided ignore or packaging instructions.

## Simple setup on Windows

Use the Python version named in the course instructions. Create one environment per course when you begin that course strand. **Install from the exact requirements file linked or supplied by the instructor for the project.** The example below assumes the instructor has supplied `AIDA-2156/requirements.txt`; if that file is not present yet, do not create a package list or guess versions—ask for the setup instructions first.

```powershell
py -3.12 -m venv .venv-2156
.\.venv-2156\Scripts\Activate.ps1
python -m pip install -r AIDA-2156\requirements.txt
python --version
deactivate
```

For AIDA 1141 and AIDA 2154, repeat with environment names `.venv-1141` and `.venv-2154` and the matching requirements file supplied or identified by the instructor. If the course package already supplies exact version pins or a tested runtime, use those instead of inventing new versions. Keep all virtual environments local; do not push them to GitHub.

## Git and D2L tools

Use Git for the complete project folder and its history:

```text
git status
git add AIDA-2156/project-labs/01-intake-volume-profile
git commit -m "AIDA 2156 project lab 01: profile intake volume"
git push
```

After pushing, open the exact folder on GitHub. Copy that folder’s URL into the corresponding D2L project-exercise/checkpoint item, and include the latest commit ID and a short completion note. Continue to submit official weekly labs to the course repository and D2L assignment named in each official lab's instructions. Do not use this one project repository as a substitute for the regular course lab repositories.

## ERP access

**Do not provide AC with an account in a live ERP, HR, payroll, or employee-record system for this academic project.** The proposed work uses synthetic data and does not need production-system access. Do not export actual employee information into this GitHub repository or any student workspace.

If AC separately needs to learn or assist with ERP tasks, treat that as a separate, authorized activity—not as a project requirement. Use the ERP vendor’s training/demo environment with fake records where possible. If a real system account is ever considered, first have the system owner and the institution/business security or privacy contact approve a specific role, purpose, permitted records/actions, and end date. Grant only the minimum access needed for that defined task; do not share an owner/admin account or credentials. The Office of the Privacy Commissioner of Canada recommends limiting access to employee information on a need-to-know basis and safeguarding it against inappropriate access or disclosure; see [Privacy in the Workplace](https://www.priv.gc.ca/en/privacy-topics/employers-and-employees/02_05_d_17). The general least-privilege principle is also described by [NIST](https://csrc.nist.gov/glossary/term/least_privilege).

## Scope checkpoint

Before the student installs an additional service or builds a larger prototype, confirm the project question, course fit, data/image source, deliverables, and approved tools with the instructor. In particular:

- approve whether the AIDA 2154 image question fits the course outcomes;
- decide whether a local MariaDB component adds an assessed learning outcome; and
- keep any optional screen mockup small enough that it explains the analysis without becoming a separate application build.
