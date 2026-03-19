from . import dataset_db
from . import accounts_db
from . import excel_import
from . import mock_data
from . import schedule_db

def initialize_all_databases() -> None:
    """
    Convenience helper to initialize both the dataset and accounts databases.
    Can be called from startup code if needed.
    """
    dataset_db.initialize_schema()
    accounts_db.initialize_schema()
    schedule_db.initialize_schema()

__all__ = [
    "dataset_db",
    "accounts_db",
    "schedule_db"
    "excel_import",
    "mock_data",
    "initialize_all_databases",
]

