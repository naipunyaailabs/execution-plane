from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import uuid

from core.database import get_db
from schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseInDB,
    KnowledgeBaseUpdate,
    KnowledgeDocumentCreate,
    KnowledgeDocumentInDB,
    KnowledgeBaseQuery,
    KnowledgeBaseQueryResult,
    KnowledgeBaseWithDocuments
)
from services.knowledge_base_service import KnowledgeBaseService
from models.knowledge_base import KnowledgeSourceType

router = APIRouter()

@router.post("/", response_model=KnowledgeBaseInDB)
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    db: Session = Depends(get_db)
):
    kb_service = KnowledgeBaseService(db)
    try:
        kb = await kb_service.create_knowledge_base(kb_data)
        return kb
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{kb_id}", response_model=KnowledgeBaseWithDocuments)
async def get_knowledge_base(
    kb_id: str,
    db: Session = Depends(get_db)
):
    kb_service = KnowledgeBaseService(db)
    kb = await kb_service.get_knowledge_base(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    documents = await kb_service.get_documents(kb_id)
    
    return KnowledgeBaseWithDocuments(
        **kb.__dict__,
        documents=[KnowledgeDocumentInDB.model_validate(doc) for doc in documents]
    )

@router.get("/agent/{agent_id}", response_model=List[KnowledgeBaseInDB])
async def get_agent_knowledge_bases(
    agent_id: str,
    db: Session = Depends(get_db)
):
    kb_service = KnowledgeBaseService(db)
    kbs = await kb_service.get_knowledge_bases_by_agent(agent_id)
    return kbs

@router.delete("/{kb_id}")
async def delete_knowledge_base(
    kb_id: str,
    db: Session = Depends(get_db)
):
    kb_service = KnowledgeBaseService(db)
    success = await kb_service.delete_knowledge_base(kb_id)
    if not success:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return {"message": "Knowledge base deleted successfully"}

@router.post("/{kb_id}/documents/text", response_model=KnowledgeDocumentInDB)
async def add_text_document(
    kb_id: str,
    text: str = Form(...),
    db: Session = Depends(get_db)
):
    kb_service = KnowledgeBaseService(db)
    
    doc_data = KnowledgeDocumentCreate(
        kb_id=kb_id,
        source_type=KnowledgeSourceType.TEXT,
        source_content=text
    )
    
    try:
        doc = await kb_service.add_document(doc_data)
        return doc
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{kb_id}/documents/url", response_model=KnowledgeDocumentInDB)
async def add_url_document(
    kb_id: str,
    url: str = Form(...),
    db: Session = Depends(get_db)
):
    kb_service = KnowledgeBaseService(db)
    
    doc_data = KnowledgeDocumentCreate(
        kb_id=kb_id,
        source_type=KnowledgeSourceType.URL,
        source_url=url
    )
    
    try:
        doc = await kb_service.add_document(doc_data)
        return doc
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{kb_id}/documents/file", response_model=KnowledgeDocumentInDB)
async def add_file_document(
    kb_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    kb_service = KnowledgeBaseService(db)
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = ['.pdf', '.docx', '.txt', '.md', '.html', '.htm']
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    file_id = str(uuid.uuid4())
    file_path = os.path.join(kb_service.upload_dir, f"{file_id}{file_ext}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    doc_data = KnowledgeDocumentCreate(
        kb_id=kb_id,
        source_type=KnowledgeSourceType.FILE,
        file_name=file.filename
    )
    
    try:
        doc = await kb_service.add_document(doc_data, process_immediately=False)
        doc.file_path = file_path
        kb_service.db.commit()
        kb = await kb_service.get_knowledge_base(kb_id)
        await kb_service._process_document(doc, kb)
        return doc
    except ValueError as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{kb_id}/query", response_model=List[KnowledgeBaseQueryResult])
async def query_knowledge_base(
    kb_id: str,
    query_data: KnowledgeBaseQuery,
    db: Session = Depends(get_db)
):
    kb_service = KnowledgeBaseService(db)
    
    try:
        results = await kb_service.query_knowledge_base(kb_id, query_data)
        return results
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    db: Session = Depends(get_db)
):
    kb_service = KnowledgeBaseService(db)
    success = await kb_service.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}

@router.get("/{kb_id}/documents", response_model=List[KnowledgeDocumentInDB])
async def get_knowledge_base_documents(
    kb_id: str,
    db: Session = Depends(get_db)
):
    kb_service = KnowledgeBaseService(db)
    documents = await kb_service.get_documents(kb_id)
    return documents
