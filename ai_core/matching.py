"""
Similarity and ranking. No database dependency; works on vectors only.
When “what makes a good match” changes (e.g. weights, filters), update here.
"""

from typing import List, Tuple

import numpy as np

from .embeddings import decode, EMBEDDING_DIM


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two 1D vectors. Assumes they are non-zero."""
    a = np.asarray(a, dtype=np.float64).ravel()
    b = np.asarray(b, dtype=np.float64).ravel()
    if a.size != b.size:
        raise ValueError("Vectors must have the same length")
    n = np.dot(a, b)
    d = np.linalg.norm(a) * np.linalg.norm(b)
    if d == 0:
        return 0.0
    return float(n / d)


def rank_by_similarity(
    query_vec: bytes,
    candidate_vecs: List[Tuple[int, bytes]],
    top_k: int = 10,
) -> List[Tuple[int, float]]:
    """
    Rank candidates by cosine similarity to the query vector.
    query_vec: embedding bytes for the donor (or query) profile.
    candidate_vecs: list of (id, embedding_bytes) for NGOs.
    Returns list of (id, score) sorted descending by score, length up to top_k.
    """
    if not candidate_vecs:
        return []
    q = decode(query_vec)
    scores: List[Tuple[int, float]] = []
    for cid, c_blob in candidate_vecs:
        c = decode(c_blob) if c_blob else np.zeros(EMBEDDING_DIM, dtype=np.float32)
        s = cosine_similarity(q, c)
        scores.append((cid, float(s)))
    scores.sort(key=lambda x: -x[1])
    return scores[:top_k]
