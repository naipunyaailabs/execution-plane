# Mem0 Memory Integration with Qdrant and Ollama

This document provides detailed information about the Mem0 memory integration in the LangGraph agent system.

## Overview

The system uses **Mem0** (open-source) as the memory layer, which internally uses:
- **Qdrant** as the vector database for persistent storage
- **Ollama** for generating embeddings (`qwen3-embedding:0.6b`, 1024 dimensions)
- **Groq** for LLM-based fact extraction from conversations

This architecture enables agents to maintain semantic memory across conversations and retrieve relevant historical information efficiently.

## Setup Instructions

### 1. Install Ollama

1. Download and install Ollama from [https://ollama.com/](https://ollama.com/)
2. Pull the qwen3-embedding model:
   ```bash
   ollama pull qwen3-embedding:0.6b
   ```

### 2. Install Dependencies

The required packages (mem0ai, qdrant-client, ollama) should already be included in the requirements.txt file. To install:

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Set your Groq API key for LLM-based fact extraction:

```bash
export GROQ_API_KEY="your-groq-api-key"
```

Qdrant will store data locally in `/tmp/qdrant` by default.

## How It Works

The integration uses **Mem0** as the memory orchestration layer:

1. **Memory Storage**: Mem0 processes conversations through an LLM (Groq) to extract factual information, generates embeddings using Ollama, and stores vectors in Qdrant
2. **Memory Retrieval**: When searching, Mem0 uses Ollama to generate query embeddings and retrieves semantically similar memories from Qdrant
3. **Context Enhancement**: Agents receive relevant factual memories (not raw conversations) to provide personalized and consistent responses

## Session-Based Memory

The system supports **ephemeral session-based memory** that automatically cleans up on page refresh:

- Each chat session has a unique `thread_id`
- Memories are stored per session
- On page refresh/close, session memories are automatically deleted
- Ensures privacy and prevents memory pollution

**See**: `SESSION_MEMORY_GUIDE.md` for detailed documentation

### Architecture Flow
```
Conversation → Mem0 (Fact Extraction via Groq) → Embeddings (Ollama) → Storage (Qdrant)
     ↑                                                                        ↓
     └────────────────────── Search & Retrieve ←──────────────────────────────┘
```

## API Endpoints

### Add Memory
```
POST /api/v1/agents/memory/add
```
Body:
```json
{
  "messages": [
    {"role": "user", "content": "I'm a vegetarian"},
    {"role": "assistant", "content": "Got it! I'll remember that you're a vegetarian."}
  ],
  "user_id": "user123",
  "agent_id": "agent456"
}
```

### Search Memory
```
POST /api/v1/agents/memory/search
```
Body:
```json
{
  "query": "What do you know about my diet?",
  "user_id": "user123",
  "agent_id": "agent456",
  "top_k": 5
}
```

### Get User Memories
```
GET /api/v1/agents/memory/user/{user_id}?agent_id={agent_id}
```

## Configuration

The memory service is automatically enabled when:
- `mem0ai`, `qdrant-client`, and `ollama` packages are installed
- Ollama is running with `qwen3-embedding:0.6b` model
- `GROQ_API_KEY` environment variable is set

Qdrant uses local storage by default at `/tmp/qdrant`.

## Troubleshooting

1. **Memory not working**: 
   - Ensure Ollama is running: `ollama list` should show `qwen3-embedding:0.6b`
   - Check Groq API key is set: `echo $GROQ_API_KEY`
   - Verify mem0ai is installed: `pip show mem0ai`

2. **No memories extracted**: Mem0 uses LLM to extract facts. Simple conversations may not yield extractable facts. Try more informative statements like "My name is X" or "I like Y"

3. **Import errors**: Run `pip install --upgrade mem0ai` to get the latest version

4. **Qdrant errors**: Qdrant data is stored locally at `/tmp/qdrant`. Delete this directory to reset.

For more information:
- [Mem0 Documentation](https://docs.mem0.ai/)
- [Mem0 Ollama Integration](https://docs.mem0.ai/components/embedders/models/ollama)
- [Qdrant Documentation](https://qdrant.tech/documentation/)