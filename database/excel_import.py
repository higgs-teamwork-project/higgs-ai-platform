from pathlib import Path
from typing import Optional

import pandas as pd

from . import dataset_db


def import_dataset_from_excel(excel_path: str | Path) -> None:
    """
    Read an Excel file and insert donors and NGOs into the dataset database.

    Expected structure (can be adjusted later when the real file arrives):
    - Sheet 'Donors' with columns: name, sectors, regions, description, keywords
    - Sheet 'NGOs'   with columns: name, sectors, regions, description, keywords
    """
    excel_path = Path(excel_path)
    if not excel_path.exists():
        raise FileNotFoundError(excel_path)

    # Make sure DB schema exists before inserting
    dataset_db.initialize_schema()

    xls = pd.ExcelFile(excel_path)

    if "Donors" in xls.sheet_names:
        donors_df = xls.parse("Donors")
        _import_organizations(donors_df, is_donor=True)

    if "NGOs" in xls.sheet_names:
        ngos_df = xls.parse("NGOs")
        _import_organizations(ngos_df, is_donor=False)


def _import_organizations(df: "pd.DataFrame", *, is_donor: bool) -> None:
    for _, row in df.iterrows():
        name = _safe_str(row.get("name"))
        if not name:
            continue

        sectors = _split_optional(row.get("sectors"))
        regions = _split_optional(row.get("regions"))
        description = _safe_str(row.get("description"))
        keywords = _split_optional(row.get("keywords"))

        if is_donor:
            dataset_db.insert_donor(
                name=name,
                sectors=sectors,
                regions=regions,
                description=description,
                keywords=keywords,
            )
        else:
            dataset_db.insert_ngo(
                name=name,
                sectors=sectors,
                regions=regions,
                description=description,
                keywords=keywords,
            )


def _safe_str(value: Optional[object]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _split_optional(value: Optional[object]) -> list[str] | None:
    """
    Split a comma-separated string into a list of trimmed values.
    """
    text = _safe_str(value)
    if not text:
        return None
    return [part.strip() for part in text.split(",") if part.strip()]

