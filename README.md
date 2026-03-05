# HIGGS AI Platform

Internal platform to help HIGGS staff match donors with NGOs using AI. The app stores donor and NGO profiles, builds semantic embeddings, and returns the best NGO matches for each donor.

---

## Project setup (full story)

Do this once per machine (or after cloning the repo).

### 1. Get the code

**Git**

```bash
# Clone the repo (if you don’t have it yet)
git clone <repository-url>
cd higgs-ai-platform

# Or if you already have it, make sure you’re up to date
git pull
```

### 2. Python version

Use **Python 3.10 or newer**. Check:

```bash
python --version
```

If you need another version, install it (e.g. from python.org or pyenv) and use that `python` when creating the venv below.

### 3. Create and activate the virtual environment

All commands below are from the **project root** (`higgs-ai-platform`).

**Windows (PowerShell)** – if script execution is allowed:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If you get “running scripts is disabled”, use **Command Prompt (cmd)** instead:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Windows (Git Bash / WSL)** or **macOS / Linux**:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# or
source .venv/Scripts/activate   # Git Bash on Windows
```

You should see `(.venv)` in your prompt.

### 4. Install dependencies

With the venv active:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs FastAPI, PySide6, pandas, sentence-transformers, etc. The first time you use the AI (e.g. run the demo), sentence-transformers may download extra data; that’s normal.

### 5. Run the app

**Full app (backend + desktop UI):**

```bash
python run.py
```

This starts the FastAPI backend and the PySide6 window. Close the window to stop both.

**Backend only (e.g. to call the API with a browser or Postman):**

```bash
uvicorn backend.main_api:app --reload
```

Then open e.g. `http://127.0.0.1:8000/docs` for the API docs.

### 6. Useful Python commands (from project root, venv active)

| What you want to do              | Command |
|----------------------------------|---------|
| Run the full app                 | `python run.py` |
| Run backend only                 | `uvicorn backend.main_api:app --reload` |
| Test the database layer          | `python -m database.test_database` |
| Demo the AI matching pipeline    | `python -m ai_core.demo` |

### 7. Git workflow (reminder)

- **Branches**: work on feature branches (e.g. `database`, `ai-recommendation`); merge to `main` when ready.
- **Commits**: prefer small commits. Prefix with `feat:`, `fix:`, `update:`, or `delete:` when it helps.
- **Ignore**: don’t commit `.venv/`, `data/*.db`, or `__pycache__/`. They’re in `.gitignore`.

---

## Folder structure

Use this to find where things live.

```
higgs-ai-platform/
├── README.md                 ← you are here (setup + overview)
├── requirements.txt         ← Python dependencies
├── run.py                   ← starts backend + desktop UI
├── .gitignore
│
├── backend/                  ← FastAPI server (do not put DB or AI logic here)
│   └── main_api.py          ← API routes (login, GET .../donors/{id}/recommendations)
│
├── frontend/                 ← PySide6 desktop UI
│   └── main_ui.py
│
├── database/                 ← all database logic (SQLite, accounts, Excel import)
│   ├── README.md             ← short guide for the database layer
│   ├── DOCUMENTATION.md      ← function reference (inputs/outputs)
│   ├── __init__.py           ← initialize_all_databases()
│   ├── dataset_db.py         ← donors, NGOs, matches (dataset.db)
│   ├── accounts_db.py        ← user accounts (accounts.db)
│   ├── excel_import.py       ← load donors/NGOs from Excel
│   ├── mock_data.py          ← seed example donors and NGOs
│   ├── test_database.py      ← script to test DB + mock data + one test account
│   ├── helpers/
│   │   ├── __init__.py
│   │   └── search.py         ← find_ngos_by_sector, find_ngos_by_region, etc.
│   └── filters/              ← placeholder for future filters
│       └── __init__.py
│
├── ai_core/                  ← AI matching (embeddings + recommendations)
│   ├── README.md             ← short guide for the AI layer
│   ├── DOCUMENTATION.md      ← function reference (inputs/outputs)
│   ├── __init__.py
│   ├── api.py                ← ensure_embeddings(), get_recommendations_for_donor()
│   ├── profile.py            ← build_donor_profile_text(), build_ngo_profile_text()
│   ├── embeddings.py         ← load model, encode text to bytes
│   ├── matching.py           ← cosine similarity, rank_by_similarity()
│   ├── demo.py               ← python -m ai_core.demo (full pipeline demo)
│   └── model/                ← sentence-transformers model files
│       └── all-MiniLM-L6-v2.pt/
│
└── data/                     ← created at runtime (not in git)
    ├── dataset.db            ← donors, NGOs, donor_ngo_matches
    └── accounts.db           ← user accounts
```

**Summary**

- **Backend**: only API routes; it calls `database` and `ai_core`, it doesn’t implement DB or AI.
- **Database**: everything about storing and loading data (donors, NGOs, accounts, Excel, helpers).
- **ai_core**: everything about embeddings and matching; reads/writes via `database`.

---

## Where to read more

- **Database**: see `database/README.md` (overview) and `database/DOCUMENTATION.md` (every function).
- **AI**: see `ai_core/README.md` (overview) and `ai_core/DOCUMENTATION.md` (every function).
