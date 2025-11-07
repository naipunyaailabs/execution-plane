# Chat with Knowledge Base - Issue Resolution

## Issues Identified

### 1. **Frontend Bug: Empty Messages Sent to Backend**
**Problem**: The chat input was cleared before the API call, causing empty messages to be sent.

**Location**: `frontend/src/components/AgentChat.tsx` line 212

**Root Cause**:
```typescript
setInput("");  // Cleared here at line 195
// ...
body: JSON.stringify({ 
  message: input,  // Empty string sent!
  thread_id: threadId
})
```

**Fix**: Capture the message before clearing:
```typescript
const messageToSend = input;  // Capture before clearing
setInput("");
// ...
body: JSON.stringify({ 
  message: messageToSend,  // Send actual message
  thread_id: threadId
})
```

---

### 2. **Backend: No Timeout on Knowledge Base Queries**
**Problem**: KB queries could hang indefinitely if Qdrant or embeddings were slow.

**Location**: `backend/services/agent_service.py` lines 187-194

**Root Cause**: No timeout protection on async KB query operations.

**Fix**: Added 10-second timeout with `asyncio.wait_for`:
```python
knowledge_context = await asyncio.wait_for(
    kb_service.query_agent_knowledge(agent_id, input_text, top_k=5),
    timeout=10.0  # 10 second timeout
)
```

---

### 3. **Backend: No Timeout on LLM Provider Calls**
**Problem**: LLM API calls (OpenAI, Anthropic, Groq) could hang if the provider was slow or unreachable.

**Location**: `backend/services/agent_service.py` lines 215-231

**Root Cause**: LangGraph's `invoke()` is synchronous and blocking without timeout.

**Fix**: Added 60-second timeout with `asyncio.to_thread`:
```python
response = await asyncio.wait_for(
    asyncio.to_thread(langgraph_agent.invoke, {"messages": messages}),
    timeout=60.0  # 60 second timeout for LLM calls
)
```

**Error Handling**:
```python
except asyncio.TimeoutError:
    raise ValueError("Agent response timed out. The LLM provider may be slow or unreachable.")
```

---

### 4. **Frontend: Generic Error Messages**
**Problem**: All errors showed "Make sure backend is running" regardless of actual cause.

**Location**: `frontend/src/components/AgentChat.tsx` lines 228-240

**Fix**: 
- Parse backend error details from response
- Display actual error messages to users
- Better error context for debugging

```typescript
const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
throw new Error(errorData.detail || 'Failed to get response');
```

---

### 5. **Missing Error Logging**
**Problem**: KB errors weren't logged with stack traces, making debugging difficult.

**Fix**: Added detailed error logging:
```python
except Exception as kb_error:
    print(f"Error retrieving knowledge base context: {kb_error}")
    import traceback
    traceback.print_exc()
```

---

## Files Modified

### Backend
1. **`backend/services/agent_service.py`**
   - Added 10s timeout to KB queries (line 194-197)
   - Added 60s timeout to LLM calls (line 232-235, 248-251)
   - Added timeout error handling (line 252-253)
   - Added detailed error logging (line 203-205)
   - Added KB context logging (line 198-199)

### Frontend
2. **`frontend/src/components/AgentChat.tsx`**
   - Fixed empty message bug (line 195)
   - Added backend error parsing (line 229-230)
   - Show actual error messages (line 235)

---

## How It Works Now

### Chat Flow with Knowledge Base

1. **User sends message** → Frontend captures message before clearing input
2. **Backend receives message** → Validates agent exists
3. **Retrieve memory context** (if mem0 enabled) → No changes
4. **Retrieve KB context** → **NEW: 10s timeout**
   - Query embeddings via Ollama
   - Search Qdrant vector DB
   - Return top 5 relevant chunks
5. **Build system prompt** → Inject KB context + memory
6. **Call LLM** → **NEW: 60s timeout**
   - Send to OpenAI/Anthropic/Groq
   - Wait for response
   - Handle timeouts gracefully
7. **Return response** → Frontend displays message
8. **Store interaction** → Save to mem0 for future context

### Timeout Behavior

**Knowledge Base Query (10s)**:
- If KB query takes >10s → Log warning, continue without KB context
- Agent still works, just without document grounding

**LLM Call (60s)**:
- If LLM takes >60s → Raise clear error to user
- User sees: "Agent response timed out. The LLM provider may be slow or unreachable."

---

## Testing Instructions

### 1. Test File Upload KB
```bash
# Start backend (in backend/)
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# In browser (http://localhost:5173)
1. Go to Playground
2. Create agent with name "Test KB Agent"
3. Click "Upload" tab in Knowledge Base section
4. Select a PDF/DOCX file
5. Click "Generate Agent"
6. Wait for KB processing
```

### 2. Test Chat with KB
```bash
# After creating agent with KB:
1. Go to Chat page
2. Select "Test KB Agent"
3. Ask: "What is in the document I uploaded?"
4. Should receive answer grounded in document content
```

### 3. Test Timeout Handling
```bash
# Simulate slow LLM:
1. Create agent with invalid/slow API key
2. Try to chat
3. Should see timeout error after 60s, not hang forever
```

### 4. Test Error Messages
```bash
# Test various error scenarios:
1. Wrong API key → "Invalid API key"
2. Rate limit → "Rate limit exceeded"
3. Network timeout → "Agent response timed out"
4. KB not found → Clear error message
```

---

## Common Issues & Solutions

### Issue: "Agent response timed out"
**Causes**:
- LLM provider API is down
- Network connectivity issues
- API key invalid/expired
- Provider rate limiting

**Solutions**:
1. Check API key in agent settings
2. Verify network connectivity
3. Try different LLM provider
4. Wait and retry (rate limit)

---

### Issue: KB returns no results
**Causes**:
- Documents not fully processed
- Embedding model not available (qwen3-embedding:0.6b)
- Query doesn't match document content

**Solutions**:
1. Check document processing status in logs
2. Verify Ollama is running: `ollama list`
3. Pull embedding model: `ollama pull qwen3-embedding:0.6b`
4. Check Qdrant storage: `ls -la /tmp/qdrant_kb` (KB) and `ls -la /tmp/qdrant` (Mem0)

---

### Issue: "Failed to send message"
**Causes**:
- Backend not running
- Port conflict (8001 already in use)
- Database connection issue

**Solutions**:
1. Start backend: `uvicorn main:app --reload --host 0.0.0.0 --port 8001`
2. Check backend logs for errors
3. Verify SQLite DB exists: `ls backend/agents.db`

---

## Performance Optimizations

### Current Timeouts
- **KB Query**: 10 seconds
- **LLM Call**: 60 seconds
- **Total Request**: ~70 seconds max

### Recommended for Production
- **KB Query**: 5 seconds (faster feedback)
- **LLM Call**: 30 seconds (most APIs respond in <10s)
- **Add retry logic**: 2-3 retries with exponential backoff
- **Connection pooling**: Reuse HTTP connections
- **Caching**: Cache frequent KB queries

---

## Monitoring & Debugging

### Backend Logs to Watch
```bash
# KB context retrieved
"Retrieved KB context for agent {agent_id}: {chars} chars"

# KB timeout
"Knowledge base query timed out for agent {agent_id}"

# KB error with stack trace
"Error retrieving knowledge base context: {error}"
```

### Frontend Network Tab
```bash
# Check request payload
POST /api/v1/agents/{id}/chat/
{
  "message": "actual message content",  # Should NOT be empty
  "thread_id": "thread_123..."
}

# Check response
{
  "response": "Agent's answer..."
}
```

---

## Summary

✅ **Fixed**: Empty messages sent to backend  
✅ **Fixed**: Indefinite hangs on KB queries  
✅ **Fixed**: Indefinite hangs on LLM calls  
✅ **Fixed**: Generic error messages  
✅ **Added**: Detailed error logging  
✅ **Added**: Timeout protection (10s KB, 60s LLM)  
✅ **Added**: Better user feedback  

**Result**: Chat with knowledge base now works reliably with proper timeout handling and clear error messages when issues occur.
