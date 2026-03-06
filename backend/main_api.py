from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

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
    # Dont print password
    print("--------------------------------------------------")
    
    # Check if the credentials match a dummy user
    if data.email == "admin@higgs.org" and data.password == "password123":
        return {"status": "success", "message": "Welcome to HIGGS!"}
    else:
        return {"status": "error", "message": "Invalid email or password"}