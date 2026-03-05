## Database Layer (short guide)

This folder contains the code that talks to the SQLite databases.  

---

### 1. Files and what they are for

- `dataset_db.py` – saves **donors**, **NGOs**, and their **match scores**.
- `accounts_db.py` – saves **user accounts** (username + password hash).
- `excel_import.py` – reads an **Excel file** and fills the dataset database.
- `mock_data.py` – adds a **few example donors and NGOs** so you can test quickly.
- `__init__.py` – provides shortcuts like `initialize_all_databases()`.

All database files are created automatically in the `data/` folder in the project root:

- `data/dataset.db` – donors, NGOs, matches.
- `data/accounts.db` – user accounts.


---

### 2. Working with donors and NGOs (`dataset_db.py`)

This module holds the data used by the AI matching.

- **Tables**
  - `donors`
  - `ngos`
  - `donor_ngo_matches`

- **Useful functions**
  - `initialize_schema()` – creates the tables if they do not exist. Safe to call many times.
  - `insert_donor(name, sectors, regions, description, keywords, embedding=None)` – adds a donor.
  - `insert_ngo(name, sectors, regions, description, keywords, embedding=None)` – adds an NGO.
  - `list_donors()` – returns all donors.
  - `list_ngos()` – returns all NGOs.

`sectors`, `regions`, and `keywords` are **lists of strings** (or `None`). The code stores them as text inside the database.

**Example (Python):**

```python
from database import dataset_db

dataset_db.initialize_schema()

dataset_db.insert_donor(
    name="Example Donor",
    sectors=["Education", "Youth"],
    regions=["Greece"],
    description="Supports education programs for young people.",
    keywords=["education", "youth"],
)

for donor in dataset_db.list_donors():
    print(donor["id"], donor["name"])
```

---

### 3. Working with user accounts (`accounts_db.py`)

This module stores login accounts for HIGGS staff.

- **Table**
  - `accounts` with:
    - `username` (unique)
    - `password_hash` (secure hash, not plain text)
    - `salt`
    - `role` (optional, e.g. `"admin"`, `"staff"`)

- **Useful functions**
  - `initialize_schema()` – creates the table if needed.
  - `create_account(username, password, role=None)` – creates a new account and returns its ID.
  - `verify_credentials(username, password) -> bool` – checks if login details are valid.

 The code saves a salted SHA‑256 hash instead.

**Example (Python):**

```python
from database import accounts_db

accounts_db.initialize_schema()
accounts_db.create_account("admin@higgs.org", "password123", role="admin")

if accounts_db.verify_credentials("admin@higgs.org", "password123"):
    print("Login OK")
else:
    print("Login failed")
```

---

### 4. Importing data from Excel (`excel_import.py`)

Use this module when you receive an Excel file with donor and NGO information.

It expects an Excel file with:

- Sheet **`Donors`** – columns:
  - `name`, `sectors`, `regions`, `description`, `keywords`
- Sheet **`NGOs`** – same columns.

- **Main function**
  - `import_dataset_from_excel(excel_path)`
    - Sets up the dataset tables.
    - Reads data from the Excel file.
    - Inserts donors and NGOs into the database.

`sectors`, `regions`, `keywords` can be comma‑separated strings (for example `"Education, Youth"`).

**Example (Python):**

```python
from database import excel_import

excel_import.import_dataset_from_excel("higgs_dataset.xlsx")
```

---

### 5. Adding example data (`mock_data.py`)

This module adds a few sample donors and NGOs so the system works even if you do not have real data yet.

- **Main function**
  - `seed_mock_data()`
    - If the database is empty, it inserts a few example records.
    - If there is already data, it does nothing.

The backend already calls this function on startup.

---

### 6. Initializing everything (`__init__.py`)


```python
import database

database.initialize_all_databases()
```

This will:

1. Create or update `dataset.db` tables.
2. Create or update `accounts.db` tables.

You can call this once when the app starts.

---

### 7. Helpers and filters

- `helpers/` – contains extra search helpers like `helpers.search.find_ngos_by_sector(...)`.
- `filters/` – reserved for future reusable filters once the final dataset is known.

---

