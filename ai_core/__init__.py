"""
AI core: embeddings, matching, and recommendation API.
Use ai_core.api for high-level calls; use profile, embeddings, matching for customization.
"""

from . import api
from . import embeddings
from . import matching
from . import profile

__all__ = ["api", "embeddings", "matching", "profile"]
