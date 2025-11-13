"""
Credentials API Endpoints
Handles secure storage and management of API keys, tokens, and connection credentials
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from core.database import get_db
from models.workflow import Credential
from schemas.workflow import CredentialCreate, CredentialUpdate, CredentialResponse
from services.credentials_service import CredentialsService

router = APIRouter()


@router.post("/", response_model=CredentialResponse, status_code=status.HTTP_201_CREATED)
async def create_credential(
    credential_data: CredentialCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new credential
    
    Securely stores API keys, tokens, and connection credentials with encryption
    """
    service = CredentialsService(db)
    try:
        credential = await service.create_credential(credential_data)
        return credential
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create credential: {str(e)}")


@router.get("/", response_model=List[CredentialResponse])
async def list_credentials(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all credentials
    
    Returns list of credentials with masked sensitive fields
    """
    service = CredentialsService(db)
    try:
        credentials = await service.list_credentials(skip=skip, limit=limit)
        return credentials
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list credentials: {str(e)}")


@router.get("/{credential_id}", response_model=CredentialResponse)
async def get_credential(
    credential_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific credential by ID
    
    Returns credential with masked sensitive fields
    """
    service = CredentialsService(db)
    try:
        credential = await service.get_credential(credential_id)
        if not credential:
            raise HTTPException(status_code=404, detail="Credential not found")
        return credential
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get credential: {str(e)}")


@router.put("/{credential_id}", response_model=CredentialResponse)
async def update_credential(
    credential_id: str,
    credential_data: CredentialUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a credential
    
    Updates credential data with proper encryption
    """
    service = CredentialsService(db)
    try:
        credential = await service.update_credential(credential_id, credential_data)
        if not credential:
            raise HTTPException(status_code=404, detail="Credential not found")
        return credential
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update credential: {str(e)}")


@router.delete("/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credential(
    credential_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a credential
    
    Permanently removes credential from storage
    """
    service = CredentialsService(db)
    try:
        success = await service.delete_credential(credential_id)
        if not success:
            raise HTTPException(status_code=404, detail="Credential not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete credential: {str(e)}")


@router.post("/{credential_id}/test", response_model=dict)
async def test_credential(
    credential_id: str,
    db: Session = Depends(get_db)
):
    """
    Test a credential connection
    
    Validates that the credential works with its target service
    """
    service = CredentialsService(db)
    try:
        result = await service.test_credential(credential_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test credential: {str(e)}")
