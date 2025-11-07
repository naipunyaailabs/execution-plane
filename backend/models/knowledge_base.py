from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class KnowledgeSourceType(str, enum.Enum):
    TEXT = "text"
    URL = "url"
    FILE = "file"

class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    
    id = Column(Integer, primary_key=True, index=True)
    kb_id = Column(String, unique=True, index=True)
    agent_id = Column(String, ForeignKey("agents.agent_id"), index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    collection_name = Column(String, unique=True, index=True)
    embedding_model = Column(String)
    chunk_size = Column(Integer, default=1000)
    chunk_overlap = Column(Integer, default=200)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, unique=True, index=True)
    kb_id = Column(String, ForeignKey("knowledge_bases.kb_id"), index=True)
    source_type = Column(SQLEnum(KnowledgeSourceType))
    source_content = Column(Text)
    source_url = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    chunk_count = Column(Integer, default=0)
    status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
