## AI Core – method reference

This file lists the main functions in the `ai_core` package: purpose, inputs, outputs, and side effects. Use it when you need the exact behaviour of each call.

---

### 1. `api` – controller / entry points

Module: `ai_core.api`

#### 1.1 `ensure_embeddings() -> None`

- **Purpose**: Generate and store embeddings for every donor and NGO that does not yet have an embedding.
- **Inputs**: none.
- **Output**: `None`.
- **Side effects**:
  - Reads all donors and NGOs from the database.
  - For each row without an embedding: builds profile text (via `profile`), encodes it (via `embeddings`), writes the result to the DB (`dataset_db.update_donor_embedding` / `update_ngo_embedding`).
- **Notes**: Safe to call repeatedly; only missing embeddings are computed.

#### 1.2 `get_recommendations_for_donor(donor_id, top_k=10, ngo_ids=None, save_matches=False) -> List[dict]`

- **Purpose**: Return the top-k recommended NGOs for a donor, ranked by semantic (cosine) similarity.
- **Inputs**:
  - `donor_id` (int) – ID of the donor.
  - `top_k` (int, default 10) – maximum number of recommendations to return.
  - `ngo_ids` (optional list of int) – if provided, only these NGO IDs are considered (e.g. after sector/region filters).
  - `save_matches` (bool, default False) – if True, each (donor_id, ngo_id, similarity) is written to `donor_ngo_matches`.
- **Output**: List of dicts, each with:
  - `"ngo_id"` (int)
  - `"ngo"` (dict) – NGO row as dict, without the `embedding` field (keys: id, name, sectors, regions, description, keywords, created_at).
  - `"score"` (float) – similarity score (higher = better match).
  Sorted by score descending, length at most `top_k`.
- **Side effects**:
  - May compute and persist donor/NGO embeddings if they were missing.
  - If `save_matches=True`, inserts/updates rows in `donor_ngo_matches`.
- **Notes**: Returns an empty list if the donor does not exist.

---

### 2. `profile` – text used for embeddings

Module: `ai_core.profile`

#### 2.1 `build_donor_profile_text(row) -> str`

- **Purpose**: Build a single string from a donor row for the embedding model.
- **Inputs**: `row` – dict-like or sqlite3.Row with keys: name, sectors, regions, description, keywords (missing/None become empty).
- **Output**: One string with non-empty fields joined by spaces.
- **Side effects**: none.

#### 2.2 `build_ngo_profile_text(row) -> str`

- **Purpose**: Same as above for an NGO row.
- **Inputs**: same shape as donor row.
- **Output**: one string.
- **Side effects**: none.

---

### 3. `embeddings` – model and encoding

Module: `ai_core.embeddings`

#### 3.1 `get_model()`

- **Purpose**: Load and cache the sentence-transformers model from `ai_core/model/all-MiniLM-L6-v2.pt`.
- **Inputs**: none.
- **Output**: the loaded model (cached for later calls).
- **Side effects**: first call loads from disk; raises `FileNotFoundError` if the model path is missing, `ImportError` if `sentence-transformers` is not installed.

#### 3.2 `encode(text: str) -> bytes`

- **Purpose**: Encode one text to a vector and return it as bytes (float32) for storage in the DB.
- **Inputs**: `text` – string; empty or whitespace-only yields a zero vector.
- **Output**: bytes (length depends on `EMBEDDING_DIM`, 384 for this model).
- **Side effects**: may load the model on first use.

#### 3.3 `encode_batch(texts: List[str]) -> List[bytes]`

- **Purpose**: Encode multiple texts in one call.
- **Inputs**: list of strings.
- **Output**: list of bytes, same length as input.
- **Side effects**: may load the model on first use.

#### 3.4 `decode(blob: bytes) -> np.ndarray`

- **Purpose**: Convert stored bytes back to a float32 vector.
- **Inputs**: `blob` – bytes from `encode`; empty or None yields a zero vector of length `EMBEDDING_DIM`.
- **Output**: 1D numpy array of dtype float32, length 384.
- **Side effects**: none.

#### 3.5 Constants

- **`MODEL_PATH`** – path to the model directory (`ai_core/model/all-MiniLM-L6-v2.pt`).
- **`EMBEDDING_DIM`** – 384 for this model.

---

### 4. `matching` – similarity and ranking

Module: `ai_core.matching`

#### 4.1 `cosine_similarity(a: np.ndarray, b: np.ndarray) -> float`

- **Purpose**: Cosine similarity between two 1D vectors.
- **Inputs**: `a`, `b` – arrays of the same length.
- **Output**: float in [-1, 1] (typically [0, 1] for normalized embeddings). 0 if either norm is zero.
- **Side effects**: none.

#### 4.2 `rank_by_similarity(query_vec: bytes, candidate_vecs: List[Tuple[int, bytes]], top_k: int = 10) -> List[Tuple[int, float]]`

- **Purpose**: Rank candidates by cosine similarity to the query vector.
- **Inputs**:
  - `query_vec` – embedding bytes (e.g. donor).
  - `candidate_vecs` – list of `(id, embedding_bytes)` (e.g. NGO id and embedding).
  - `top_k` – maximum number of results.
- **Output**: list of `(id, score)` sorted by score descending, length at most `top_k`.
- **Side effects**: none. Uses `embeddings.decode` internally.

---

### 5. `demo` – runnable demo

Module: `ai_core.demo` (run as `python -m ai_core.demo`)

#### 5.1 `main() -> None`

- **Purpose**: Run a full demo: init DB, seed mock data, build embeddings, run recommendations for each donor, print results.
- **Inputs**: none (reads from database, writes embeddings if missing).
- **Output**: none (prints to stdout).
- **Side effects**:
  - Calls `database.initialize_all_databases()` and `database.mock_data.seed_mock_data()`.
  - Calls `ai_core.api.ensure_embeddings()`.
  - For each donor, calls `get_recommendations_for_donor(donor_id, top_k=3, save_matches=False)` and prints donor name, then top 3 NGOs with score and sectors.
