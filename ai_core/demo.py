"""
Demo: run the full AI matching pipeline and print results.

From project root (with venv active):
  python -m ai_core.demo
"""

import database
import ai_core.api as ai_api


def main() -> None:


    print("1. Initializing database (using current data, no mock)...")
    database.initialize_all_databases()

    print("2. Building embeddings for donors and NGOs (this may take a moment)...")
    ai_api.ensure_embeddings()

    donors = database.dataset_db.list_donors()
    if not donors:
        print("No donors in the database. Add data and run again.")
        return

    print("\n3. Recommendation results\n")
    print("-" * 60)

    for donor in donors:
        donor_id = donor["id"]
        donor_name = donor["name"]
        results = ai_api.get_recommendations_for_donor(donor_id, top_k=3, save_matches=False)

        print(f"\nDonor: {donor_name} (id={donor_id})")
        print("Top NGO matches:")
        for i, r in enumerate(results, 1):
            ngo = r["ngo"]
            score = r["score"]
            name = ngo.get("name", "?")
            sectors = ngo.get("sectors") or "-"
            print(f"  {i}. {name}  (score: {score:.3f})")
            print(f"     Sectors: {sectors}")
        print("-" * 60)

    print("\nDone. Use the API at GET /api/donors/<id>/recommendations for more.")


if __name__ == "__main__":
    main()
