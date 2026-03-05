"""
Load the sentence-transformers model and encode text to vectors.
Vectors are stored as bytes (float32) for the database.
"""

from pathlib import Path
from typing import List, Optional

import numpy as np

# Local model path (saved all-MiniLM-L6-v2.pt under ai_core/model)
_AI_CORE_DIR = Path(__file__).resolve().parent
MODEL_PATH = _AI_CORE_DIR / "model" / "all-MiniLM-L6-v2.pt"

# Dimension for this model; needed to decode bytes back to vector
EMBEDDING_DIM = 384

_model = None


def get_model():
    """Load and cache the sentence-transformers model from the local path."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for embeddings. "
                "Install with: pip install sentence-transformers"
            )
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Ensure the model is saved under ai_core/model/all-MiniLM-L6-v2.pt"
            )
        _model = SentenceTransformer(str(MODEL_PATH))
    return _model


def encode(text: str) -> bytes:
    """
    Encode a single text to a vector and return as bytes (float32) for storage.
    """
    if not (text or "").strip():
        return _zeros_bytes()
    model = get_model()
    vec = model.encode(text.strip(), convert_to_numpy=True)
    return vec.astype(np.float32).tobytes()


def encode_batch(texts: List[str]) -> List[bytes]:
    """Encode multiple texts in one call; returns list of bytes."""
    if not texts:
        return []
    # Filter empty; we'll return zero vectors for them to keep indices aligned if needed
    cleaned = [t.strip() if t else "" for t in texts]
    model = get_model()
    vecs = model.encode(cleaned, convert_to_numpy=True)
    out = []
    for v in vecs:
        out.append(v.astype(np.float32).tobytes())
    return out


def decode(blob: bytes) -> np.ndarray:
    """Convert stored bytes back to a float32 vector."""
    if not blob:
        return np.zeros(EMBEDDING_DIM, dtype=np.float32)
    return np.frombuffer(blob, dtype=np.float32)


def _zeros_bytes() -> bytes:
    return np.zeros(EMBEDDING_DIM, dtype=np.float32).tobytes()
