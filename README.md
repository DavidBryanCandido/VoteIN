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
        "email": "john.doe@example.com",
        "photo_url": "/media/profile_pictures/202312345.jpg"
    }
    ```
-   **Notes:**
    -   Only JPEG, PNG, and WebP images are allowed.
    -   Maximum file size: 2MB.
    -   Image is automatically cropped to a 1:1 aspect ratio.

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

# CRUD API Endpoints

All endpoints below require authentication via JWT. Add the header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.dummyaccesstoken
```

## Position

-   **Create Position**

    -   `POST /api/auth/positions/`
    -   **Request Body:**
        ```json
        {
            "position_name": "Secretary",
            "description": "Handles documentation and records",
            "program": "BSCS",
            "rank": 3
        }
        ```
    -   **Response:** `201 Created`
        ```json
        {
            "id": "<id>",
            "position_name": "Secretary",
            "description": "Handles documentation and records",
            "program": "BSCS",
            "rank": 3,
            "created_at": "2024-06-01T12:10:00Z"
        }
        ```

-   **List Positions**

    -   `GET /api/auth/positions/`
    -   **Response:**
        ```json
        [
            {
                "id": "<id>",
                "position_name": "President",
                "description": "Head of the student council",
                "program": "ALL",
                "rank": 1,
                "created_at": "2024-06-01T12:00:00Z"
            },
            {
                "id": "<id>",
                "position_name": "Vice President",
                "description": "Assists the President",
                "program": "BSIT",
                "rank": 2,
                "created_at": "2024-06-01T12:05:00Z"
            }
        ]
        ```

-   **Retrieve Position**

    -   `GET /api/auth/positions/<id>/`
    -   **Response:**
        ```json
        {
            "id": "<id>",
            "position_name": "President",
            "description": "Head of the student council",
            "program": "ALL",
            "rank": 1,
            "created_at": "2024-06-01T12:00:00Z"
        }
        ```

-   **Update Position**

    -   `PUT /api/auth/positions/a1b2c3d4-e5f6-7890-abcd-1234567890ef/`
    -   **Request Body:**
        ```json
        {
            "position_name": "President",
            "description": "Leads the student council and represents students",
            "program": "ALL",
            "rank": 1
        }
        ```
    -   **Response:** `200 OK`
        ```json
        {
            "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ef",
            "position_name": "President",
            "description": "Leads the student council and represents students",
            "program": "ALL",
            "rank": 1,
            "created_at": "2024-06-01T12:00:00Z"
        }
        ```

-   **Delete Position**
    -   `DELETE /api/auth/positions/a1b2c3d4-e5f6-7890-abcd-1234567890ef/`
    -   **Response:** `204 No Content`

---

## PartyList

-   **List PartyLists**

    -   `GET /api/auth/partylists/`
    -   **Response:**
        ```json
        [
            {
                "id": "d4e5f6a1-b2c3-0123-dabc-4567890123ef",
                "election": "e5f6a1b2-c3d4-1234-efab-5678901234cd",
                "party_leader_name": "Jane Smith",
                "party_name": "Unity Party",
                "description": "A party for all students",
                "vision": "Unity and Progress",
                "mission": "Serve the students",
                "created_by": "f6a1b2c3-d4e5-2345-fabc-6789012345de",
                "status": "pending",
                "is_finalized": false
            }
        ]
        ```

-   **Create PartyList**

    -   `POST /api/auth/partylists/`
    -   **Request Body Example:**
        ```json
        {
            "election": "e5f6a1b2-c3d4-1234-efab-5678901234cd",
            "party_leader_name": "Jane Smith",
            "party_name": "Unity Party",
            "description": "A party for all students",
            "vision": "Unity and Progress",
            "mission": "Serve the students",
            "created_by": "f6a1b2c3-d4e5-2345-fabc-6789012345de",
            "status": "pending",
            "is_finalized": false
        }
        ```
    -   **Response:** `201 Created`
        ```json
        {
            "id": "d4e5f6a1-b2c3-0123-dabc-4567890123ef",
            "election": "e5f6a1b2-c3d4-1234-efab-5678901234cd",
            "party_leader_name": "Jane Smith",
            "party_name": "Unity Party",
            "description": "A party for all students",
            "vision": "Unity and Progress",
            "mission": "Serve the students",
            "created_by": "f6a1b2c3-d4e5-2345-fabc-6789012345de",
            "status": "pending",
            "is_finalized": false
        }
        ```

-   **Retrieve PartyList**

    -   `GET /api/auth/partylists/d4e5f6a1-b2c3-0123-dabc-4567890123ef/`
    -   **Response:**
        ```json
        {
            "id": "d4e5f6a1-b2c3-0123-dabc-4567890123ef",
            "election": "e5f6a1b2-c3d4-1234-efab-5678901234cd",
            "party_leader_name": "Jane Smith",
            "party_name": "Unity Party",
            "description": "A party for all students",
            "vision": "Unity and Progress",
            "mission": "Serve the students",
            "created_by": "f6a1b2c3-d4e5-2345-fabc-6789012345de",
            "status": "pending",
            "is_finalized": false
        }
        ```

-   **Update PartyList**

    -   `PUT /api/auth/partylists/d4e5f6a1-b2c3-0123-dabc-4567890123ef/`
    -   **Request Body:**
        ```json
        {
            "election": "e5f6a1b2-c3d4-1234-efab-5678901234cd",
            "party_leader_name": "Jane Smith",
            "party_name": "Unity Party",
            "description": "A party for all students and faculty",
            "vision": "Unity, Progress, and Service",
            "mission": "Serve the students and faculty",
            "created_by": "f6a1b2c3-d4e5-2345-fabc-6789012345de",
            "status": "approved",
            "is_finalized": true
        }
        ```
    -   **Response:** `200 OK`
        ```json
        {
            "id": "d4e5f6a1-b2c3-0123-dabc-4567890123ef",
            "election": "e5f6a1b2-c3d4-1234-efab-5678901234cd",
            "party_leader_name": "Jane Smith",
            "party_name": "Unity Party",
            "description": "A party for all students and faculty",
            "vision": "Unity, Progress, and Service",
            "mission": "Serve the students and faculty",
            "created_by": "f6a1b2c3-d4e5-2345-fabc-6789012345de",
            "status": "approved",
            "is_finalized": true
        }
        ```

-   **Delete PartyList**
    -   `DELETE /api/auth/partylists/d4e5f6a1-b2c3-0123-dabc-4567890123ef/`
    -   **Response:** `204 No Content`

---

## Election

-   **List Elections**

    -   `GET /api/auth/elections/`
    -   **Response:**
        ```json
        [
            {
                "id": "e5f6a1b2-c3d4-1234-efab-5678901234cd",
                "title": "2024 Student Council Election",
                "description": "Annual election for student council",
                "start_date": "2024-06-01T09:00:00Z",
                "end_date": "2024-06-01T17:00:00Z",
                "status": "scheduled",
                "created_by": "f6a1b2c3-d4e5-2345-fabc-6789012345de",
                "created_at": "2024-05-20T10:00:00Z"
            }
        ]
        ```

-   **Create Election**

    -   `POST /api/auth/elections/`
    -   **Request Body Example:**
        ```json
        {
            "title": "2024 Student Council Election",
            "description": "Annual election for student council",
            "start_date": "2024-06-01T09:00:00Z",
            "end_date": "2024-06-01T17:00:00Z",
            "status": "scheduled",
            "created_by": "f6a1b2c3-d4e5-2345-fabc-6789012345de"
        }
        ```
    -   **Response:** `201 Created`
        ```json
        {
            "id": "e5f6a1b2-c3d4-1234-efab-5678901234cd",
            "title": "2024 Student Council Election",
            "description": "Annual election for student council",
            "start_date": "2024-06-01T09:00:00Z",
            "end_date": "2024-06-01T17:00:00Z",
            "status": "scheduled",
            "created_by": "f6a1b2c3-d4e5-2345-fabc-6789012345de",
            "created_at": "2024-05-20T10:00:00Z"
        }
        ```

-   **Retrieve Election**

    -   `GET /api/auth/elections/e5f6a1b2-c3d4-1234-efab-5678901234cd/`
    -   **Response:**
        ```json
        {
            "id": "e5f6a1b2-c3d4-1234-efab-5678901234cd",
            "title": "2024 Student Council Election",
            "description": "Annual election for student council",
            "start_date": "2024-06-01T09:00:00Z",
            "end_date": "2024-06-01T17:00:00Z",
            "status": "scheduled",
            "created_by": "f6a1b2c3-d4e5-2345-fabc-6789012345de",
            "created_at": "2024-05-20T10:00:00Z"
        }
        ```

-   **Update Election**

    -   `PUT /api/auth/elections/e5f6a1b2-c3d4-1234-efab-5678901234cd/`
    -   **Request Body:**
        ```json
        {
            "title": "2024 Student Council Election",
            "description": "Annual election for student council (updated)",
            "start_date": "2024-06-01T09:00:00Z",
            "end_date": "2024-06-01T17:00:00Z",
            "status": "ongoing",
            "created_by": "f6a1b2c3-d4e5-2345-fabc-6789012345de"
        }
        ```
    -   **Response:** `200 OK`
        ```json
        {
            "id": "e5f6a1b2-c3d4-1234-efab-5678901234cd",
            "title": "2024 Student Council Election",
            "description": "Annual election for student council (updated)",
            "start_date": "2024-06-01T09:00:00Z",
            "end_date": "2024-06-01T17:00:00Z",
            "status": "ongoing",
            "created_by": "f6a1b2c3-d4e5-2345-fabc-6789012345de",
            "created_at": "2024-05-20T10:00:00Z"
        }
        ```

-   **Delete Election**
    -   `DELETE /api/auth/elections/e5f6a1b2-c3d4-1234-efab-5678901234cd/`
    -   **Response:** `204 No Content`

---

## Error Handling

-   Invalid credentials: `401 Unauthorized`
-   Unauthorized access: `401 Unauthorized`
-   Not found: `404 Not Found`
-   Validation error: `400 Bad Request`

---

## Notes

-   Use your `student_id` as the username when logging in.
-   All passwords are securely hashed.
-   JWT tokens are used for authentication.

## Setup Instructions

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

## Authentication

This API uses JWT for authentication. A valid token must be included in the `Authorization` header for protected routes. Example:

```
Authorization: Bearer <your_jwt_token_here>
```

# Rate Limiting

Some endpoints (e.g., registration, login) are rate-limited.

-   **Limit:** 3 requests per 60 seconds per IP/user.
-   **Error Response:**
    -   Status: 429 Too Many Requests
    -   Body:
        ```json
        {
            "detail": "Rate limit exceeded. Max 3 requests per 60 seconds."
        }
        ```

# File Upload Documentation

## Profile Picture Upload

The API supports profile picture uploads during user registration. The following features are implemented:

### Supported File Types

-   JPEG (.jpg, .jpeg)
-   PNG (.png)
-   WebP (.webp)

### File Size Limits

-   Maximum file size: 2MB
-   Files exceeding this limit will be rejected with a validation error

### Image Processing

-   Images are automatically cropped to a 1:1 aspect ratio
-   The crop is centered on the image
-   Original image quality is preserved

### Storage

-   Files are stored in the `profile_pictures` directory
-   File naming convention: `{student_id}.{extension}`
-   Files are served through Django's media URL configuration

### Error Handling

The API will return appropriate error messages for:

-   Invalid file types
-   Files exceeding size limit
-   Corrupted or invalid image files

### Example Usage

```python
# Using Python requests
import requests

url = 'http://127.0.0.1:8000/api/auth/register/'
files = {
    'photo_url': ('profile.jpg', open('profile.jpg', 'rb'), 'image/jpeg')
}
data = {
    'student_id': '202312345',
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john.doe@example.com',
    'password': 'yourpassword',
    'confirm_password': 'yourpassword'
}

response = requests.post(url, files=files, data=data)
```

### Response Example

```json
{
    "student_id": "202312345",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "photo_url": "/media/profile_pictures/202312345.jpg"
}
```

### Configuration

To enable file uploads, ensure the following settings are in your Django settings:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'profile_pictures')
```

And in your URLs configuration:

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your URL patterns ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
