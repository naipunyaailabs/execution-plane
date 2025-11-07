# Knowledge Base Implementation - File Map

## 📁 File Organization

```
mech-agent/
├── frontend/src/components/
│   ├── AgentBuilder.tsx ⭐     # Create agents with KB
│   └── AgentChat.tsx           # Chat interface
│
├── backend/
│   ├── api/v1/
│   │   ├── knowledge_base.py ⭐ # KB REST endpoints
│   │   └── agents.py           # Chat endpoint
│   │
│   ├── services/
│   │   ├── knowledge_base_service.py ⭐⭐⭐ # CORE KB LOGIC
│   │   ├── agent_service.py ⭐  # Agent execution + KB integration
│   │   └── memory_service.py   # Mem0 integration
│   │
│   ├── models/
│   │   ├── knowledge_base.py   # SQLAlchemy models
│   │   └── agent.py            # Agent model
│   │
│   ├── schemas/
│   │   ├── knowledge_base.py   # Pydantic schemas
│   │   └── agent.py            # Agent schemas
│   │
│   └── core/
│       ├── database.py         # SQLite connection
│       └── config.py           # Configuration
│
└── Storage/
    ├── /tmp/qdrant_kb/         # KB vectors (Qdrant)
    ├── /tmp/qdrant/            # Mem0 vectors (Qdrant)
    ├── /tmp/knowledge_base_uploads/  # Uploaded files
    └── backend/agents.db       # SQLite metadata
```

⭐ = Important file
⭐⭐⭐ = Most critical file

---

## 🔍 File Details

### Frontend Layer

#### `frontend/src/components/AgentBuilder.tsx`
**Lines: 661 | Language: TypeScript React**

**Purpose:** UI for creating agents with knowledge bases

**Key State Variables:**
```typescript
const [knowledgeMode, setKnowledgeMode] = useState<"upload" | "links" | "text">("text");
const [knowledgeText, setKnowledgeText] = useState("");      // For text input
const [knowledgeLinks, setKnowledgeLinks] = useState("");    // For URL input
const [knowledgeFiles, setKnowledgeFiles] = useState<File[]>([]); // For file upload
```

**Important Sections:**
- **Lines 167-169:** State declarations for KB modes
- **Lines 480-599:** KB input UI (tabs: Text, Links, Upload)
- **Lines 223-282:** KB creation and document upload logic in `handleGenerateAgent()`

**API Calls Made:**
```typescript
// 1. Create KB
POST /api/v1/knowledge-bases/
Body: { agent_id, name, embedding_model }

// 2. Add text document
POST /api/v1/knowledge-bases/{kb_id}/documents/text
FormData: { text }

// 3. Add URL document
POST /api/v1/knowledge-bases/{kb_id}/documents/url
FormData: { url }

// 4. Upload file
POST /api/v1/knowledge-bases/{kb_id}/documents/file
FormData: { file }
```

---

#### `frontend/src/components/AgentChat.tsx`
**Lines: 458 | Language: TypeScript React**

**Purpose:** Chat interface with agents (KB context automatically retrieved)

**Important Functions:**
```typescript
const handleSend = async () => {
  // Send message to agent
  const response = await fetch(`/api/v1/agents/${selectedAgentId}/chat/`, {
    method: 'POST',
    body: JSON.stringify({ 
      message: messageToSend,
      thread_id: threadId 
    })
  });
  // Display response (KB context already integrated by backend)
};
```

**Key Lines:**
- **185-245:** Message sending and response handling
- **206-217:** Chat API call with thread_id for session management

---

### Backend API Layer

#### `backend/api/v1/knowledge_base.py`
**Lines: 203 | Language: Python (FastAPI)**

**Purpose:** REST API endpoints for all KB operations

**Endpoints:**

```python
# 1. Create Knowledge Base
@router.post("/")
async def create_knowledge_base(kb_data: KnowledgeBaseCreate):
    # Creates KB + Qdrant collection
    return await kb_service.create_knowledge_base(kb_data)

# 2. Add Text Document
@router.post("/{kb_id}/documents/text")
async def add_text_document(kb_id: str, text: str = Form(...)):
    doc_data = KnowledgeDocumentCreate(
        kb_id=kb_id,
        source_type=KnowledgeSourceType.TEXT,
        source_content=text
    )
    return await kb_service.add_document(doc_data)

# 3. Add URL Document
@router.post("/{kb_id}/documents/url")
async def add_url_document(kb_id: str, url: str = Form(...)):
    doc_data = KnowledgeDocumentCreate(
        kb_id=kb_id,
        source_type=KnowledgeSourceType.URL,
        source_url=url
    )
    return await kb_service.add_document(doc_data)

# 4. Upload File Document
@router.post("/{kb_id}/documents/file")
async def add_file_document(kb_id: str, file: UploadFile):
    # Save file to /tmp/knowledge_base_uploads/
    # Create document record
    # Process file (extract text, chunk, embed, store)
    return doc

# 5. Query Knowledge Base
@router.post("/{kb_id}/query")
async def query_knowledge_base(kb_id: str, query: KnowledgeBaseQuery):
    return await kb_service.query_knowledge_base(
        kb_id=query.kb_id,
        query_text=query.query,
        top_k=query.top_k
    )

# 6. Get KB Details
@router.get("/{kb_id}")
async def get_knowledge_base(kb_id: str):
    return await kb_service.get_knowledge_base(kb_id)

# 7. List All KBs
@router.get("/")
async def list_knowledge_bases():
    return kb_service.list_knowledge_bases()

# 8. Delete KB
@router.delete("/{kb_id}")
async def delete_knowledge_base(kb_id: str):
    return await kb_service.delete_knowledge_base(kb_id)
```

**Dependencies:**
```python
from services.knowledge_base_service import KnowledgeBaseService
from schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeDocumentCreate
from models.knowledge_base import KnowledgeSourceType
```

---

#### `backend/api/v1/agents.py`
**Lines: 180 | Language: Python (FastAPI)**

**Purpose:** Agent management and chat endpoint

**Key Endpoint for KB:**
```python
@router.post("/{agent_id}/chat/")
async def chat_with_agent(
    agent_id: str,
    message: str = Body(...),
    thread_id: Optional[str] = Body(None)
):
    # Calls agent_service which automatically retrieves KB context
    response = await agent_service.chat_with_agent(
        agent_id=agent_id,
        message=message,
        thread_id=thread_id
    )
    return {"response": response}
```

---

### Backend Service Layer (Business Logic)

#### `backend/services/knowledge_base_service.py` ⭐⭐⭐
**Lines: 298 | Language: Python | MOST IMPORTANT FILE**

**Purpose:** All KB operations - embeddings, storage, querying

**Class Structure:**
```python
# Singleton Qdrant client (prevents lock conflicts)
_qdrant_client = None

def get_qdrant_client():
    """Get or create singleton QdrantClient instance"""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(path="/tmp/qdrant_kb")
    return _qdrant_client

class KnowledgeBaseService:
    def __init__(self, db: Session):
        self.db = db
        self.qdrant_client = get_qdrant_client()  # Reuse singleton
        self.ollama_client = OllamaClient()       # For embeddings
        self.upload_dir = "/tmp/knowledge_base_uploads"
```

**Critical Methods:**

**1. Generate Embeddings (Lines 42-47)**
```python
def _get_embeddings(self, texts: List[str], model: str = "qwen3-embedding:0.6b"):
    """Convert text chunks to 1024-dim vectors via Ollama"""
    embeddings = []
    for text in texts:
        response = self.ollama_client.embeddings(model=model, prompt=text)
        embeddings.append(response['embedding'])
    return embeddings
```

**2. Create KB (Lines 49-65)**
```python
async def create_knowledge_base(self, kb_data: KnowledgeBaseCreate):
    """Create KB + Qdrant collection"""
    # Generate collection name
    collection_name = self._generate_collection_name(kb_data.agent_id, kb_data.name)
    
    # Determine embedding dimensions
    embedding_dim = 1024  # qwen3-embedding:0.6b
    
    # Create Qdrant collection
    self.qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE)
    )
    
    # Save to SQLite
    db_kb = KnowledgeBase(kb_id=kb_id, ...)
    self.db.add(db_kb)
    self.db.commit()
    return db_kb
```

**3. Add Document (Lines 121-146)**
```python
async def add_document(self, doc_data: KnowledgeDocumentCreate):
    """Add document and trigger processing"""
    # Create DB record
    db_doc = KnowledgeDocument(
        doc_id=str(uuid.uuid4()),
        kb_id=doc_data.kb_id,
        source_type=doc_data.source_type,
        source_content=doc_data.source_content,
        status=ProcessingStatus.PENDING
    )
    self.db.add(db_doc)
    self.db.commit()
    
    # Process document (chunk, embed, store)
    await self._process_document(db_doc, kb)
    return db_doc
```

**4. Process Document (Lines 148-235) ⭐ MOST IMPORTANT METHOD**
```python
async def _process_document(self, db_doc: KnowledgeDocument, kb: KnowledgeBase):
    """
    THE CORE LOGIC - Transform document into searchable vectors
    
    Flow:
    1. Load content based on source type (TEXT/FILE/URL)
    2. Split into chunks (1000 chars, 200 overlap)
    3. Generate embeddings via Ollama
    4. Store vectors in Qdrant with metadata
    5. Update document status
    """
    
    # STEP 1: Load Content
    if db_doc.source_type == KnowledgeSourceType.TEXT:
        documents = [Document(page_content=db_doc.source_content)]
    
    elif db_doc.source_type == KnowledgeSourceType.FILE:
        loader = self._get_loader(db_doc.file_path)  # PyPDF/Docx2txt/HTML
        documents = loader.load()
    
    elif db_doc.source_type == KnowledgeSourceType.URL:
        response = requests.get(db_doc.source_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        documents = [Document(page_content=text)]
    
    # STEP 2: Chunk
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=kb.chunk_size,      # 1000
        chunk_overlap=kb.chunk_overlap  # 200
    )
    chunks = text_splitter.split_documents(documents)
    
    # STEP 3: Generate Embeddings
    embeddings = self._get_embeddings(
        [chunk.page_content for chunk in chunks],
        kb.embedding_model
    )
    
    # STEP 4: Create Qdrant Points
    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        points.append(PointStruct(
            id=f"{db_doc.doc_id}_{i}",
            vector=embedding,
            payload={
                "doc_id": db_doc.doc_id,
                "kb_id": kb.kb_id,
                "agent_id": kb.agent_id,
                "chunk_index": i,
                "chunk_text": chunk.page_content,
                "source_type": db_doc.source_type.value,
                "source_url": db_doc.source_url,
                "file_name": db_doc.file_name
            }
        ))
    
    # STEP 5: Store in Qdrant
    self.qdrant_client.upsert(
        collection_name=kb.collection_name,
        points=points
    )
    
    # STEP 6: Update Status
    db_doc.status = ProcessingStatus.COMPLETED
    db_doc.processed_chunks = len(chunks)
    self.db.commit()
```

**5. Query KB (Lines 256-298)**
```python
async def query_agent_knowledge(self, agent_id: str, query: str, top_k: int = 5):
    """
    Search all KBs for an agent and return relevant context
    
    Flow:
    1. Find all KBs for agent
    2. Generate query embedding
    3. Search Qdrant collections
    4. Format results as context string
    """
    
    # STEP 1: Get all KBs for agent
    kbs = self.db.query(KnowledgeBase).filter_by(agent_id=agent_id).all()
    if not kbs:
        return ""
    
    # STEP 2: Generate query embedding
    query_embedding = self._get_embeddings([query], kbs[0].embedding_model)[0]
    
    # STEP 3: Search each KB
    all_results = []
    for kb in kbs:
        try:
            results = self.qdrant_client.search(
                collection_name=kb.collection_name,
                query_vector=query_embedding,
                limit=top_k
            )
            all_results.extend(results)
        except Exception as e:
            print(f"Error searching KB {kb.kb_id}: {e}")
    
    # STEP 4: Format context
    if not all_results:
        return ""
    
    # Sort by score and take top_k overall
    all_results.sort(key=lambda x: x.score, reverse=True)
    top_results = all_results[:top_k]
    
    # Build context string
    context = "Relevant information from knowledge base:\n\n"
    for i, result in enumerate(top_results, 1):
        context += f"{i}. [Score: {result.score:.2f}] {result.payload['chunk_text']}\n\n"
    
    return context
```

**Dependencies:**
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from ollama import Client as OllamaClient
import requests
from bs4 import BeautifulSoup
```

---

#### `backend/services/agent_service.py`
**Lines: 747 | Language: Python**

**Purpose:** Agent execution logic, integrates KB context into chat

**KB Integration (Lines 187-205):**
```python
async def execute_agent(self, agent_id, input_text, session_id):
    # ... memory retrieval ...
    
    # Retrieve KB context with timeout
    knowledge_context = ""
    try:
        import asyncio
        from services.knowledge_base_service import KnowledgeBaseService
        kb_service = KnowledgeBaseService(self.db)
        
        # 10 second timeout for KB queries
        knowledge_context = await asyncio.wait_for(
            kb_service.query_agent_knowledge(agent_id, input_text, top_k=5),
            timeout=10.0
        )
        
        if knowledge_context:
            print(f"Retrieved KB context: {len(knowledge_context)} chars")
    
    except asyncio.TimeoutError:
        print(f"KB query timed out for agent {agent_id}")
    except Exception as kb_error:
        print(f"Error retrieving KB context: {kb_error}")
```

**Prompt Construction (Lines 215-224):**
```python
if agent.agent_type == "react":
    # Add KB context to system prompt
    system_content = agent.system_prompt or "You are a helpful AI assistant."
    
    if knowledge_context:
        system_content += f"\n\n{knowledge_context}"
    
    if memory_context:
        system_content += f"\n\n{memory_context}"
    
    messages.insert(0, SystemMessage(content=system_content))
```

---

### Backend Models (Database Schema)

#### `backend/models/knowledge_base.py`
**Lines: 70 | Language: Python (SQLAlchemy)**

**Purpose:** Database table definitions

**Models:**

```python
class KnowledgeBase(Base):
    """KB configuration and metadata"""
    __tablename__ = "knowledge_bases"
    
    kb_id = Column(String, primary_key=True)
    agent_id = Column(String, ForeignKey("agents.agent_id"))
    name = Column(String, nullable=False)
    description = Column(String)
    embedding_model = Column(String, default="qwen3-embedding:0.6b")
    collection_name = Column(String, unique=True, nullable=False)
    chunk_size = Column(Integer, default=1000)
    chunk_overlap = Column(Integer, default=200)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    documents = relationship("KnowledgeDocument", back_populates="knowledge_base")

class KnowledgeDocument(Base):
    """Individual documents in KB"""
    __tablename__ = "knowledge_documents"
    
    doc_id = Column(String, primary_key=True)
    kb_id = Column(String, ForeignKey("knowledge_bases.kb_id"))
    source_type = Column(Enum(KnowledgeSourceType), nullable=False)
    source_content = Column(Text)           # For TEXT type
    source_url = Column(String)             # For URL type
    file_path = Column(String)              # For FILE type
    file_name = Column(String)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)
    processed_chunks = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")

class KnowledgeSourceType(str, Enum):
    """Document source types"""
    TEXT = "text"
    FILE = "file"
    URL = "url"

class ProcessingStatus(str, Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
```

---

#### `backend/schemas/knowledge_base.py`
**Lines: 80 | Language: Python (Pydantic)**

**Purpose:** API request/response schemas

**Schemas:**

```python
class KnowledgeBaseCreate(BaseModel):
    """Create KB request"""
    agent_id: str
    name: str
    description: Optional[str] = None
    embedding_model: Optional[str] = "qwen3-embedding:0.6b"
    chunk_size: Optional[int] = 1000
    chunk_overlap: Optional[int] = 200

class KnowledgeDocumentCreate(BaseModel):
    """Create document request"""
    kb_id: str
    source_type: KnowledgeSourceType
    source_content: Optional[str] = None  # For TEXT
    source_url: Optional[str] = None      # For URL
    file_name: Optional[str] = None       # For FILE

class KnowledgeBaseQuery(BaseModel):
    """Query KB request"""
    kb_id: str
    query: str
    top_k: Optional[int] = 5

class KnowledgeBaseQueryResult(BaseModel):
    """Query response"""
    results: List[dict]
    query: str
    kb_id: str
```

---

## 🔄 How Files Interact

### Upload Flow
```
AgentBuilder.tsx (Frontend)
    ↓ HTTP POST
knowledge_base.py (API)
    ↓ Call service method
knowledge_base_service.py
    ├→ Save metadata to SQLite (knowledge_base.py model)
    ├→ Generate embeddings via Ollama
    └→ Store vectors in Qdrant (/tmp/qdrant_kb/)
```

### Chat Flow
```
AgentChat.tsx (Frontend)
    ↓ HTTP POST /agents/{id}/chat
agents.py (API)
    ↓ Call service
agent_service.py
    ↓ Retrieve KB context
knowledge_base_service.py
    ├→ Query SQLite for KBs
    ├→ Generate query embedding via Ollama
    ├→ Search Qdrant for similar chunks
    └→ Return formatted context
        ↓
agent_service.py
    ├→ Build LLM prompt with KB context
    └→ Call LLM and return response
```

---

## 📊 Data Storage Locations

```
/tmp/qdrant_kb/                        # Qdrant vector storage (KB)
├── collection/
│   └── kb_abc123ab_test_xyz/
│       ├── meta.json                  # Collection config
│       ├── segments/                  # Vector data
│       └── payload/                   # Chunk text + metadata

/tmp/qdrant/                           # Qdrant vector storage (Mem0)
├── collection/
│   └── agent_memories/

/tmp/knowledge_base_uploads/           # Uploaded files
├── abc123_filename.pdf
└── def456_document.docx

backend/agents.db                      # SQLite database
├── knowledge_bases table
└── knowledge_documents table
```

---

## 🔧 Configuration Files

**Environment Variables:**
```bash
# backend/.env
GROQ_API_KEY=gsk_xxx         # For LLM
OPENAI_API_KEY=sk-xxx        # Alternative LLM
ANTHROPIC_API_KEY=sk-ant-xxx # Alternative LLM
```

**Dependencies:**
```
backend/requirements.txt:
- qdrant-client           # Vector DB
- ollama                  # Embeddings
- langchain-community     # Document loaders
- langchain-text-splitters # Chunking
- beautifulsoup4          # HTML parsing
- pypdf                   # PDF loading
- docx2txt                # DOCX loading
```

---

This file map should help you navigate the codebase and understand which file does what! 🗺️
