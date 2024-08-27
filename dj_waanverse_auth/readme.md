# Waanverse Accounts

## Introduction

Waanverse Accounts is an internal package built and managed by Waanverse Labs Inc. It is designed for REST authentication using JWT (JSON Web Tokens), including features for rotating and refreshing tokens. The package is primarily used for authenticating apps and websites with built-in cookie support.

**Lead Developer:** Tawee (tawee@waanverse.com)

## Required Packages

Waanverse Accounts depends on the following packages:

-   Django
-   Django Rest Framework
-   PyTOP (for MFA)

## Installation

To install Waanverse Accounts, use the following pip command:

```bash
pip install waanverse-accounts
```

## Configuration

### Adding to INSTALLED_APPS

Add 'waanverse_accounts' to your `INSTALLED_APPS` in your Django `settings.py` file:

```python
INSTALLED_APPS = [
    # ...
    'waanverse_accounts',
    # ...
]
```

### Required Settings

In addition to adding Waanverse Accounts to your `INSTALLED_APPS`, you need to configure the following settings in your `settings.py` file:

```python
AUTHENTICATION_BACKENDS = [
    "dj_waanverse_auth.backends.CustomAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "dj_waanverse_auth.backends.JWTAuthentication",
    ),
}
```

These settings ensure that Waanverse Accounts' custom authentication backend and JWT authentication are properly configured for your project.

### Customizing Settings

You can customize the behavior of Waanverse Accounts by adding an `ACCOUNTS_CONFIG` dictionary to your Django `settings.py` file. Here are the default settings:

```python
DEFAULT_ACCOUNTS_CONFIG = {
    "AUTHENTICATION_METHODS": ["username"],
    "MFA_RECOVERY_CODES_COUNT": 2,
    "ACCESS_TOKEN_COOKIE_NAME": "access",
    "REFRESH_TOKEN_COOKIE_NAME": "refresh",
    "COOKIE_PATH": "/",
    "COOKIE_DOMAIN": None,
    "COOKIE_SAMESITE": "Lax",
    "COOKIE_SECURE": False,
    "COOKIE_HTTP_ONLY": True,
    "MFA_COOKIE_NAME": "mfa",
    "MFA_COOKIE_LIFETIME": timedelta(minutes=2),
    "USER_CLAIM_SERIALIZER": "dj_waanverse_auth.serializers.BasicAccountSerializer",
}
```

### SIMPLE JWT Configuration

It's important to include the SIMPLE JWT configuration in your `settings.py`, particularly the lifetime of the access and refresh tokens. These settings affect the cookie lifetimes. For example:

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    # ... other SIMPLE JWT settings ...
}
```

### URL Configuration

To enable the authentication endpoints provided by Waanverse Accounts, you need to include its URLs in your project's `urls.py` file. Add the following to your `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... your other url patterns ...
    path('accounts/', include('dj_waanverse_auth.urls')),
]
```

## Settings Explanation

-   `AUTHENTICATION_METHODS`: An array specifying which authentication methods to use. Each method should correspond to a field in your accounts model. Available options [`username`, `email`, `phone`].
-   `MFA_RECOVERY_CODES_COUNT`: The number of recovery codes generated for Multi-Factor Authentication.
-   `ACCESS_TOKEN_COOKIE_NAME`: The name of the cookie used to store the access token.
-   `REFRESH_TOKEN_COOKIE_NAME`: The name of the cookie used to store the refresh token.
-   `COOKIE_PATH`: The path for which the cookie is valid.
-   `COOKIE_DOMAIN`: The domain for which the cookie is valid.
-   `COOKIE_SAMESITE`: The SameSite attribute for the cookie.
-   `COOKIE_SECURE`: Whether the cookie should only be transmitted over HTTPS.
-   `COOKIE_HTTP_ONLY`: Whether the cookie should be accessible only through HTTP(S) requests.
-   `MFA_COOKIE_NAME`: The name of the cookie used for Multi-Factor Authentication.
-   `MFA_COOKIE_LIFETIME`: The lifetime of the MFA cookie.
-   `USER_CLAIM_SERIALIZER`: The serializer used for user claims in the response after successful login.

## API Endpoints

Here's a detailed breakdown of the available endpoints:

### 1. User Login

-   **URL:** `/accounts/login/`
-   **Method:** POST
-   **Request Body:**
    ```json
    {
        "login_field": "string",
        "password": "string"
    }
    ```
-   **Success Response:**

    -   **Code:** 200
    -   **Content:**
        This endpoint returns an access token and a refresh token and the user details based on the user_claim_serializer. It include Http cookies for the access and refresh tokens as well.

        ```json
        {
            "access_token": "string",
            "refresh_token": "string",
            "user": {
                "id": "integer",
                "username": "string"
            }
        }
        ```

        or
        `mfa` if MFA is activated
        The mfa is a string containing the user id which is also passed through the cookie and has a max life time configured through the settings.

        ```json
        {
            "mfa": "string"
        }
        ```

-   **Error Response:**

    -   **Code:** 401 UNAUTHORIZED or 400 BAD REQUEST
    -   **Content:**

        ```json
        {
            "non_field_errors": ["No active account found with the given credentials"]
        }
        ```

### 2. User Logout

-   **URL:** `/accounts/logout/`
-   **Method:** POST
-   **Headers:** Authorization: Bearer [access_token]
-   **Success Response:**
    -   **Code:** 200
    -   **Content:**
        ```json
        {
            "detail": "Successfully logged out."
        }
        ```
-   **Error Response:**
    -   **Code:** 401 UNAUTHORIZED
    -   **Content:**
        ```json
        {
            "detail": "Authentication credentials were not provided."
        }
        ```

### 3. User Registration

-   **URL:** `/accounts/register/`
-   **Method:** POST
-   **Request Body:**
    ```json
    {
        "username": "string",
        "email": "string",
        "password": "string"
    }
    ```
-   **Success Response:**
    -   **Code:** 201 CREATED
    -   **Content:**
        ```json
        {
            "id": "integer",
            "username": "string",
            "email": "string"
        }
        ```
-   **Error Response:**
    -   **Code:** 400 BAD REQUEST
    -   **Content:**
        ```json
        {
            "username": ["A user with that username already exists."],
            "email": ["user with this email address already exists."]
        }
        ```

### 4. Token Refresh

-   **URL:** `/accounts/refresh/`
-   **Method:** POST
-   **Request Body:**
    ```json
    {
        "refresh": "string"
    }
    ```
-   **Success Response:**
    -   **Code:** 200
    -   **Content:**
        ```json
        {
            "access": "string"
        }
        ```
-   **Error Response:**
    -   **Code:** 401 UNAUTHORIZED
    -   **Content:**
        ```json
        {
            "detail": "Token is invalid or expired",
            "code": "token_not_valid"
        }
        ```

### 5. MFA Setup

-   **URL:** `/accounts/mfa/setup/`
-   **Method:** POST
-   **Headers:** Authorization: Bearer [access_token]
-   **Success Response:**
    -   **Code:** 200
    -   **Content:**
        ```json
        {
            "secret_key": "string",
            "qr_code": "string (base64 encoded image)"
        }
        ```
-   **Error Response:**
    -   **Code:** 400 BAD REQUEST
    -   **Content:**
        ```json
        {
            "detail": "MFA is already set up for this account."
        }
        ```

### 6. MFA Verify

-   **URL:** `/accounts/mfa/verify/`
-   **Method:** POST
-   **Request Body:**
    ```json
    {
        "token": "string"
    }
    ```
-   **Success Response:**
    -   **Code:** 200
    -   **Content:**
        ```json
        {
            "detail": "MFA verification successful."
        }
        ```
-   **Error Response:**
    -   **Code:** 400 BAD REQUEST
    -   **Content:**
        ```json
        {
            "detail": "Invalid MFA token."
        }
        ```

Note: All endpoints return a 500 INTERNAL SERVER ERROR if there's an unexpected server-side issue. The response body for such errors will contain a general error message.

[... rest of the documentation remains the same ...]
