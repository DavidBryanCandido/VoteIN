# VoteIN Authentication API

## Endpoints

### 1. Register a New User

-   **POST** `/api/auth/register/`
-   **Request Body:**
    ```json
    {
        "student_id": "202312345",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "password": "yourpassword",
        "confirm_password": "yourpassword"
    }
    ```
-   **Response:**
    -   `201 Created`
    ```json
    {
        "student_id": "202312345",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com"
    }
    ```

---

### 2. Login (Obtain JWT Token)

-   **POST** `/api/auth/login/`
-   **Request Body:**
    ```json
    {
        "username": "202312345", // Use student_id as username
        "password": "yourpassword"
    }
    ```
-   **Response:**
    -   `200 OK`
    ```json
    {
        "refresh": "<refresh_token>",
        "access": "<access_token>"
    }
    ```

---

### 3. Refresh Token

-   **POST** `/api/auth/token/refresh/`
-   **Request Body:**
    ```json
    {
        "refresh": "<refresh_token>"
    }
    ```
-   **Response:**
    ```json
    {
        "access": "<new_access_token>"
    }
    ```

---

### 4. Protected Route

-   **GET** `/api/auth/protected/`
-   **Headers:**
    -   `Authorization: Bearer <access_token>`
-   **Response:**
    ```json
    {
        "message": "Hello, John! This is a protected route."
    }
    ```

---

## Error Handling

-   Invalid credentials: `401 Unauthorized`
-   Unauthorized access: `401 Unauthorized`

---

## Notes

-   Use your `student_id` as the username when logging in.
-   All passwords are securely hashed.
-   JWT tokens are used for authentication.

Setup Instructions
------------------

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/DavidBryanCandido/VoteIN.git
   cd VoteIN
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Run the Server:**
   ```bash
   python manage.py runserver
   ```

5. **Test Endpoints:**
   - Use Postman, or any REST client to test the endpoints.
   - Start with the `/api/auth/register/` endpoint.

---

Authentication
--------------
This API uses JWT for authentication. A valid token must be included in the `Authorization` header for protected routes. Example:

```
Authorization: Bearer <your_jwt_token_here>
```

