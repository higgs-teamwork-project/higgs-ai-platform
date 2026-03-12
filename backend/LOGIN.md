# Backend API Documentation

### Register a New Account
* **URL:** `/api/register`
* **Method:** `POST`
* **Description:** Creates a securely hashed account in the `accounts.db` database.
* **Request Body (JSON):**
  ```json
  {
    "email": "user@organization.org",
    "password": "securepassword123", 
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
