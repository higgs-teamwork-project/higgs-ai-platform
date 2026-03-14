"""
Run the AI matching pipeline on your imported donors and NGOs.

- Builds embeddings for all donors and NGOs that don't have one yet (first run can take a few minutes).
- Shows top NGO recommendations for the first few donors so you can see the AI work.

From project root (venv active):
  python scripts/run_ai_demo.py

Requires: sentence-transformers, and the model at ai_core/model/all-MiniLM-L6-v2.pt
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import database
import database.dataset_db as dataset_db
import ai_core.api as ai_api


def main():
    print("1. Initializing database (using your imported data, no mock)...")
    database.initialize_all_databases()

    donors = dataset_db.list_donors()
    ngos = dataset_db.list_ngos()
    if not donors:
        print("No donors in the database. Run scripts/import_donors_book1.py first.")
        sys.exit(1)
    if not ngos:
        print("No NGOs in the database. Run scripts/import_ngos_book2.py first.")
        sys.exit(1)

    print(f"   Donors: {len(donors)}, NGOs: {len(ngos)}")

    print("\n2. Building embeddings for donors and NGOs (first run may take 1–2 min)...")
    ai_api.ensure_embeddings()
    print("   Done.")

    # Show recommendations for first 3 donors
    show_donors = donors[:3]
    top_k = 5

    print(f"\n3. Top-{top_k} NGO recommendations per donor (semantic similarity)\n")
    print("-" * 70)

    for donor in show_donors:
        donor_id = donor["id"]
        donor_name = donor["name"]
        strategy = (donor["strategy"] or "")[:80]
        if len(donor["strategy"] or "") > 80:
            strategy += "..."

        results = ai_api.get_recommendations_for_donor(
            donor_id, top_k=top_k, save_matches=False
        )

        print(f"\nDonor: {donor_name} (id={donor_id})")
        print(f"  Strategy: {strategy or '-'}")
        print("  Top NGO matches:")
        for i, r in enumerate(results, 1):
            ngo = r["ngo"]
            score = r["score"]
            name = ngo.get("name", "?")
            focus = (ngo.get("focus") or ngo.get("strategy") or "")[:50]
            if len(ngo.get("focus") or ngo.get("strategy") or "") > 50:
                focus += "..."
            print(f"    {i}. {name}  (score: {score:.3f})")
            print(f"       Focus: {focus or '-'}")
        print("-" * 70)

    print("\nDone. You can also:")
    print("  - Start the backend and call GET /api/donors/<id>/recommendations?top_k=10")
    print("  - Use save_matches=true to store scores in the DB.")


if __name__ == "__main__":
    main()
