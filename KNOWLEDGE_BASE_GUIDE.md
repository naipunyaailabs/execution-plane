# Knowledge Base Implementation Guide

## Overview

The Knowledge Base system allows each agent to have its own isolated vector database collection for storing and retrieving domain-specific information. This enables agents to provide context-aware responses based on uploaded documents, URLs, and text.

## Architecture

### Components

1. **Database Models**
   - `KnowledgeBase`: Stores metadata about each knowledge base
   - `KnowledgeDocument`: Tracks individual documents added to a knowledge base

2. **Vector Storage**
   - Each knowledge base gets a unique Qdrant collection
   - Collection naming: `kb_{agent_id}_{kb_name}_{unique_id}`
   - Isolated per agent to prevent cross-contamination

3. **Document Processing**
   - Text chunking using RecursiveCharacterTextSplitter
   - Embeddings generated using Ollama (nomic-embed-text by default)
   - Support for multiple document types: Text, URLs, PDF, DOCX, TXT, MD, HTML

4. **Integration**
   - Automatic knowledge base querying during agent execution
   - Context injection into system prompts
   - Works alongside Mem0 conversational memory

## Key Features

### 1. Isolated Collections Per Agent
- Each agent's knowledge base is stored in a separate Qdrant collection
- Prevents knowledge leakage between agents
- Easy to manage and delete per-agent data

### 2. Multiple Document Types
- **Text**: Direct text input
- **URLs**: Web scraping with HTML parsing
- **Files**: PDF, DOCX, TXT, MD, HTML support

### 3. Smart Chunking
- Configurable chunk size (default: 1000 characters)
- Configurable overlap (default: 200 characters)
- Recursive character splitting for semantic coherence

### 4. Semantic Search
- Vector similarity search using cosine distance
- Configurable top-k results
- Score-based relevance filtering

### 5. Unified Context
- Knowledge base context combined with Mem0 memories
- Injected into agent's system prompt
- Seamless integration with existing agent types

## API Endpoints

### Knowledge Base Management

```
POST   /api/v1/knowledge-bases/
GET    /api/v1/knowledge-bases/{kb_id}
GET    /api/v1/knowledge-bases/agent/{agent_id}
DELETE /api/v1/knowledge-bases/{kb_id}
```

### Document Management

```
POST   /api/v1/knowledge-bases/{kb_id}/documents/text
POST   /api/v1/knowledge-bases/{kb_id}/documents/url
POST   /api/v1/knowledge-bases/{kb_id}/documents/file
GET    /api/v1/knowledge-bases/{kb_id}/documents
DELETE /api/v1/knowledge-bases/documents/{doc_id}
```

### Query

```
POST   /api/v1/knowledge-bases/{kb_id}/query
```

## Usage Examples

### 1. Create Knowledge Base

```python
import requests

kb_data = {
    "agent_id": "your-agent-id",
    "name": "Product Documentation",
    "description": "Knowledge base for product docs",
    "embedding_model": "nomic-embed-text",
    "chunk_size": 1000,
    "chunk_overlap": 200
}

response = requests.post(
    "http://localhost:8001/api/v1/knowledge-bases/",
    json=kb_data
)
kb = response.json()
```

### 2. Add Text Document

```python
form_data = {
    "text": "Your documentation text here..."
}

response = requests.post(
    f"http://localhost:8001/api/v1/knowledge-bases/{kb_id}/documents/text",
    data=form_data
)
```

### 3. Add URL Document

```python
form_data = {
    "url": "https://docs.example.com/api"
}

response = requests.post(
    f"http://localhost:8001/api/v1/knowledge-bases/{kb_id}/documents/url",
    data=form_data
)
```

### 4. Add File Document

```python
files = {
    "file": open("document.pdf", "rb")
}

response = requests.post(
    f"http://localhost:8001/api/v1/knowledge-bases/{kb_id}/documents/file",
    files=files
)
```

### 5. Query Knowledge Base

```python
query_data = {
    "query": "How do I authenticate?",
    "top_k": 5
}

response = requests.post(
    f"http://localhost:8001/api/v1/knowledge-bases/{kb_id}/query",
    json=query_data
)
results = response.json()
```

### 6. Chat with Agent (Auto-retrieval)

```python
chat_data = {
    "message": "How do I authenticate with the API?",
    "thread_id": "session_123"
}

response = requests.post(
    f"http://localhost:8001/api/v1/agents/{agent_id}/chat/",
    json=chat_data
)
# Agent automatically retrieves relevant knowledge base context
```

## Frontend Integration

The UI already supports knowledge base during agent creation:

1. **Text Mode**: Paste documentation or context directly
2. **Links Mode**: Add URLs (one per line) to scrape
3. **Upload Mode**: Upload PDF, DOCX, or text files

When creating an agent with knowledge data:
1. Agent is created first
2. Knowledge base is automatically created
3. Documents are processed and embedded
4. Agent can immediately use the knowledge

## Technical Details

### Embedding Model

Default: `qwen3-embedding:0.6b` (via Ollama)
- Dimension: 1024
- Optimized for multilingual text
- Fast and efficient

### Vector Storage

- Database: Qdrant (local at `/tmp/qdrant_kb`)
- Distance metric: Cosine similarity
- Each agent gets isolated collections
- Metadata stored: doc_id, kb_id, agent_id, chunk_index, source info
- Note: Separate from Mem0's storage at `/tmp/qdrant`

### Document Processing Flow

1. **Ingestion**: Document uploaded via API
2. **Loading**: Content extracted based on type
3. **Chunking**: Text split into semantic chunks
4. **Embedding**: Each chunk converted to vector
5. **Storage**: Vectors stored in Qdrant with metadata
6. **Status Update**: Document marked as completed/failed

### Retrieval Flow

1. **User Query**: User sends message to agent
2. **Query Embedding**: User message embedded
3. **Vector Search**: Top-k similar chunks retrieved
4. **Context Building**: Chunks formatted into context string
5. **Prompt Injection**: Context added to system prompt
6. **Agent Response**: Agent generates response with context

## Best Practices

### 1. Chunk Size Selection
- **Small chunks (500-800)**: Better for precise queries
- **Medium chunks (1000-1500)**: Balanced performance
- **Large chunks (2000+)**: Better for broad context

### 2. Document Organization
- Create separate knowledge bases for different domains
- Use descriptive names for knowledge bases
- Tag documents with metadata for filtering

### 3. Performance Optimization
- Batch document uploads when possible
- Use appropriate top_k values (3-5 usually sufficient)
- Monitor collection sizes

### 4. Maintenance
- Regularly clean up outdated documents
- Update knowledge bases when documentation changes
- Monitor failed document processing

## Troubleshooting

### Document Processing Failures

Check `KnowledgeDocument.error_message` for details:
```python
response = requests.get(f"/api/v1/knowledge-bases/{kb_id}/documents")
docs = response.json()
for doc in docs:
    if doc['status'] == 'failed':
        print(f"Failed: {doc['file_name']} - {doc['error_message']}")
```

### Missing Context in Responses

1. Verify knowledge base exists for agent
2. Check document processing status
3. Test direct knowledge base query
4. Verify embeddings are created
5. Check Qdrant collection

### URL Scraping Issues

- Ensure URLs are accessible
- Check for SSL certificate errors
- Some sites may block scraping
- Consider manual text extraction for problematic sites

## Database Schema

### knowledge_bases

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| kb_id | String | Unique identifier |
| agent_id | String | Associated agent |
| name | String | Display name |
| description | Text | Optional description |
| collection_name | String | Qdrant collection |
| embedding_model | String | Model for embeddings |
| chunk_size | Integer | Chunk size config |
| chunk_overlap | Integer | Overlap config |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Update timestamp |

### knowledge_documents

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| doc_id | String | Unique identifier |
| kb_id | String | Parent knowledge base |
| source_type | Enum | TEXT/URL/FILE |
| source_content | Text | Original content (truncated) |
| source_url | String | Source URL if applicable |
| file_name | String | Original filename |
| file_path | String | Stored file path |
| chunk_count | Integer | Number of chunks |
| status | Enum | PENDING/PROCESSING/COMPLETED/FAILED |
| error_message | Text | Error details if failed |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Update timestamp |

## Security Considerations

1. **File Upload Validation**
   - Whitelist allowed file extensions
   - Scan for malicious content
   - Limit file sizes

2. **URL Scraping**
   - Validate URL format
   - Implement request timeouts
   - Handle SSL verification
   - Rate limiting

3. **Access Control**
   - Knowledge bases isolated per agent
   - Filter by agent_id in queries
   - No cross-agent data access

## Future Enhancements

1. **Advanced Filtering**
   - Filter by document metadata
   - Date range filtering
   - Source type filtering

2. **Reranking**
   - Implement semantic reranking
   - Cross-encoder models
   - Hybrid search (BM25 + vector)

3. **Multi-modal Support**
   - Image document support
   - Audio transcription
   - Video content extraction

4. **Analytics**
   - Query performance metrics
   - Popular queries tracking
   - Knowledge gap identification

5. **Incremental Updates**
   - Update existing documents
   - Version control for knowledge
   - Change detection

## Testing

Run the test script:
```bash
cd backend
python test_knowledge_base.py
```

This will:
1. Create a test agent
2. Create a knowledge base
3. Add text and URL documents
4. Query the knowledge base
5. Test agent chat with context
6. Clean up resources

## Support

For issues or questions:
1. Check server logs for detailed errors
2. Verify Ollama is running (for embeddings)
3. Check Qdrant storage at `/tmp/qdrant_kb` (KB) and `/tmp/qdrant` (Mem0)
4. Review document processing status
5. Test knowledge base queries directly
