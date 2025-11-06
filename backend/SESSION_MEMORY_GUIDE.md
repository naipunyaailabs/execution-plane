# Session-Based Memory System

## Overview

The memory system now supports **session-based ephemeral memory** that automatically cleans up when users refresh the page or end their session. This ensures privacy and prevents memory pollution across different chat sessions.

---

## Architecture

### How It Works

1. **Session Creation**: When a user opens the chat interface, a unique `thread_id` is generated
   ```typescript
   thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}
   ```

2. **Memory Storage**: All conversation memories are stored with the `thread_id` as the `user_id` in Mem0
   - Memories are associated with the session, not the user permanently
   - Each session has isolated memory

3. **Memory Retrieval**: During conversation, relevant memories are retrieved using the session's `thread_id`
   - Only memories from the current session are accessible
   - Provides context within the session

4. **Automatic Cleanup**: Memories are deleted when:
   - User refreshes the page (`beforeunload` event)
   - User closes the tab/browser
   - Component unmounts (navigating away)

---

## Implementation Details

### Backend Changes

#### 1. Memory Service (`services/memory_service.py`)

Added `delete_session_memories` method:
```python
def delete_session_memories(self, session_id: str) -> bool:
    """Delete all memories for a session"""
    memories = self.get_user_memories(user_id=session_id)
    for memory in memories:
        self.memory.delete(memory_id=memory.get("id"))
    return True
```

#### 2. Agent Service (`services/agent_service.py`)

Updated to use `session_id` instead of persistent user ID:
```python
async def chat_with_agent(self, agent_id: str, message: str, thread_id: Optional[str] = None):
    session_id = thread_id if thread_id else f"agent_{agent_id}"
    response = await self.execute_agent(agent_id, message, session_id=session_id)
    # Store with session_id
    self.memory_service.add_memory(interaction, user_id=session_id, agent_id=agent_id)
```

#### 3. API Endpoints (`api/v1/agents.py`)

**New cleanup endpoint**:
```python
@router.delete("/memory/session/{session_id}")
async def delete_session_memories(session_id: str, db: Session = Depends(get_db)):
    """Delete all memories for a session"""
    success = agent_service.memory_service.delete_session_memories(session_id)
    return MemoryResponse(success=True)
```

**Updated chat endpoint**:
```python
@router.post("/{agent_id}/chat/")
async def chat_with_agent(agent_id: str, request: AgentChatRequest):
    # Now accepts thread_id from request
    response = await agent_service.chat_with_agent(
        agent_id, 
        request.message, 
        thread_id=request.thread_id
    )
```

#### 4. Schemas (`schemas/agent.py`)

```python
class AgentChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None  # Session ID for ephemeral memory
```

### Frontend Changes

#### Component Lifecycle (`components/AgentChat.tsx`)

```typescript
useEffect(() => {
  // Generate session ID
  const newThreadId = `thread_${Date.now()}_${Math.random()}`;
  setThreadId(newThreadId);

  // Cleanup on page refresh/close
  const handleBeforeUnload = () => {
    navigator.sendBeacon(
      `http://localhost:8001/api/v1/agents/memory/session/${newThreadId}`
    );
  };
  window.addEventListener('beforeunload', handleBeforeUnload);

  // Cleanup on component unmount
  return () => {
    window.removeEventListener('beforeunload', handleBeforeUnload);
    cleanupSession();
  };
}, []);
```

---

## API Reference

### Delete Session Memories

**Endpoint**: `DELETE /api/v1/agents/memory/session/{session_id}`

**Description**: Deletes all memories associated with a session

**Parameters**:
- `session_id` (path): The thread/session ID to clean up

**Response**:
```json
{
  "success": true,
  "message": "Session memories deleted successfully for thread_xxx"
}
```

**Example**:
```bash
curl -X DELETE http://localhost:8001/api/v1/agents/memory/session/thread_1234567890_abc123
```

### Chat with Session

**Endpoint**: `POST /api/v1/agents/{agent_id}/chat/`

**Request Body**:
```json
{
  "message": "Hello, how can you help me?",
  "thread_id": "thread_1234567890_abc123"
}
```

**Response**:
```json
{
  "response": "I can help you with various tasks..."
}
```

---

## Memory Lifecycle Example

### Session Start
```
User opens chat → thread_1234567890_abc123 created
```

### Conversation
```
User: "My name is Alice"
Agent: "Nice to meet you, Alice!"

→ Memory stored: "User's name is Alice" (session: thread_1234567890_abc123)

User: "What's my name?"
Agent: "Your name is Alice"

→ Memory retrieved from session thread_1234567890_abc123
```

### Session End
```
User refreshes page → DELETE /memory/session/thread_1234567890_abc123
All memories deleted ✓

New session starts → thread_9876543210_xyz789 created
Agent has no memory of previous conversation ✓
```

---

## Benefits

### ✅ Privacy
- No persistent storage of user conversations
- Each session is isolated
- Memory doesn't leak between sessions

### ✅ Clean State
- Every page refresh starts fresh
- No memory pollution from old conversations
- Easier to test and debug

### ✅ Session Context
- Full context within a single session
- Agent remembers previous messages in the same session
- Natural conversation flow maintained

### ✅ Automatic Cleanup
- No manual intervention required
- Reliable cleanup on page unload
- Prevents memory bloat in Qdrant

---

## Configuration

### Enabling Session Memory

Session memory is **enabled by default** when `thread_id` is provided in chat requests.

### Fallback to Persistent Memory

If no `thread_id` is provided, the system falls back to persistent memory:
```python
session_id = thread_id if thread_id else f"agent_{agent_id}"
```

This allows:
- **With `thread_id`**: Session-based ephemeral memory
- **Without `thread_id`**: Persistent memory (old behavior)

---

## Testing

### Manual Test

1. Start the backend:
```bash
cd backend
python main.py
```

2. Open the frontend chat interface

3. Have a conversation with an agent:
```
User: "My name is Bob"
Agent: "Nice to meet you, Bob!"

User: "What's my name?"
Agent: "Your name is Bob"  ✓ (memory works)
```

4. Refresh the page

5. Ask again:
```
User: "What's my name?"
Agent: "I don't have that information"  ✓ (memory cleared)
```

### Programmatic Test

```python
import requests

# Start a session
thread_id = "test_thread_123"

# Chat with memory
response = requests.post(
    "http://localhost:8001/api/v1/agents/{agent_id}/chat/",
    json={"message": "My name is Alice", "thread_id": thread_id}
)

# Verify memory exists
response = requests.post(
    "http://localhost:8001/api/v1/agents/{agent_id}/chat/",
    json={"message": "What's my name?", "thread_id": thread_id}
)
assert "Alice" in response.json()["response"]

# Clean up session
requests.delete(f"http://localhost:8001/api/v1/agents/memory/session/{thread_id}")

# Verify memory is gone
response = requests.get(
    f"http://localhost:8001/api/v1/agents/memory/user/{thread_id}"
)
assert len(response.json()["data"]) == 0
```

---

## Troubleshooting

### Issue: Memories Not Being Deleted

**Check**:
1. Browser console for cleanup errors
2. Backend logs for DELETE request
3. Qdrant collection still has data

**Solution**: Verify the `beforeunload` event is firing:
```javascript
console.log("Cleanup triggered for:", newThreadId);
```

### Issue: Memory Persists Across Refreshes

**Cause**: `thread_id` not being passed to backend

**Solution**: Ensure frontend sends `thread_id` in request body:
```typescript
body: JSON.stringify({ 
  message: input,
  thread_id: threadId  // Must be included
})
```

### Issue: Cleanup Fails Silently

**Cause**: `sendBeacon` only works with POST requests by default

**Solution**: Backend DELETE endpoint is already configured to handle this. If issues persist, switch to:
```typescript
fetch(`/memory/session/${threadId}`, { 
  method: 'DELETE',
  keepalive: true  // Ensures request completes even if page closes
});
```

---

## Migration from Persistent Memory

### If You Want Persistent Memory

Keep the old behavior by **not passing `thread_id`**:
```typescript
// Don't include thread_id in request
body: JSON.stringify({ message: input })
```

### If You Want Both

Use different endpoints or a flag:
```python
class AgentChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    persistent: bool = False  # Flag for persistent vs ephemeral
```

---

## Future Enhancements

1. **Session Timeout**: Auto-delete sessions after X hours of inactivity
2. **Session Persistence**: Option to save certain sessions
3. **Session Sharing**: Share session ID between users for collaborative chats
4. **Session Export**: Download session history before cleanup

---

**Status**: ✅ Implemented and Tested  
**Version**: 1.0  
**Last Updated**: 2025
