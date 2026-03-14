# HIGGS AI Platform

**Desktop application** (PySide6) for HIGGS staff to match donors with NGOs using AI. The app stores donor and NGO profiles, builds semantic embeddings, and returns the best NGO matches for each donor.

- **Desktop app**: the UI runs on your machine; you start it with `python run.py`.
- **Backend**: a local FastAPI server that the desktop app talks to. It is not a public web API—it serves only this desktop client. Routes are referred to as “endpoints” or “backend routes” in the docs.

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

**Full desktop app (recommended):**

```bash
python run.py
```

This starts the **backend** (FastAPI) and the **desktop window** (PySide6). The desktop app talks to the backend over HTTP on localhost. Close the window to stop both.

**Backend only** (e.g. for scripts or debugging):

```bash
uvicorn backend.main_api:app --reload
```

Then you can call the endpoints from scripts or open `http://127.0.0.1:8000/docs` for the interactive docs.

### 6. Useful commands (from project root, venv active)

| What you want to do              | Command |
|----------------------------------|---------|
| Run the full app                 | `python run.py` |
| Run backend only                 | `uvicorn backend.main_api:app --reload` |
| **Load donors** (Book 1 Excel)   | `python scripts/import_donors_book1.py` or `python scripts/import_donors_book1.py path/to/book1.xlsx` |
| **Load NGOs** (Book 2 Excel)     | `python scripts/import_ngos_book2.py` or `python scripts/import_ngos_book2.py path/to/book2.xlsx` |
| Precompute embeddings            | `python scripts/run_ai_demo.py` (or call `POST /api/ensure-embeddings` after backend is up) |
| Demo AI matching (your data)     | `python scripts/run_ai_demo.py` |
| Test matchmaking API (backend)   | `python scripts/test_matchmaking_api.py` (backend must be running) |
| Test the database layer          | `python -m database.test_database` |
| Demo AI (legacy, no mock seed)    | `python -m ai_core.demo` |

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
├── scripts/                  ← data loading and tests (run from project root)
│   ├── import_donors_book1.py   ← load donors from Book 1 Excel
│   ├── import_ngos_book2.py     ← load NGOs from Book 2 Excel
│   ├── run_ai_demo.py           ← build embeddings, show top matches for first donors
│   └── test_matchmaking_api.py  ← HTTP tests for matchmaking (backend must be up)
│
├── backend/                  ← FastAPI server (do not put DB or AI logic here)
│   └── main_api.py          ← API routes (login, matchmaking, donors, NGOs)
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
│   ├── api.py                ← ensure_embeddings(), get_recommendations_for_donor(), get_recommendations_for_donor_profile()
│   ├── profile.py            ← build_donor_profile_text(), build_ngo_profile_text()
│   ├── embeddings.py         ← load model, encode text to bytes
│   ├── matching.py           ← cosine similarity, rank_by_similarity()
│   ├── demo.py               ← python -m ai_core.demo (full pipeline demo)
│   └── model/                ← sentence-transformers model files
│       └── all-MiniLM-L6-v2.pt/
│
└── data/                     ← created at runtime (not in git)
    ├── dataset.db            ← donors, NGOs, donor_ngo_matches
    ├── accounts.db           ← user accounts
    ├── imports/              ← uploaded Excel files (from desktop app)
    └── export_file/          ← matchmaking CSV written here (overwritten each export)
        └── matchmaking_results.csv
```

**Summary**

- **Desktop app**: PySide6 UI; talks to the backend over HTTP. Run with `python run.py`.
- **Backend**: FastAPI server used by the desktop app (and by scripts). It only routes requests; it calls `database` and `ai_core`, it does not implement DB or AI.
- **Database**: everything about storing and loading data (donors, NGOs, accounts, Excel, helpers).
- **ai_core**: everything about embeddings and matching; reads/writes via `database`.

---

## Matchmaking (for the backend / desktop app)

Matchmaking is **single-donor**: the user enters one donor's name and strategy; the backend ranks NGOs in the database by semantic similarity and returns normalized scores (0–100%).

### Data flow

- **Donors** and **NGOs** live in the same database (`data/dataset.db`) in different tables: `donors` and `ngos`. You can load donors from Book 1 and NGOs from Book 2 independently.
- **Single-donor matchmaking** does **not** store the donor: the request body sends `donor_name` and `donor_strategy`; the backend builds an embedding from that text and compares it to all NGO embeddings in the DB.
- **Scores**: raw AI scores (e.g. 0.45) are normalized so the best match = 100%; matches too far below the top are dropped. Optional `match_threshold_percent` filters by minimum %.

### Backend endpoints (matchmaking)

| Method / endpoint | Purpose |
|-------------------|--------|
| `POST /api/matchmaking/generate` | Body: `{ "donor_name", "donor_strategy", "match_threshold_percent"?: number }`. Returns `{ donor_name, matches: [...], total_matched }`. |
| `POST /api/matchmaking/export`  | Same body as generate. Writes CSV to **`data/export_file/matchmaking_results.csv`** (overwrites each time), returns JSON: `{ "saved_to", "path_absolute", "filename", "total_matched" }`. |
| `POST /api/ngos`                 | Add one NGO: body `{ name, strategy?, focus?, legal_form? }`. |
| `DELETE /api/ngos`               | Delete NGOs: body `{ "ids": [1, 2, 3] }`. |
| `POST /api/ensure-embeddings`    | Precompute embeddings for all donors and NGOs that don't have one. |

### Where is the CSV file?

The matchmaking export **writes the CSV into the app** so the desktop app can open it without a “save as” dialog:

- **Path**: `data/export_file/matchmaking_results.csv` (relative to project root).
- **Behaviour**: Each time the user runs matchmaking and exports, this file is **overwritten**. So there is always one latest result file.
- The export endpoint returns JSON with `saved_to` (relative path) and `path_absolute` (full path) so the desktop app can open or show the file.

### Loading data and testing (quick reference)

1. Load donors: `python scripts/import_donors_book1.py` (put `book1.xlsx` in project root or pass path).
2. Load NGOs: `python scripts/import_ngos_book2.py` (put `book2.xlsx` in project root or pass path).
3. Start backend: `uvicorn backend.main_api:app --reload`.
4. Optionally precompute embeddings: `POST /api/ensure-embeddings` or run `python scripts/run_ai_demo.py` once.
5. Test matchmaking API: `python scripts/test_matchmaking_api.py` .

---

## Where to read more

- **Database**: see `database/README.md` (overview) and `database/DOCUMENTATION.md` (every function).
- **AI**: see `ai_core/README.md` (overview) and `ai_core/DOCUMENTATION.md` (every function).
