from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import database
import ai_core.api as ai_api

app = FastAPI()


@app.on_event("startup")
async def on_startup() -> None:
    # Ensure the SQLite databases exist before handling any requests
    database.initialize_all_databases()
    # Seed a small amount of mock data to make the system usable before real imports
    database.mock_data.seed_mock_data()

# 1. Define the blueprint for the incoming data
class LoginData(BaseModel):
    email: str
    password: str

# 2. Create the POST endpoint to receive the data
@app.post("/api/login")
async def process_login(data: LoginData):
    # This is where your backend officially reads the frontend data!
    print("--------------------------------------------------")
    print(f"BACKEND RECEIVED LOGIN ATTEMPT:")
    print(f"Email: {data.email}")
    print(f"Password: {data.password}") # In reality, never print passwords!
    print("--------------------------------------------------")
    
    # Check if the credentials match a dummy user
    if data.email == "admin@higgs.org" and data.password == "password123":
        return {"status": "success", "message": "Welcome to HIGGS!"}
    else:
        return {"status": "error", "message": "Invalid email or password"}


@app.get("/api/donors/{donor_id}/recommendations")
async def get_donor_recommendations(
    donor_id: int,
    top_k: int = 10,
    save_matches: bool = False,
):
    """
    Return top NGO recommendations for a donor by semantic similarity.
    top_k: max number of results (default 10).
    save_matches: if true, store scores in donor_ngo_matches table.
    """
    if database.dataset_db.get_donor(donor_id) is None:
        raise HTTPException(status_code=404, detail="Donor not found")
    results = ai_api.get_recommendations_for_donor(
        donor_id=donor_id,
        top_k=top_k,
        save_matches=save_matches,
    )
    return {"donor_id": donor_id, "recommendations": results}