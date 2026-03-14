"""
Build the text we send to the embedding model for donors and NGOs.

When the real Excel arrives and columns change, only this module should need
updates. Row is dict-like (e.g. sqlite3.Row) with keys: name, sectors, regions,
description, keywords.
"""

from typing import Any


def _get(row: Any, key: str) -> str:
    """Get string value from a row (dict or sqlite3.Row); empty if missing or None."""
    try:
        val = row.get(key) if hasattr(row, "get") else row[key]
    except (KeyError, TypeError, IndexError):
        return ""
    if val is None:
        return ""
    return str(val).strip()


def _join_parts(parts: list[str]) -> str:
    """Join non-empty parts with spaces."""
    return " ".join(p for p in parts if p)


def build_donor_profile_text(row: Any) -> str:
    """
    Build a single text string representing a donor for embedding.
    Used for semantic similarity with NGO profiles.
    """
    name = _get(row, "name")
    legal_form = _get(row, "legal_form")
    strategy = _get(row, "strategy")
    sectors = _get(row, "sectors")
    regions = _get(row, "regions")
    description = _get(row, "description")
    keywords = _get(row, "keywords")
    return _join_parts(
        [name, legal_form, strategy, sectors, regions, description, keywords]
    )


def build_ngo_profile_text(row: Any) -> str:
    """
    Build a single text string representing an NGO for embedding.
    """
    name = _get(row, "name")
    legal_form = _get(row, "legal_form")
    strategy = _get(row, "strategy")
    focus = _get(row, "focus")
    sectors = _get(row, "sectors")
    regions = _get(row, "regions")
    description = _get(row, "description")
    keywords = _get(row, "keywords")
    return _join_parts(
        [name, legal_form, strategy, focus, sectors, regions, description, keywords]
    )
