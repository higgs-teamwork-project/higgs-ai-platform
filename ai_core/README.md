## AI Core (short guide)

This folder contains the AI matching pipeline: it turns donor and NGO profiles into text, encodes them with a sentence-transformers model, and ranks NGOs by similarity for each donor.

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
  - Returns a list of `{"ngo_id", "ngo": {...}, "score": float}` sorted by score (best first).
  - `ngo_ids`: if you pass a list of NGO IDs, only those NGOs are considered (e.g. after sector/region filters).
  - `save_matches=True`: also writes each (donor_id, ngo_id, similarity) into the `donor_ngo_matches` table.

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

### 6. Demo script

To see the full pipeline (DB + embeddings + recommendations) in one go:

```bash
python -m ai_core.demo
```

This initializes the database, seeds mock data, builds embeddings, and prints top NGO matches for each donor. First run can be slow while the model loads.

---

### 7. HTTP API

The backend exposes:

- **`GET /api/donors/{donor_id}/recommendations?top_k=10&save_matches=false`**

Returns `{"donor_id": 1, "recommendations": [{ "ngo_id", "ngo", "score" }, ...]}`.

---

### 8. Dependencies

Install with `pip install -r requirements.txt` from the project root. The AI part needs `sentence-transformers` and `numpy`. The model files must be present under `ai_core/model/all-MiniLM-L6-v2.pt`.
