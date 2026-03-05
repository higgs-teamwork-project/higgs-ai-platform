"""
Controller / API for the AI matching pipeline.
Call these from the backend or scripts; they orchestrate embeddings and DB.
"""

from typing import Any, List, Optional

import database.dataset_db as dataset_db
from . import embeddings
from . import matching
from . import profile


def ensure_embeddings() -> None:
    """
    Generate and store embeddings for every donor and NGO that does not have one.
    Safe to call repeatedly.
    """
    for row in dataset_db.list_donors():
        if row["embedding"]:
            continue
        text = profile.build_donor_profile_text(row)
        blob = embeddings.encode(text)
        dataset_db.update_donor_embedding(row["id"], blob)

    for row in dataset_db.list_ngos():
        if row["embedding"]:
            continue
        text = profile.build_ngo_profile_text(row)
        blob = embeddings.encode(text)
        dataset_db.update_ngo_embedding(row["id"], blob)


def _donor_embedding(donor_row: Any) -> bytes:
    """Return donor embedding bytes, computing and persisting if missing."""
    if donor_row["embedding"]:
        return donor_row["embedding"]
    text = profile.build_donor_profile_text(donor_row)
    blob = embeddings.encode(text)
    dataset_db.update_donor_embedding(donor_row["id"], blob)
    return blob


def _ngo_candidates(ngo_ids: Optional[List[int]] = None) -> List[Any]:
    """Return list of NGO rows, optionally filtered by ngo_ids."""
    rows = dataset_db.list_ngos()
    if ngo_ids is not None:
        ids_set = set(ngo_ids)
        rows = [r for r in rows if r["id"] in ids_set]
    return rows


def _ensure_ngo_embedding(ngo_row: Any) -> bytes:
    """Return NGO embedding bytes, computing and persisting if missing."""
    if ngo_row["embedding"]:
        return ngo_row["embedding"]
    text = profile.build_ngo_profile_text(ngo_row)
    blob = embeddings.encode(text)
    dataset_db.update_ngo_embedding(ngo_row["id"], blob)
    return blob


def get_recommendations_for_donor(
    donor_id: int,
    top_k: int = 10,
    ngo_ids: Optional[List[int]] = None,
    save_matches: bool = False,
) -> List[dict]:
    """
    Return the top-k recommended NGOs for a donor, by semantic similarity.

    donor_id: ID of the donor.
    top_k: maximum number of recommendations to return.
    ngo_ids: if provided, only consider these NGO IDs (e.g. from sector/region filters).
    save_matches: if True, write each (donor_id, ngo_id, similarity) to donor_ngo_matches.

    Returns a list of dicts: [{"ngo_id": int, "ngo": row_dict, "score": float}, ...]
    ordered by score descending. Row dict has keys like name, sectors, regions, description, keywords.
    """
    donor = dataset_db.get_donor(donor_id)
    if donor is None:
        return []

    query_vec = _donor_embedding(donor)
    candidates = _ngo_candidates(ngo_ids)
    if not candidates:
        return []

    # Build list of (ngo_id, embedding_bytes), computing embeddings where missing
    candidate_vecs: List[tuple] = []
    for ngo in candidates:
        blob = _ensure_ngo_embedding(ngo)
        candidate_vecs.append((ngo["id"], blob))

    ranked = matching.rank_by_similarity(query_vec, candidate_vecs, top_k=top_k)
    ngo_by_id = {n["id"]: n for n in candidates}

    results = []
    for ngo_id, score in ranked:
        ngo = dataset_db.get_ngo(ngo_id)  # fresh row for response
        ngo_dict = {k: ngo[k] for k in ngo.keys() if k != "embedding"} if ngo else {}
        results.append({"ngo_id": ngo_id, "ngo": ngo_dict, "score": score})
        if save_matches:
            dataset_db.save_match(donor_id, ngo_id, score)

    return results
