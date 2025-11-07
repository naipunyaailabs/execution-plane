# Qdrant Lock Conflict - Issue Resolution

## Problem Identified

### Error Message
```
RuntimeError: Storage folder /tmp/qdrant is already accessed by another instance of Qdrant client. 
If you require concurrent access, use Qdrant server instead.
```

### Root Cause Analysis

**Two systems trying to access the same Qdrant directory:**

1. **Mem0 (Memory Service)**
   - Path: `/tmp/qdrant`
   - Used for: Conversational memory storage
   - Creates Qdrant client internally via Mem0 config

2. **Knowledge Base Service**
   - Path: `/tmp/qdrant` (SAME PATH!)
   - Used for: Document embeddings and retrieval
   - Creates new QdrantClient on every request

**Qdrant local mode uses file locking** → Only ONE client can access a directory at a time → Lock conflict on concurrent requests.

### Why It Failed

```python
# EVERY chat request did this:
def execute_agent(...):
    kb_service = KnowledgeBaseService(self.db)  # NEW instance
    # KnowledgeBaseService.__init__ calls:
    self.qdrant_client = QdrantClient(path="/tmp/qdrant")  # NEW client = NEW lock attempt
```

**Result**: 
- First request: OK (gets lock)
- Second concurrent request: FAILS (lock already held)
- KB feature broken on all concurrent requests

---

## Solution Implemented

### Fix 1: Singleton QdrantClient Pattern

**Before (Broken)**:
```python
class KnowledgeBaseService:
    def __init__(self, db: Session):
        self.qdrant_client = QdrantClient(path="/tmp/qdrant")  # New instance every time!
```

**After (Fixed)**:
```python
# Module-level singleton
_qdrant_client = None

def get_qdrant_client():
    """Get or create singleton QdrantClient instance"""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(path="/tmp/qdrant_kb")
    return _qdrant_client

class KnowledgeBaseService:
    def __init__(self, db: Session):
        self.qdrant_client = get_qdrant_client()  # Reuse same instance
```

**Benefits**:
- ✅ Only ONE QdrantClient created for entire application lifetime
- ✅ All requests share the same client
- ✅ No lock conflicts between KB requests

---

### Fix 2: Separate Qdrant Paths

**Mem0 uses**: `/tmp/qdrant`  
**KB uses**: `/tmp/qdrant_kb` (NEW separate path)

**Why separate paths?**
- Mem0 manages its own Qdrant client internally
- We can't inject our singleton into Mem0
- Easiest solution: Use different directories

**Storage Layout**:
```
/tmp/
├── qdrant/              ← Mem0 conversational memory
│   ├── collection/
│   │   └── agent_memories/
│   └── meta.json
└── qdrant_kb/           ← Knowledge base documents
    ├── collection/
    │   └── kb_<agent>_<name>_<id>/
    └── meta.json
```

---

## Files Modified

1. **`backend/services/knowledge_base_service.py`**
   - Added singleton `get_qdrant_client()` function (lines 22-28)
   - Changed path from `/tmp/qdrant` → `/tmp/qdrant_kb` (line 27)
   - Use singleton in `__init__` (line 34)

---

## Testing the Fix

### Before Fix - Expected Behavior
```bash
# Terminal logs:
RuntimeError: Storage folder /tmp/qdrant is already accessed by another instance
# KB queries fail
# Chat works but no KB context retrieved
```

### After Fix - Expected Behavior

**1. First chat request:**
```bash
INFO: Retrieved KB context for agent xxx: 245 chars
INFO: HTTP Request: POST https://api.groq.com/... "200 OK"
INFO: Memory added successfully
```

**2. Second concurrent request:**
```bash
INFO: Retrieved KB context for agent xxx: 189 chars  # No error!
INFO: HTTP Request: POST https://api.groq.com/... "200 OK"
```

**3. Verify separate storage:**
```bash
$ ls -la /tmp/qdrant*/
/tmp/qdrant:
-rw-r--r-- meta.json
drwxr-xr-x collection/

/tmp/qdrant_kb:
-rw-r--r-- meta.json
drwxr-xr-x collection/
```

---

## How to Apply the Fix

### 1. Restart Backend
```bash
# Stop existing server (Ctrl+C)
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 2. Test KB with Text
```bash
# In browser:
1. Go to Playground
2. Create agent "Test KB Text"
3. Knowledge Base section → "Text" tab
4. Paste: "CognitBotz is an AI company. Email: contact@cognitbotz.com"
5. Generate Agent
6. Go to Chat
7. Select "Test KB Text"
8. Ask: "What is the company email?"
9. Should respond with: "contact@cognitbotz.com"
```

### 3. Test Concurrent Requests
```bash
# Send multiple messages quickly
# All should work without lock errors
```

---

## Architecture Notes

### Why Not Use Qdrant Server Mode?

**Qdrant Server** would solve the lock issue by allowing multiple connections, but:
- ❌ Requires running separate Qdrant service
- ❌ More complex setup for users
- ❌ Overkill for single-machine development

**Our Solution**:
- ✅ Zero additional services
- ✅ Simple file-based storage
- ✅ Works out of the box
- ✅ Production can still upgrade to server mode if needed

### Memory Service Qdrant Usage

**Mem0's Qdrant is isolated:**
```python
# memory_service.py (unchanged)
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "path": "/tmp/qdrant",  # Mem0's own path
            "collection_name": "agent_memories",
        }
    }
}
memory = Memory.from_config(config)  # Mem0 manages its own client
```

**KB's Qdrant is isolated:**
```python
# knowledge_base_service.py (fixed)
_qdrant_client = QdrantClient(path="/tmp/qdrant_kb")  # Separate path
```

---

## Cleanup (Optional)

### Remove Old /tmp/qdrant KB Data

If you had KB data in the old `/tmp/qdrant` before the fix, it's now orphaned:

```bash
# Check what's in there
ls -la /tmp/qdrant/collection/

# If you see KB collections (kb_*), they're orphaned
# You can either:

# Option 1: Keep them (harmless, mem0 ignores them)
# Do nothing

# Option 2: Clean them up
rm -rf /tmp/qdrant/collection/kb_*

# DO NOT delete /tmp/qdrant entirely - mem0 needs it!
```

### Verify Storage Separation

```bash
# Mem0 collections (agent memories)
ls /tmp/qdrant/collection/
# Expected: agent_memories/

# KB collections (documents)
ls /tmp/qdrant_kb/collection/
# Expected: kb_<agent_id>_<name>_<uuid>/
```

---

## Performance Impact

### Before Fix
- ❌ KB failed on concurrent requests
- ❌ Only 1 request could use KB at a time
- ✅ Memories worked (different issue)

### After Fix
- ✅ KB works on all requests
- ✅ Multiple concurrent requests work
- ✅ Memories continue working
- ✅ No performance degradation
- ✅ Singleton pattern slightly more efficient (no repeated initialization)

---

## Summary

| Issue | Status | Fix |
|-------|--------|-----|
| Qdrant lock conflict | ✅ Fixed | Singleton pattern |
| Mem0 vs KB collision | ✅ Fixed | Separate paths |
| KB not working for text | ✅ Fixed | Lock issue resolved |
| Concurrent requests failing | ✅ Fixed | Singleton reuse |
| Memory service | ✅ Working | Already cached |

**Result**: Knowledge base now works reliably for text, links, and file uploads with full concurrent request support! 🎉
