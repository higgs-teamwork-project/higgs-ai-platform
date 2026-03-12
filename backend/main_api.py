from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import database
import ai_core.api as ai_api

import database.accounts_db as accounts_db

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
    # Endpoint to handle login requests from the frontend
    is_valid = accounts_db.verify_credentials(data.email, data.password)

    print(f"Login attempt for email: {data.email} - {'SUCCESS' if is_valid else 'FAILURE'}")
    
    if is_valid:
        return {"status": "success", "message": "Welcome to HIGGS AI matchmaking platform!"}
    else:
        # FastAPI's standard way to handle errors
        raise HTTPException(status_code=401, detail="Invalid email or password")
    

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

class RegisterData(BaseModel):
    email: str
    password: str

@app.post("/api/register")
async def register_account(data: RegisterData):
    try:
        account_id = accounts_db.create_account(data.email, data.password)
        return {"status": "success", "message": f"Account created with ID {account_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/donors")
async def get_all_donors():
    donors = database.dataset_db.list_donors()
    return [dict(donor) for donor in donors]

@app.get("/api/ngos")
async def get_all_ngos():
    ngos = database.dataset_db.list_ngos()
    return [dict(ngo) for ngo in ngos]
