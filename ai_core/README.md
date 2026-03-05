# ai_core

AI matching pipeline: turn donor and NGO profiles into embeddings and return the best NGO matches for a donor.

## Quick use

From backend or any code that has the project root on `sys.path`:

```python
import ai_core.api

# Optional: fill embeddings for all donors/NGOs that don't have one yet
ai_core.api.ensure_embeddings()

# Get top 10 NGO recommendations for donor with id 1
results = ai_core.api.get_recommendations_for_donor(1, top_k=10)

for r in results:
    print(r["score"], r["ngo"]["name"])
```

## Modules

- **api** – Main entry: `ensure_embeddings()`, `get_recommendations_for_donor(donor_id, top_k=10, ngo_ids=None, save_matches=False)`.
- **profile** – Builds the text we embed from a donor/NGO row. Change here when Excel columns change.
- **embeddings** – Loads the local sentence-transformers model and encodes text to bytes.
- **matching** – Cosine similarity and ranking; no DB. Change here if scoring logic changes.

## Model

The model lives under `ai_core/model/all-MiniLM-L6-v2.pt`. Install deps with `pip install -r requirements.txt` (includes `sentence-transformers`).
