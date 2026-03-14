## AI Core (short guide)

This folder contains the AI matching pipeline used by the **desktop app**’s backend: it turns donor and NGO profiles into text, encodes them with a sentence-transformers model, and ranks NGOs by similarity for each donor. The backend (FastAPI) calls this layer; it is not a public web API.

---

### 1. Files and what they are for

- `api.py` – main entry: build embeddings and get recommendations. Call this from the backend or scripts.
- `profile.py` – builds the text we send to the model from a donor or NGO row. Change here when Excel columns change.
- `embeddings.py` – loads the local model and encodes text to vectors (stored as bytes in the DB).
- `matching.py` – cosine similarity and ranking. No database; change here if scoring logic changes.
- `demo.py` – small script to run the full pipeline and print results (see below).
- `model/` – folder where the sentence-transformers model lives (`all-MiniLM-L6-v2.pt`).

---

### 2. Quick use (Python)

From the project root (with venv active):

```python
import ai_core.api

# Fill embeddings for all donors/NGOs that don't have one yet
ai_core.api.ensure_embeddings()

# Get top 10 NGO recommendations for donor id 1
results = ai_core.api.get_recommendations_for_donor(1, top_k=10)

for r in results:
    print(r["score"], r["ngo"]["name"])
```

---

### 3. Main functions (`api.py`)

- **`ensure_embeddings()`** – For every donor and NGO that has no embedding, build profile text, encode it, and save it to the database. Safe to call many times.
- **`get_recommendations_for_donor(donor_id, top_k=10, ngo_ids=None, save_matches=False)`**
  - Returns a list of `{"ngo_id", "ngo": {...}, "score": float}` sorted by score (best first). Use when the donor is stored in the DB.
  - `ngo_ids`: if provided, only those NGOs are considered.
  - `save_matches=True`: writes each (donor_id, ngo_id, similarity) into `donor_ngo_matches`.
- **`get_recommendations_for_donor_profile(donor_name, donor_strategy, top_k=50)`**
  - **Single-donor matchmaking**: donor is **not** in the DB; you pass name and strategy as strings. Returns list of `{"ngo_id", "ngo", "score"}` ranked by similarity. Used by `POST /api/matchmaking/generate`; the backend then normalizes scores to 0–100% and filters.

---

### 4. Profile text (`profile.py`)

- **`build_donor_profile_text(row)`** – Builds one string from name, sectors, regions, description, keywords.
- **`build_ngo_profile_text(row)`** – Same for an NGO row.

When the real Excel arrives and columns or fields change, only these two functions need to be updated so the model still gets the right input.

---

### 5. Embeddings and matching

- **`embeddings.encode(text)`** – One text → bytes (float32 vector). Used to store in the DB.
- **`embeddings.decode(blob)`** – Bytes → numpy vector for similarity.
- **`matching.rank_by_similarity(query_vec, candidate_vecs, top_k)`** – Ranks by cosine similarity. Inputs are bytes; returns list of `(id, score)`.

---

### 6. Demo and test scripts

- **`python scripts/run_ai_demo.py`** – Uses your existing donors and NGOs (load them first with the import scripts). Builds embeddings, then prints top-5 NGO matches for the first 3 donors. No mock data.
- **`python -m ai_core.demo`** – Same idea; uses whatever is in the DB (no mock seed). Builds embeddings and prints top-3 matches per donor.
- **`python scripts/test_matchmaking_api.py`** – Backend test: list NGOs/donors, call matchmaking generate/export with real-sounding donors, validate 400 for missing fields. Requires backend running (`uvicorn backend.main_api:app --reload`).

---

### 7. HTTP API (matchmaking and recommendations)

The backend exposes:

- **`GET /api/donors/{donor_id}/recommendations?top_k=10&save_matches=false`**  
  For donors stored in the DB. Returns `{"donor_id", "recommendations": [{ "ngo_id", "ngo", "score" }, ...]}`.

- **`POST /api/matchmaking/generate`**  
  Single-donor matchmaking (donor not in DB). Body: `{ "donor_name", "donor_strategy", "match_threshold_percent"?: number }`. Returns matches with **normalized scores** (0–100%, best = 100%) and drops matches too far below the top. Uses `get_recommendations_for_donor_profile` then normalizes in the backend.

- **`POST /api/matchmaking/export`**  
  Same body as generate. Runs matchmaking and **writes the CSV to `data/export_file/matchmaking_results.csv`** (overwrites each time). Returns JSON: `{ "saved_to", "path_absolute", "filename", "total_matched" }`. The desktop app can open the file at `path_absolute`.

- **`POST /api/ensure-embeddings`**  
  Precompute embeddings for all donors and NGOs that don't have one.

---

### 8. Dependencies

Install with `pip install -r requirements.txt` from the project root. The AI part needs `sentence-transformers` and `numpy`. The model files must be present under `ai_core/model/all-MiniLM-L6-v2.pt`.
