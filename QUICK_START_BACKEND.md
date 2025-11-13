# 🚀 Quick Start - Backend Setup

## ✅ Backend Implementation Complete!

All backend features for the production workflow builder are now implemented. Follow these steps to get started.

---

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- Dependencies installed (already in requirements.txt)

---

## 🔧 Setup Steps

### 1. Install Dependencies (if needed)
```bash
cd backend
pip install cryptography  # For credential encryption
```

### 2. Set Environment Variables
```bash
# Add to your .env file or export:
export SECRET_KEY="your-secret-key-change-in-production-make-it-long-and-random"
export DATABASE_URL="postgresql://user:password@localhost/dbname"
export ALLOWED_ORIGINS="http://localhost:5173,http://localhost:3000"
```

### 3. Run Database Migration
```bash
cd backend
python migrations/add_credentials.py
```

**Expected Output:**
```
Running credentials migration...
✅ Credentials table created successfully
```

### 4. Start the Backend
```bash
# If not already running:
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Verify APIs
Open your browser to:
```
http://localhost:8000/docs
```

You should see:
- ✅ Credentials API section
- ✅ Webhooks API section
- ✅ Workflows API with executions endpoint

---

## 🧪 Quick Test

### Test 1: Create a Credential
```bash
curl -X POST http://localhost:8000/api/v1/credentials \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test API Key",
    "type": "api_key",
    "data": {
      "api_key": "test-key-12345",
      "api_secret": "test-secret-67890"
    }
  }'
```

**Expected Response:**
```json
{
  "id": "cred-abc123",
  "name": "Test API Key",
  "type": "api_key",
  "data": {
    "api_key": "test****2345",
    "api_secret": "test****7890"
  },
  "createdAt": "2024-11-13T10:00:00Z"
}
```

✅ Notice the sensitive fields are masked!

---

### Test 2: List Credentials
```bash
curl http://localhost:8000/api/v1/credentials
```

**Expected Response:**
```json
[
  {
    "id": "cred-abc123",
    "name": "Test API Key",
    "type": "api_key",
    "data": {
      "api_key": "test****2345",
      "api_secret": "test****7890"
    },
    "createdAt": "2024-11-13T10:00:00Z"
  }
]
```

---

### Test 3: Create a Webhook Trigger
First, create a workflow (or use existing workflow ID):
```bash
# Create workflow
curl -X POST http://localhost:8000/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Workflow",
    "description": "Testing webhooks",
    "definition": {
      "steps": [],
      "dependencies": {}
    }
  }'

# Note the workflow_id from response
```

Then create webhook:
```bash
curl -X POST http://localhost:8000/api/v1/webhooks/{workflow_id}/triggers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Webhook",
    "method": "POST",
    "auth_type": "api_key",
    "auth_config": {
      "api_key": "my-secure-key-123"
    }
  }'
```

**Expected Response:**
```json
{
  "id": "trigger-xyz789",
  "workflow_id": "workflow-abc123",
  "name": "Test Webhook",
  "webhook_url": "/api/v1/webhooks/workflow-abc123/trigger-xyz789",
  "method": "POST",
  "auth_type": "api_key",
  "is_active": true,
  "created_at": "2024-11-13T10:05:00Z"
}
```

---

### Test 4: Trigger Webhook
```bash
curl -X POST http://localhost:8000/api/v1/webhooks/{workflow_id}/{trigger_id} \
  -H "Authorization: Bearer my-secure-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "test": "data",
    "value": 123
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "execution_id": "exec-def456",
  "status": "completed",
  "message": "Workflow execution completed"
}
```

---

## 🔍 Troubleshooting

### Error: "Module 'cryptography' not found"
```bash
pip install cryptography
```

### Error: "Table already exists"
If the migration fails:
```bash
# Drop the table and re-run
python migrations/add_credentials.py
```

Or manually in PostgreSQL:
```sql
DROP TABLE IF EXISTS credentials;
```
Then re-run migration.

### Error: "SECRET_KEY not set"
```bash
export SECRET_KEY="your-secret-key-here"
# Or add to .env file
```

### Error: "Failed to decrypt credential data"
This means the encryption key changed. Either:
1. Use the same SECRET_KEY
2. Delete and recreate credentials

---

## 📊 Database Check

Verify the table was created:
```sql
-- Connect to your database
psql -U your_user -d your_database

-- Check table
\d credentials

-- Expected output:
                                         Table "public.credentials"
    Column     |           Type           | Collation | Nullable |                Default                 
---------------+--------------------------+-----------+----------+---------------------------------------
 id            | integer                  |           | not null | nextval('credentials_id_seq'::regclass)
 credential_id | character varying        |           | not null | 
 name          | character varying        |           | not null | 
 type          | character varying        |           | not null | 
 data          | jsonb                    |           | not null | 
 tenant_id     | character varying        |           |          | 
 created_by    | character varying        |           |          | 
 created_at    | timestamp with time zone |           |          | CURRENT_TIMESTAMP
 updated_at    | timestamp with time zone |           |          | 

-- Check indexes
\di credentials*

-- Expected output:
 idx_credentials_credential_id | index | ... | credentials | (credential_id)
 idx_credentials_name         | index | ... | credentials | (name)
 idx_credentials_tenant_id    | index | ... | credentials | (tenant_id)
```

---

## 🎯 Integration with Frontend

### Frontend Configuration
The frontend is already configured to use these endpoints. Just ensure:

1. **Backend is running** on `http://localhost:8000`
2. **CORS is enabled** (already configured in main.py)
3. **Frontend can reach backend** (check network)

### Test from Frontend
1. Go to http://localhost:5173/production-workflow
2. Click "Credentials" tab
3. Click "Add Credential"
4. Fill in the form
5. Submit
6. You should see the credential appear in the list (with masked fields)

---

## 📝 API Endpoints Available

### Workflows (Existing + Enhanced)
```
✅ POST   /api/v1/workflows                      # Create workflow
✅ GET    /api/v1/workflows                      # List workflows
✅ GET    /api/v1/workflows/{id}                 # Get workflow
✅ PUT    /api/v1/workflows/{id}                 # Update workflow
✅ DELETE /api/v1/workflows/{id}                 # Delete workflow
✅ POST   /api/v1/workflows/{id}/execute         # Execute workflow
✅ GET    /api/v1/workflows/{id}/executions      # Get executions (NEW)
✅ GET    /api/v1/executions/{id}                # Get execution details
```

### Credentials (NEW)
```
✅ POST   /api/v1/credentials                    # Create credential
✅ GET    /api/v1/credentials                    # List credentials
✅ GET    /api/v1/credentials/{id}               # Get credential
✅ PUT    /api/v1/credentials/{id}               # Update credential
✅ DELETE /api/v1/credentials/{id}               # Delete credential
✅ POST   /api/v1/credentials/{id}/test          # Test credential
```

### Webhooks (NEW)
```
✅ POST   /api/v1/webhooks/{wf_id}/{trigger_id} # Trigger workflow
✅ GET    /api/v1/webhooks/{wf_id}/triggers     # List webhooks
✅ POST   /api/v1/webhooks/{wf_id}/triggers     # Create webhook
✅ PUT    /api/v1/webhooks/{wf_id}/triggers/{id}# Update webhook
✅ DELETE /api/v1/webhooks/{wf_id}/triggers/{id}# Delete webhook
```

### Agents (Existing)
```
✅ POST   /api/v1/agents/execute                 # Execute agent
✅ GET    /api/v1/agents/                        # List agents
```

---

## 🔐 Security Notes

### Credential Encryption
- ✅ All credentials are encrypted using Fernet (AES-128)
- ✅ Encryption key derived from SECRET_KEY using PBKDF2
- ✅ Sensitive fields automatically masked in API responses
- ✅ Only decrypted when actually used in workflows

### Production Recommendations
1. **Use a strong SECRET_KEY** (at least 32 characters, random)
2. **Store SECRET_KEY in environment** (not in code)
3. **Use HTTPS in production** (never HTTP)
4. **Enable API rate limiting** (prevent abuse)
5. **Implement proper authentication** (API keys, JWT)
6. **Monitor credential access** (audit logs)
7. **Rotate credentials regularly** (best practice)

---

## ✅ Verification Checklist

After setup, verify:
- [ ] Backend starts without errors
- [ ] Migration ran successfully
- [ ] Credentials table exists in database
- [ ] Can create a credential via API
- [ ] Sensitive fields are masked in response
- [ ] Can list credentials
- [ ] Can create webhook trigger
- [ ] Can trigger webhook
- [ ] Frontend can connect to backend
- [ ] CORS headers present in responses

---

## 🎉 Success!

If all tests pass, your backend is ready to use!

### Next Steps:
1. Open frontend: http://localhost:5173/production-workflow
2. Try creating a workflow
3. Add credentials
4. Add webhook triggers
5. Execute the workflow
6. View execution history

---

## 📞 Need Help?

### Check the Logs
```bash
# Backend logs
tail -f backend/logs/app.log

# Or if using uvicorn:
# Logs will appear in terminal
```

### Check the Docs
```
http://localhost:8000/docs    # OpenAPI/Swagger
http://localhost:8000/redoc   # ReDoc
```

### Common Issues
1. **Port already in use**: Kill process on port 8000
2. **Database connection error**: Check DATABASE_URL
3. **Import errors**: Run `pip install -r requirements.txt`
4. **CORS errors**: Check ALLOWED_ORIGINS setting

---

**🚀 Your backend is now ready for production workflow building!**

All features are implemented, tested, and documented. Happy building!
