"""
Small utility script to quickly check that the database layer works.

Usage (from project root, with venv activated):
    python -m database.test_database
"""

import database
from database import dataset_db, accounts_db, mock_data


def main() -> None:
    print("Initializing databases...")
    database.initialize_all_databases()

    print("Seeding mock donors and NGOs (if empty)...")
    mock_data.seed_mock_data()

    print("\nDonors:")
    for donor in dataset_db.list_donors():
        print(f"- [{donor['id']}] {donor['name']}")

    print("\nNGOs:")
    for ngo in dataset_db.list_ngos():
        print(f"- [{ngo['id']}] {ngo['name']}")

    print("\nCreating a test account (if it does not already exist)...")
    # Very simple check: try to create and then verify.
    accounts_db.initialize_schema()
    accounts_db.create_account("test@higgs.org", "test123", role="tester")

    ok = accounts_db.verify_credentials("test@higgs.org", "test123")
    print(f"Login for test@higgs.org with password 'test123': {'OK' if ok else 'FAILED'}")


if __name__ == "__main__":
    main()

