Here is the complete, ready-to-copy Markdown file. You can paste this directly into a new file named `DOCUMENTATION.md` inside your `backend` folder.

```markdown
# Backend API Documentation

This document outlines the core FastAPI application (`main_api.py`) that serves as the central controller for the HIGGS AI Platform. It acts as the bridge connecting the PySide6 frontend UI to the local SQLite databases and the AI matchmaking engine.

## Overview

The backend is built using **FastAPI** and uses **Pydantic** to enforce strict data validation. It handles user authentication, data retrieval (Donors/NGOs), and triggers the AI recommendations.

---

## 🚀 Startup Behavior

When the FastAPI server boots up (via `uvicorn`), it triggers an `@app.on_event("startup")` lifecycle hook:

1. **Database Initialization:** It calls `database.initialize_all_databases()` to ensure the `accounts.db` and `dataset.db` SQLite files and their respective tables exist.
2. **Mock Data Seeding:** It calls `database.mock_data.seed_mock_data()` to populate the databases with a small set of dummy users, donors, and NGOs so the frontend has immediate data to test with.

---

## Authentication Endpoints

### 1. Register a New Account
* **URL:** `/api/register`
* **Method:** `POST`
* **Description:** Creates a securely hashed account in the `accounts.db` database.
* **Request Body (JSON):**
  ```json
  {
    "email": "user@organization.org",
    "password": "securepassword123",
    "role": "donor" 
  }

```

* **Success Response (200 OK):** 
```json
{
"status": "success",
"message": "Account created with ID <id>"
}
```

* **Error Response (400 Bad Request):** Triggered if the email already exists or another database error occurs.

### User Login

* **URL:** `/api/login`
* **Method:** `POST`
* **Description:** Verifies an email and password against the securely hashed credentials in `accounts.db`.
* **Request Body (JSON):**
```json
{
  "email": "user@organization.org",
  "password": "securepassword123"
}

```


* **Success Response (200 OK):** 
```json
{
"status": "success",
"message": "Welcome to HIGGS AI matchmaking platform!"
}
```



* **Error Response (401 Unauthorized):** 
```json
{
"detail": "Invalid email or password"
}
```

---

## Data Retrieval Endpoints

### Get All Donors

* **URL:** `/api/donors`
* **Method:** `GET`
* **Description:** Fetches the complete list of all registered donors from the `dataset.db` database.
* **Success Response (200 OK):** Returns a JSON array of donor objects (dictionaries containing fields like `name`, `sectors`, `regions`, `description`, etc.).

### Get All NGOs

* **URL:** `/api/ngos`
* **Method:** `GET`
* **Description:** Fetches the complete list of all registered NGOs from the `dataset.db` database.
* **Success Response (200 OK):** Returns a JSON array of NGO objects (dictionaries containing fields like `name`, `sectors`, `regions`, `description`, etc.).

---

## AI Matchmaking Endpoints

### Get Recommendations for Donor

* **URL:** `/api/donors/{donor_id}/recommendations`
* **Method:** `GET`
* **Description:** Triggers the AI core to calculate semantic similarity between a specific donor and all available NGOs, returning the best matches.
* **Query Parameters:**
* `top_k` (integer, optional): Maximum number of recommendations to return. Default is `10`.
* `save_matches` (boolean, optional): If `true`, saves the resulting match scores into the `donor_ngo_matches` database table. Default is `false`.


* **Success Response (200 OK):** 
```json
{
"donor_id": 1,
"recommendations": [
{
"ngo_id": 5,
"ngo": {"name": "Example NGO", "sectors": "Education", "...": "..."},
"score": 0.95
},
{
"ngo_id": 2,
"ngo": {"name": "Another NGO", "sectors": "Health", "...": "..."},
"score": 0.88
}
]
}
```



* **Error Response (404 Not Found):** Triggered if the `donor_id` does not exist in the database.