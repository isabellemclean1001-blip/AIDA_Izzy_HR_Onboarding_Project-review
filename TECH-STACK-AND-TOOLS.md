# Technology Stack and Tools for Your Project

## The recommendation

Use **one integrated project, one private GitHub repository, one local MariaDB database, and one Python 3.12 environment** for all 30 project exercises, the three course-specific analyses, and the small demonstration app.

The project is one fictional HR onboarding intake-and-routing workflow. Its data, database, code, and demo screens build on the same synthetic records. The AIDA 1141, AIDA 2156, and AIDA 2154 folders hold the different analysis and evidence required for each course; they are not separate software projects and do not need separate environments.

Use this single stack for your cross-course project in this repository. Continue to complete and submit regular weekly course labs as their D2L instructions direct.

## Your project tools

| Tool | What you will use it for |
|---|---|
| **Python 3.12** | The one project runtime for data preparation, EDA, the structured-data model, computer vision, and the local demo. Python 3.12 is a practical choice on Windows because the current PyTorch install guidance supports Windows with Python 3.9–3.12; Streamlit supports Python 3.12 as well. See [PyTorch installation guidance](https://docs.pytorch.org/get-started/locally/) and [Streamlit Python support](https://docs.streamlit.io/knowledge-base/using-streamlit/sanity-checks). |
| **Visual Studio Code** with the Python and Jupyter extensions | Open this repository, edit code/notebooks, and select the project interpreter. |
| **One project-root virtual environment** named `.venv` | Install and run one compatible package set for all of the project exercises. Do not create one environment per course or per lab. |
| **MariaDB Community Server, running locally** | Store only synthetic onboarding requests, routing suggestions, human decisions, and status history in the project database. |
| **DBeaver Community or a MariaDB client** (optional) | View and inspect the local synthetic database. This is a helper, not another programming stack. |
| **Python packages** | Use pandas and NumPy for data; Matplotlib/Seaborn for EDA; scikit-learn for structured-data models; OpenCV and Pillow for image processing; PyTorch/Torchvision for the small approved vision model; Streamlit for the local screens; and MariaDB Connector/Python for database access. |
| **CSV and generated image files** | Export documented data snapshots for reproducible analysis. Keep synthetic images as files with a manifest and labels; do not store employee documents or personal images. |
| **Git and this private GitHub repository** | Track and push all project exercises and integrated project work. Submit the matching folder link and commit ID in D2L as directed in the student project guide. |

The app is a small, local demonstration. It may show three connected views: (1) enter a synthetic onboarding request, (2) see a routing suggestion in a staff review queue, and (3) confirm the route and update completion status. The system must show that a person reviews and confirms suggestions. It is not a real HR application and does not connect to an ERP.

Streamlit is intended for Python data apps and supports a local development server. See its [official documentation](https://docs.streamlit.io/) and [data connection guidance](https://docs.streamlit.io/develop/concepts/connections/connecting-to-data). MariaDB provides an [official Python connector](https://mariadb.com/docs/connectors/mariadb-connector-python).

## How the three course strands connect

1. **Shared project data:** Generate a small, documented set of fictional onboarding requests. Store structured request and status data in MariaDB. Keep the schema, data generator, and a CSV export command in Git.
2. **AIDA 2156 exploration:** Use a CSV snapshot generated from those same synthetic records to examine data quality, intake volume, delay patterns, and handoffs.
3. **AIDA 1141 structured-data work:** Use the documented request fields and labels to build and evaluate a small routing suggestion. Save its outputs and state the cases that require human review.
4. **AIDA 2154 vision work:** Use only instructor-approved, computer-generated icons or mock visual cards associated with fictional requests. Save image files and their labels/metadata. Do not use real forms, employee documents, or personal photographs.
5. **Integrated demonstration:** The local Streamlit views connect intake, suggested route, human review, and status tracking using the same project database and outputs.

The course questions and final reports remain distinct even though they use one workflow and toolset. Keep course-specific evidence in its named folder and explain how that strand contributes to the shared workflow.

## One environment for the whole project

You will create **one** Python virtual environment at the root of this repository. Python documents virtual environments as isolated project package setups; this lets the project keep one reproducible package set without changing packages installed elsewhere on your computer. See [Python's virtual-environment guide](https://docs.python.org/3/tutorial/venv.html).

The project will use one repository-root `requirements.txt` containing a compatible, pinned set of all Python packages used across the project. Your instructor will provide that file before package installation. Do not create separate per-course package files, install a second course-specific project environment, or guess package versions.

After the project `requirements.txt` is present, open PowerShell at the repository root and run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python --version
```

Select the `.venv` interpreter in VS Code. When you return to this project later, activate the same environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Do not commit `.venv/`, package caches, local database passwords, or secret files. The repository's `.gitignore` excludes common local-only files.

## Database setup and safe data

- Run one local MariaDB database for this project. Use a dedicated project database and a non-administrator local account.
- Use only synthetic records and generated images. Do not connect to a live ERP, payroll system, HR system, or institutional database.
- Store the schema, synthetic-data generator, and seed/load scripts in the project repository.
- Keep database passwords and connection details in an untracked local configuration file. Commit only a placeholder example such as `.env.example`, never a working secret.
- Keep a CSV export of each analysis dataset so that the EDA and structured-data results can be reviewed without manually editing database tables.
- Keep generated images outside MariaDB and link them to fictional request IDs through a manifest.
- Never commit personal information, actual employer/client records, or confidential data.

## Suggested project layout

```text
AIDA_Izzy_HR_Onboarding_Project/
  .gitignore
  requirements.txt
  README.md
  AC-STUDENT-PROJECT-GUIDE.md
  TECH-STACK-AND-TOOLS.md
  shared/
    database/
      schema.sql
      seed_synthetic_data.py
      export_csv.py
    data/
      generated/
      exports/
    images/
      generated/
      image-manifest.csv
    app/
      streamlit_app.py
    workflow/
  AIDA-1141/
    project-labs/
    final-project/
  AIDA-2156/
    project-labs/
    final-project/
  AIDA-2154/
    project-labs/
    final-project/
```

Create each exercise folder when you start that exercise. Keep all three course strands, all 30 project exercises, and the integrated prototype in this repository. Your regular weekly course labs still go to the course repositories named in their D2L instructions.

## Your Git and D2L routine

For each completed project exercise:

```text
git status
git add AIDA-2156/project-labs/01-intake-volume-profile
git commit -m "AIDA 2156 project lab 01: profile intake volume"
git push
```

Change the folder and commit message to match the exercise. Open the folder on GitHub after pushing and confirm the files and commit are visible. Submit that folder's direct URL and the latest commit ID to its matching D2L project exercise. Follow the posted D2L due date and instructions. For regular course labs, use the D2L-assigned course repository and normal lab due date.

## ERP access is separate from this project

You do **not** need access to a live ERP, HR, payroll, or employee-record system to complete this project. The project uses synthetic data and the local project database. Do not use an ERP export or add real employee information to GitHub.

If you are separately asked to learn or help with ERP tasks, that is a different activity from this project. Use an approved training/demo environment with fake records where possible. Do not use another person's login. Any real-system account must be separately approved for a defined task and limited to the minimum access and time needed. The [Office of the Privacy Commissioner of Canada](https://www.priv.gc.ca/en/privacy-topics/employers-and-employees/02_05_d_17) recommends need-to-know access to employee information; [NIST's least-privilege principle](https://csrc.nist.gov/glossary/term/least_privilege) likewise calls for only the access needed for the task.
