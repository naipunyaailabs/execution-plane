from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models.knowledge_base import KnowledgeSourceType, ProcessingStatus

class KnowledgeBaseCreate(BaseModel):
    agent_id: str
    name: str
    description: Optional[str] = None
    embedding_model: Optional[str] = "qwen3-embedding:0.6b"
    chunk_size: Optional[int] = 1000
    chunk_overlap: Optional[int] = 200

class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None

class KnowledgeBaseInDB(BaseModel):
    kb_id: str
    agent_id: str
    name: str
    description: Optional[str] = None
    collection_name: str
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class KnowledgeDocumentCreate(BaseModel):
    kb_id: str
    source_type: KnowledgeSourceType
    source_content: Optional[str] = None
    source_url: Optional[str] = None
    file_name: Optional[str] = None

class KnowledgeDocumentInDB(BaseModel):
    doc_id: str
    kb_id: str
    source_type: KnowledgeSourceType
    source_content: Optional[str] = None
    source_url: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    chunk_count: int
    status: ProcessingStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class KnowledgeBaseQuery(BaseModel):
    query: str
    top_k: Optional[int] = 5

class KnowledgeBaseQueryResult(BaseModel):
    content: str
    score: float
    metadata: dict

class KnowledgeBaseWithDocuments(KnowledgeBaseInDB):
    documents: List[KnowledgeDocumentInDB] = []
