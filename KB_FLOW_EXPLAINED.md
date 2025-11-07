# Knowledge Base System - Complete Flow Explanation

## 🎯 Quick Overview

**What it does:** Allows agents to answer questions based on uploaded documents (text, PDFs, DOCX, URLs)

**How it works:** 
1. Documents → Split into chunks
2. Chunks → Convert to embeddings (1024-dim vectors)
3. Embeddings → Store in Qdrant vector database
4. User question → Convert to embedding → Find similar chunks → Send to LLM as context

---

## 📊 Architecture Diagram

```
User Input (Text/File/URL)
         ↓
    Frontend (React)
         ↓
    FastAPI Endpoint
         ↓
  KB Service (Python)
         ↓
    ┌────┴────┐
    ↓         ↓
Ollama      Qdrant        SQLite
(Embeddings) (Vectors)   (Metadata)
```

---

## 🔄 Flow 1: Upload Text to Knowledge Base

### Step-by-Step Process

**1. User Creates Agent with KB Text**
```
Location: frontend/src/components/AgentBuilder.tsx
Action: User types "CognitBotz email is contact@cognitbotz.com" in Text tab
```

**2. Frontend: Create Agent**
```javascript
POST /api/v1/agents/
Body: { name: "Test Agent", llm_provider: "groq", ... }
Response: { agent_id: "abc-123" }
```

**3. Frontend: Create Knowledge Base**
```javascript
POST /api/v1/knowledge-bases/
Body: { 
  agent_id: "abc-123",
  name: "Test Agent Knowledge Base",
  embedding_model: "qwen3-embedding:0.6b"
}
Response: { kb_id: "kb-456" }
```

**4. Frontend: Upload Text**
```javascript
POST /api/v1/knowledge-bases/kb-456/documents/text
Body: FormData { text: "CognitBotz email is contact@cognitbotz.com" }
```

**5. Backend: API Route Receives Request**
```python
# File: backend/api/v1/knowledge_base.py
@router.post("/{kb_id}/documents/text")
async def add_text_document(kb_id: str, text: str = Form(...)):
    doc_data = KnowledgeDocumentCreate(
        kb_id=kb_id,
        source_type=KnowledgeSourceType.TEXT,
        source_content=text
    )
    return await kb_service.add_document(doc_data)
```

**6. KB Service: Create Document Record**
```python
# File: backend/services/knowledge_base_service.py
async def add_document(self, doc_data):
    # Generate UUID
    doc_id = str(uuid.uuid4())
    
    # Create database record
    db_doc = KnowledgeDocument(
        doc_id=doc_id,
        kb_id=doc_data.kb_id,
        source_type=doc_data.source_type,
        source_content=doc_data.source_content,
        status=ProcessingStatus.PENDING
    )
    
    # Save to SQLite
    self.db.add(db_doc)
    self.db.commit()
    
    # Process the document
    await self._process_document(db_doc, kb)
```

**7. Process Document - THE CORE LOGIC**
```python
# File: backend/services/knowledge_base_service.py
async def _process_document(self, db_doc, kb):
    # Step 7a: Load content
    text = db_doc.source_content  # "CognitBotz email is contact@..."
    documents = [Document(page_content=text)]
    
    # Step 7b: Split into chunks (if text > 1000 chars)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,      # Max 1000 characters per chunk
        chunk_overlap=200     # 200 chars overlap between chunks
    )
    chunks = text_splitter.split_documents(documents)
    # Result: [Chunk("CognitBotz email is contact@cognitbotz.com")]
    
    # Step 7c: Generate embeddings via Ollama
    embeddings = self._get_embeddings(
        texts=[chunk.page_content for chunk in chunks],
        model="qwen3-embedding:0.6b"
    )
    # Result: [[0.123, -0.456, 0.789, ...]]  (1024 dimensions)
    
    # Step 7d: Prepare Qdrant points
    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        points.append({
            "id": f"{db_doc.doc_id}_{i}",  # "doc-789_0"
            "vector": embedding,            # [0.123, -0.456, ...]
            "payload": {
                "doc_id": db_doc.doc_id,
                "kb_id": kb.kb_id,
                "agent_id": kb.agent_id,
                "chunk_index": i,
                "chunk_text": chunk.page_content,
                "source_type": "text"
            }
        })
    
    # Step 7e: Store in Qdrant
    self.qdrant_client.upsert(
        collection_name=kb.collection_name,
        points=points
    )
    
    # Step 7f: Update status
    db_doc.status = ProcessingStatus.COMPLETED
    db_doc.processed_chunks = len(chunks)
    self.db.commit()
```

**8. Embedding Generation Details**
```python
def _get_embeddings(self, texts, model):
    embeddings = []
    for text in texts:
        # Call Ollama API
        response = self.ollama_client.embeddings(
            model="qwen3-embedding:0.6b",
            prompt=text
        )
        embeddings.append(response['embedding'])
    return embeddings

# What Ollama does:
# 1. Loads qwen3-embedding:0.6b model
# 2. Processes text through neural network
# 3. Returns 1024-dimensional vector
# 4. Vector captures semantic meaning
# Example: "email" and "contact" have similar vectors
```

**9. Qdrant Storage Structure**
```
/tmp/qdrant_kb/
└── collection/
    └── kb_abc123ab_test_agent_knowledge_base_xyz/
        ├── meta.json          # Collection metadata
        ├── segments/          # Vector data
        │   ├── 000001.data   # Actual vectors
        │   └── 000001.index  # HNSW index for fast search
        └── payload/           # Chunk text and metadata
            └── 000001.data
```

---

## 🔄 Flow 2: Chat with Agent Using KB

### Step-by-Step Process

**1. User Sends Message**
```javascript
// frontend/src/components/AgentChat.tsx
POST /api/v1/agents/abc-123/chat/
Body: { 
  message: "What is the company email?",
  thread_id: "thread_xyz"
}
```

**2. Agent Service: Execute Agent**
```python
# backend/services/agent_service.py
async def execute_agent(self, agent_id, input_text, session_id):
    # Retrieve KB context
    kb_service = KnowledgeBaseService(self.db)
    knowledge_context = await kb_service.query_agent_knowledge(
        agent_id=agent_id,
        query=input_text,
        top_k=5
    )
```

**3. KB Service: Query Knowledge**
```python
async def query_agent_knowledge(self, agent_id, query, top_k):
    # Step 3a: Find all KBs for this agent
    kbs = self.db.query(KnowledgeBase).filter_by(agent_id=agent_id).all()
    # Result: [KB(kb_id="kb-456", collection_name="kb_abc123ab_...")]
    
    # Step 3b: Generate query embedding
    query_embedding = self._get_embeddings(
        [query],  # "What is the company email?"
        model="qwen3-embedding:0.6b"
    )[0]
    # Result: [0.789, -0.234, 0.567, ...]  (1024 dimensions)
    
    # Step 3c: Search Qdrant
    results = self.qdrant_client.search(
        collection_name="kb_abc123ab_test_agent_knowledge_base_xyz",
        query_vector=query_embedding,
        limit=5
    )
    # Qdrant compares query vector to all stored vectors
    # Uses cosine similarity: dot(query, chunk) / (||query|| * ||chunk||)
    # Returns top 5 most similar chunks
    
    # Step 3d: Format results
    context = "Relevant information from knowledge base:\n\n"
    for i, result in enumerate(results, 1):
        context += f"{i}. [Score: {result.score:.2f}] {result.payload['chunk_text']}\n\n"
    
    return context
```

**4. Build LLM Prompt**
```python
# backend/services/agent_service.py
system_content = agent.system_prompt  # "You are a helpful assistant..."
system_content += f"\n\n{knowledge_context}"
# System prompt now includes:
# "You are a helpful assistant...
#  
#  Relevant information from knowledge base:
#  1. [Score: 0.87] CognitBotz email is contact@cognitbotz.com"

messages = [
    SystemMessage(content=system_content),
    HumanMessage(content="What is the company email?")
]
```

**5. Call LLM**
```python
response = await asyncio.wait_for(
    asyncio.to_thread(langgraph_agent.invoke, {"messages": messages}),
    timeout=60.0
)
# LLM sees the KB context in system prompt
# Generates grounded response: "The company email is contact@cognitbotz.com"
```

**6. Return Response**
```python
return response  # "The company email is contact@cognitbotz.com"
```

---

## 🗂️ Key Files Reference

### Most Important Files

**1. `backend/services/knowledge_base_service.py` (298 lines)**
- **Purpose:** Core KB logic - embeddings, storage, querying
- **Key Methods:**
  - `_get_embeddings()` - Line 42: Generate embeddings via Ollama
  - `create_knowledge_base()` - Line 49: Create KB and Qdrant collection
  - `add_document()` - Line 121: Add document to KB
  - `_process_document()` - Line 148: **MOST IMPORTANT** - Chunk, embed, store
  - `query_agent_knowledge()` - Line 256: Search KB for relevant chunks

**2. `backend/api/v1/knowledge_base.py` (203 lines)**
- **Purpose:** REST API endpoints
- **Key Routes:**
  - `POST /` - Create KB
  - `POST /{kb_id}/documents/text` - Add text
  - `POST /{kb_id}/documents/file` - Upload file
  - `POST /{kb_id}/documents/url` - Add URL
  - `POST /{kb_id}/query` - Query KB

**3. `backend/services/agent_service.py` (747 lines)**
- **Purpose:** Agent execution and context integration
- **Key Methods:**
  - `execute_agent()` - Line 155: Retrieve KB + memory context
  - `chat_with_agent()` - Line 106: Main chat handler

**4. `frontend/src/components/AgentBuilder.tsx` (661 lines)**
- **Purpose:** Create agents with KB
- **Key Logic:**
  - Lines 167-169: KB state management
  - Lines 223-282: KB creation and upload
  - Lines 567-599: File upload UI

**5. `backend/models/knowledge_base.py` (70 lines)**
- **Purpose:** Database models
- **Models:**
  - `KnowledgeBase` - KB metadata
  - `KnowledgeDocument` - Document records

---

## 🧠 How Embeddings Work

### What are Embeddings?

**Embeddings = Dense vector representations of text that capture semantic meaning**

```python
# Example (simplified, actual vectors are 1024-dim):
"email" → [0.8, 0.2, -0.3, 0.5]
"contact" → [0.7, 0.3, -0.2, 0.4]
"weather" → [-0.1, -0.5, 0.9, -0.2]

# Similar meanings = similar vectors
cosine_similarity("email", "contact") = 0.95  # Very similar
cosine_similarity("email", "weather") = 0.12  # Not similar
```

### Ollama Embedding Model

**Model:** `qwen3-embedding:0.6b`
- **Dimensions:** 1024
- **Size:** ~600MB
- **Speed:** ~100ms per chunk
- **Language:** Multilingual (English, Chinese, etc.)

**API Call:**
```python
POST http://localhost:11434/api/embeddings
{
  "model": "qwen3-embedding:0.6b",
  "prompt": "CognitBotz email is contact@cognitbotz.com"
}

Response:
{
  "embedding": [0.123, -0.456, 0.789, ..., 0.234]  # 1024 numbers
}
```

### Why Embeddings for Search?

**Traditional keyword search:**
```
Query: "company email"
Document: "contact information: contact@cognitbotz.com"
Match: NO ❌ (no exact word match)
```

**Embedding-based search:**
```
Query embedding: [0.8, 0.3, -0.2, ...]
Document embedding: [0.75, 0.35, -0.18, ...]
Similarity: 0.92 ✅ (semantic match even without exact words)
```

---

## 💾 Storage Architecture

### SQLite (Metadata)
```sql
-- Tables: knowledge_bases, knowledge_documents
-- Stores: KB config, document info, status
-- Location: backend/agents.db

SELECT * FROM knowledge_bases;
| kb_id  | agent_id | name        | collection_name | chunk_size |
|--------|----------|-------------|-----------------|------------|
| kb-456 | abc-123  | Test KB     | kb_abc123ab_... | 1000       |

SELECT * FROM knowledge_documents;
| doc_id  | kb_id  | source_type | status    | processed_chunks |
|---------|--------|-------------|-----------|------------------|
| doc-789 | kb-456 | text        | completed | 1                |
```

### Qdrant (Vectors)
```
Location: /tmp/qdrant_kb/
Purpose: Store embeddings + enable fast similarity search
Algorithm: HNSW (Hierarchical Navigable Small World)
Search time: O(log N) - very fast even with millions of vectors

Structure per collection:
- Vectors: [0.123, -0.456, ...] × 1024 dimensions
- Payload: { chunk_text, doc_id, kb_id, agent_id, ... }
- Index: Optimized for cosine similarity search
```

---

## 🔍 Vector Search Process

### 1. Indexing (When uploading document)
```
Document chunks → Generate embeddings → Build HNSW graph
                                        ↓
                            Graph of nearest neighbors
                            (Fast navigation structure)
```

### 2. Searching (When querying)
```
Query "email" → Generate embedding [0.8, 0.3, ...]
                       ↓
           Navigate HNSW graph (log N comparisons)
                       ↓
           Find K nearest neighbors
                       ↓
           Return top 5 similar chunks with scores
```

### 3. Similarity Calculation
```python
def cosine_similarity(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sqrt(sum(a * a for a in vec1))
    magnitude2 = sqrt(sum(b * b for b in vec2))
    return dot_product / (magnitude1 * magnitude2)

# Score ranges from -1 to 1
# 1 = identical
# 0 = orthogonal (no similarity)
# -1 = opposite
```

---

## 🚀 Complete Data Flow Summary

```
USER INPUT
    ↓
[Text/File/URL]
    ↓
Frontend (AgentBuilder.tsx)
    ↓
API Endpoint (knowledge_base.py)
    ↓
KB Service (knowledge_base_service.py)
    ↓
┌───┴───┬───────┬────────┐
↓       ↓       ↓        ↓
Text   Load    Split   Embed
       ↓       ↓        ↓
  Documents  Chunks  Vectors
                      ↓
              ┌───────┴────────┐
              ↓                ↓
          Qdrant            SQLite
      (Vectors +         (Metadata)
       Payload)
              ↓
       STORED ✓

QUERY TIME
    ↓
User question
    ↓
Generate query embedding
    ↓
Search Qdrant
    ↓
Get top K similar chunks
    ↓
Format as context string
    ↓
Add to LLM prompt
    ↓
LLM generates grounded response
    ↓
Return to user ✓
```

---

## 📈 Performance Characteristics

**Embedding Generation:**
- Speed: ~100ms per chunk (Ollama local)
- Batch: 10 chunks = ~1 second
- Large doc (50 chunks) = ~5 seconds

**Vector Search:**
- 1,000 vectors: <10ms
- 100,000 vectors: ~50ms
- 1,000,000 vectors: ~100ms

**Complete KB Creation:**
- Text (1 page): ~1-2 seconds
- PDF (10 pages): ~5-10 seconds
- Large doc (100 pages): ~30-60 seconds

**Chat Response with KB:**
- Query embedding: ~100ms
- Vector search: ~50ms
- LLM response: 1-5 seconds
- **Total: 1-5 seconds** (LLM is bottleneck)

---

## 🎓 Key Concepts Summary

**RAG (Retrieval-Augmented Generation):**
Retrieve relevant docs → Augment LLM prompt → Generate grounded response

**Chunking:**
Split large documents into smaller pieces (1000 chars) for better retrieval

**Embeddings:**
Convert text to vectors that capture semantic meaning

**Vector Database:**
Store embeddings + enable fast similarity search

**Singleton Pattern:**
Reuse single Qdrant client to avoid lock conflicts

**Cosine Similarity:**
Measure how similar two vectors are (used for search)

---

This system enables your agents to answer questions accurately based on uploaded documents rather than just relying on pre-trained knowledge! 🎉
