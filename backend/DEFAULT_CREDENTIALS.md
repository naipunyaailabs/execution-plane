# Default Login Credentials

## Overview
Default user accounts have been created for the Execution Plane application.

## Accounts

### Admin User (Full Access)
- **Email:** `admin@execution-plane.com`
- **Username:** `admin`
- **Password:** `admin12`
- **Role:** System Administrator (Superuser)
- **Permissions:** Full access to all features

### Regular User
- **Email:** `user@execution-plane.com`
- **Username:** `user`
- **Password:** `user12`
- **Role:** Regular User
- **Permissions:** Standard user access

## Login Instructions

### Via API
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@execution-plane.com", "password": "admin12"}'
```

### Via Swagger UI
1. Navigate to `http://localhost:8000/docs`
2. Click "Authorize" button
3. Use the `/api/v1/auth/login` endpoint
4. Enter email and password
5. Copy the `access_token` from the response
6. Click "Authorize" and paste the token with `Bearer ` prefix

### Response Format
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "user_id": "admin-user-id",
    "email": "admin@execution-plane.com",
    "username": "admin",
    "full_name": "System Administrator",
    "is_active": true,
    "is_superuser": true,
    "tenant_id": null,
    "roles": [],
    "created_at": "2025-11-13T07:39:09"
  },
  "session_token": "..."
}
```

## Security Notes

⚠️ **IMPORTANT SECURITY WARNINGS:**

1. **Change Default Passwords Immediately** after first login
2. **Never use these credentials in production** without changing them
3. Use strong, unique passwords (minimum 12 characters)
4. Enable two-factor authentication when available
5. Regularly rotate passwords
6. Monitor login attempts and sessions

## Password Requirements
- Minimum length: 6 characters (for compatibility)
- Maximum length: 72 bytes (bcrypt limitation)
- Recommended: Use strong passwords with mixed characters

## Troubleshooting

### Login Failed Error
If you receive "Login failed" error:
1. Verify the email and password are correct
2. Check that the backend server is running on port 8000
3. Ensure the request format is correct (email and password in JSON body)
4. Check browser console for detailed error messages

### Backend Issues
If the backend is not responding:
1. Check if the server is running: `lsof -ti:8000`
2. Restart the server: `venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000`
3. Check server logs for errors

## Recreating Users

If you need to recreate the default users:
```bash
cd /Users/apple/Desktop/execution-plane/backend
venv/bin/python simple_create_users.py
```

## Technical Details

### Password Hashing
- Uses **Argon2** algorithm (primary)
- Fallback to **bcrypt** for compatibility
- Configured in `services/auth_service.py`

### Authentication Flow
1. User submits email and password
2. Backend verifies credentials using Argon2/bcrypt
3. JWT access token generated (24-hour expiration)
4. Session token created for tracking
5. Tokens returned to client

### Database
- SQLite database: `agents.db`
- Users table contains hashed passwords
- Sessions tracked in `user_sessions` table
