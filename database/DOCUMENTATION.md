## Database module reference

This file lists the main functions in the `database` package and what they do.  
Use this when you want to know the exact inputs and outputs.

---

### 1. `dataset_db` – donors, NGOs, and matches

Module: `database.dataset_db`

#### 1.1 `get_connection() -> sqlite3.Connection`

- **Purpose**: Open a connection to `data/dataset.db`.
- **Inputs**: none.
- **Output**: a `sqlite3.Connection` object with `row_factory` set so rows behave like dictionaries.
- **Notes**: usually you do not need this directly; prefer the helper functions below.

#### 1.2 `initialize_schema() -> None`

- **Purpose**: Create the tables `donors`, `ngos`, and `donor_ngo_matches` if they do not exist.
- **Inputs**: none.
- **Output**: `None`.
- **Side effects**: Creates or updates tables in `data/dataset.db`.

#### 1.3 `insert_donor(...) -> int`

Signature:

```python
insert_donor(
    name: str,
    sectors: Optional[Iterable[str]] = None,
    regions: Optional[Iterable[str]] = None,
    description: Optional[str] = None,
    keywords: Optional[Iterable[str]] = None,
    embedding: Optional[bytes] = None,
) -> int
```

- **Purpose**: Insert a donor record.
- **Inputs**:
  - `name` – donor name (required).
  - `sectors` – list of sector strings, e.g. `["Education", "Youth"]` (optional).
  - `regions` – list of region strings, e.g. `["Greece"]` (optional).
  - `description` – free‑text description (optional).
  - `keywords` – list of keyword strings, e.g. `["climate", "biodiversity"]` (optional).
  - `embedding` – raw bytes for the embedding vector (optional, can be `None` for now).
- **Output**: integer ID of the newly created donor (primary key).
- **Side effects**: Writes one row to the `donors` table.

#### 1.4 `insert_ngo(...) -> int`

Signature:

```python
insert_ngo(
    name: str,
    sectors: Optional[Iterable[str]] = None,
    regions: Optional[Iterable[str]] = None,
    description: Optional[str] = None,
    keywords: Optional[Iterable[str]] = None,
    embedding: Optional[bytes] = None,
) -> int
```

- **Purpose**: Insert an NGO record.
- **Inputs**: same meaning as `insert_donor`, but stored in the `ngos` table.
- **Output**: integer ID of the new NGO.
- **Side effects**: Writes one row to the `ngos` table.

#### 1.5 `list_donors() -> list[sqlite3.Row]`

- **Purpose**: Get all donors from the database.
- **Inputs**: none.
- **Output**: a list of `sqlite3.Row` objects.  
  Each row can be accessed like a dict: `row["id"]`, `row["name"]`, etc.
- **Side effects**: opens and closes a database connection.

#### 1.6 `list_ngos() -> list[sqlite3.Row]`

- **Purpose**: Get all NGOs from the database.
- **Inputs**: none.
- **Output**: a list of `sqlite3.Row` objects with NGO data.
- **Side effects**: opens and closes a database connection.

---

#### 1.7 `get_donor(donor_id: int) -> Optional[sqlite3.Row]`

- **Purpose**: Fetch a single donor by ID.
- **Inputs**:
  - `donor_id` – the primary key ID of the donor.
- **Output**:
  - A `sqlite3.Row` with the donor data, or `None` if no donor exists with that ID.

#### 1.8 `get_ngo(ngo_id: int) -> Optional[sqlite3.Row]`

- **Purpose**: Fetch a single NGO by ID.
- **Inputs**:
  - `ngo_id` – the primary key ID of the NGO.
- **Output**:
  - A `sqlite3.Row` with the NGO data, or `None` if no NGO exists with that ID.

#### 1.9 `update_donor_embedding(donor_id: int, embedding: bytes) -> None`

- **Purpose**: Update the embedding vector for a donor.
- **Inputs**:
  - `donor_id` – ID of the donor to update.
  - `embedding` – new embedding bytes to store.
- **Output**: `None`.
- **Side effects**: Updates the `embedding` column in the `donors` table.

#### 1.10 `update_ngo_embedding(ngo_id: int, embedding: bytes) -> None`

- **Purpose**: Update the embedding vector for an NGO.
- **Inputs**:
  - `ngo_id` – ID of the NGO to update.
  - `embedding` – new embedding bytes to store.
- **Output**: `None`.
- **Side effects**: Updates the `embedding` column in the `ngos` table.

#### 1.11 `save_match(donor_id: int, ngo_id: int, similarity: float, notes: Optional[str] = None) -> int`

- **Purpose**: Insert or update a similarity match between a donor and an NGO.
- **Inputs**:
  - `donor_id` – ID of the donor.
  - `ngo_id` – ID of the NGO.
  - `similarity` – similarity score (for example, cosine similarity).
  - `notes` – optional free‑text notes.
- **Output**: integer ID of the match row.
- **Side effects**:
  - Inserts a new row if no match exists for that `(donor_id, ngo_id)` pair.
  - If a row already exists, updates the `similarity` (and `notes` when provided).

---

### 2. `accounts_db` – user accounts

Module: `database.accounts_db`

#### 2.1 `get_connection() -> sqlite3.Connection`

- **Purpose**: Open a connection to `data/accounts.db`.
- **Inputs**: none.
- **Output**: a `sqlite3.Connection` object.
- **Notes**: normally you use the helper functions instead of this directly.

#### 2.2 `initialize_schema() -> None`

- **Purpose**: Create the `accounts` table if needed.
- **Inputs**: none.
- **Output**: `None`.
- **Side effects**: ensures the `accounts` table exists.

#### 2.3 `create_account(username: str, password: str, role: str | None = None) -> int`

- **Purpose**: Create a new user account.
- **Inputs**:
  - `username` – login name, must be unique.
  - `password` – plain‑text password to be hashed and stored.
  - `role` – optional string such as `"admin"` or `"staff"`.
- **Output**: integer ID of the new account.
- **Side effects**:
  - Generates a random salt.
  - Hashes the password with SHA‑256 and the salt.
  - Stores `username`, `password_hash`, `salt`, and `role` in the `accounts` table.

#### 2.4 `verify_credentials(username: str, password: str) -> bool`

- **Purpose**: Check if a username and password combination is valid.
- **Inputs**:
  - `username` – login name to check.
  - `password` – password provided by the user.
- **Output**:
  - `True` if the credentials are correct.
  - `False` if the user does not exist or the password does not match.
- **Side effects**: reads one row from the database, but does not modify any data.

---

### 3. `excel_import` – loading donors and NGOs from Excel

Module: `database.excel_import`

#### 3.1 `import_dataset_from_excel(excel_path: str | Path) -> None`

- **Purpose**: Read an Excel file and add donors and NGOs to the dataset database.
- **Inputs**:
  - `excel_path` – path to the Excel file (string or `Path`).
- **Expected Excel structure**:
  - Sheet `"Donors"` with columns: `name`, `sectors`, `regions`, `description`, `keywords`.
  - Sheet `"NGOs"` with the same column names.
- **Output**: `None`.
- **Side effects**:
  - Ensures dataset tables exist (`dataset_db.initialize_schema()`).
  - Inserts multiple rows into `donors` and `ngos`.
  - Raises `FileNotFoundError` if the file does not exist.

#### 3.2 Internal helpers

These functions are marked as "internal" and are not usually called from outside the module, but are documented here for completeness.

- `_import_organizations(df: pd.DataFrame, *, is_donor: bool) -> None`
  - Reads each row in a DataFrame and calls `insert_donor` or `insert_ngo`.
- `_safe_str(value: Optional[object]) -> Optional[str]`
  - Converts a value to a trimmed string or returns `None` if empty.
- `_split_optional(value: Optional[object]) -> list[str] | None`
  - Splits a comma‑separated string into a list of trimmed strings.

---

### 4. `mock_data` – example records

Module: `database.mock_data`

#### 4.1 `seed_mock_data() -> None`

- **Purpose**: Insert a small set of example donors and NGOs.
- **Inputs**: none.
- **Output**: `None`.
- **Side effects**:
  - Reads current donors and NGOs from the dataset database.
  - If there are already records, does nothing.
  - If the database is empty, inserts a few predefined donors and NGOs.

---

### 5. `database` package (`__init__.py`)

Module: `database`

#### 5.1 `initialize_all_databases() -> None`

- **Purpose**: Initialize both the dataset and accounts databases in one call.
- **Inputs**: none.
- **Output**: `None`.
- **Side effects**:
  - Calls `dataset_db.initialize_schema()`.
  - Calls `accounts_db.initialize_schema()`.

#### 5.2 Re-exported modules

The `database` package makes these modules available:

- `database.dataset_db`
- `database.accounts_db`
- `database.excel_import`
- `database.mock_data`

So you can import them simply with:

```python
import database

database.initialize_all_databases()
database.dataset_db.list_donors()
```

---

### 6. `helpers` – search helpers

Module: `database.helpers.search`

#### 6.1 `find_ngos_by_sector(sector: str) -> list`

- **Purpose**: Find NGOs whose `sectors` text contains the given sector (case-insensitive).
- **Inputs**:
  - `sector` – sector name fragment to search for, e.g. `"Environment"`.
- **Output**: a list of `sqlite3.Row` NGOs matching the condition.

#### 6.2 `find_ngos_by_region(region: str) -> list`

- **Purpose**: Find NGOs whose `regions` text contains the given region (case-insensitive).
- **Inputs**:
  - `region` – region fragment, e.g. `"Greece"` or `"Athens"`.
- **Output**: a list of `sqlite3.Row` NGOs matching the condition.

#### 6.3 `find_ngos_by_sectors_any(sectors: Iterable[str]) -> list`

- **Purpose**: Find NGOs that match **any** sector in a list.
- **Inputs**:
  - `sectors` – an iterable of sector strings; empty or all-empty input returns an empty list.
- **Output**: a list of `sqlite3.Row` NGOs that match at least one of the sectors.


