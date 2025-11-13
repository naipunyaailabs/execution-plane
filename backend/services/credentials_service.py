"""
Credentials Service
Handles secure storage, encryption, and management of API keys and credentials
"""
import uuid
import json
import base64
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

from models.workflow import Credential
from schemas.workflow import CredentialCreate, CredentialUpdate
from core.config import settings

logger = logging.getLogger(__name__)


class CredentialsService:
    """Service for managing encrypted credentials"""
    
    def __init__(self, db: Session):
        self.db = db
        self.encryption_key = self._get_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        
    def _get_encryption_key(self) -> bytes:
        """
        Get or generate encryption key for credentials
        In production, this should be stored securely (e.g., AWS Secrets Manager)
        """
        # Try to get from environment
        key_string = os.getenv("CREDENTIALS_ENCRYPTION_KEY")
        
        if not key_string:
            # Generate a key from a password (in production, use a secure secret)
            password = getattr(settings, 'SECRET_KEY', 'default-secret-key-change-in-production').encode()
            salt = b'credential_encryption_salt'  # In production, use a random salt stored securely
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            return key
        
        return key_string.encode()
    
    def _encrypt_data(self, data: Dict[str, Any]) -> str:
        """Encrypt sensitive credential data"""
        try:
            json_data = json.dumps(data)
            encrypted = self.fernet.encrypt(json_data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise ValueError("Failed to encrypt credential data")
    
    def _decrypt_data(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt credential data"""
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(decoded)
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise ValueError("Failed to decrypt credential data")
    
    def _mask_sensitive_fields(self, credential_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive fields based on credential type"""
        masked_data = data.copy()
        
        # Fields to mask based on type
        sensitive_fields = {
            "api_key": ["api_key", "api_secret"],
            "oauth2": ["client_secret", "access_token", "refresh_token"],
            "basic_auth": ["password"],
            "database": ["password"],
            "smtp": ["password"],
            "aws": ["secret_access_key"]
        }
        
        fields_to_mask = sensitive_fields.get(credential_type, [])
        
        for field in fields_to_mask:
            if field in masked_data and masked_data[field]:
                # Show first 4 and last 4 characters
                value = str(masked_data[field])
                if len(value) > 8:
                    masked_data[field] = f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"
                else:
                    masked_data[field] = '*' * len(value)
        
        return masked_data
    
    async def create_credential(self, credential_data: CredentialCreate, tenant_id: Optional[str] = None) -> dict:
        """Create a new encrypted credential"""
        credential_id = str(uuid.uuid4())
        
        # Encrypt the credential data
        encrypted_data = self._encrypt_data(credential_data.data)
        
        db_credential = Credential(
            credential_id=credential_id,
            name=credential_data.name,
            type=credential_data.type,
            data={"encrypted": encrypted_data},  # Store encrypted string
            tenant_id=tenant_id
        )
        
        self.db.add(db_credential)
        self.db.commit()
        self.db.refresh(db_credential)
        
        # Return with masked data
        decrypted_data = self._decrypt_data(encrypted_data)
        masked_data = self._mask_sensitive_fields(credential_data.type, decrypted_data)
        
        return {
            "id": db_credential.credential_id,
            "name": db_credential.name,
            "type": db_credential.type,
            "data": masked_data,
            "createdAt": db_credential.created_at,
            "updatedAt": db_credential.updated_at
        }
    
    async def get_credential(self, credential_id: str, mask_sensitive: bool = True) -> Optional[dict]:
        """Get a credential by ID"""
        db_credential = self.db.query(Credential).filter(
            Credential.credential_id == credential_id
        ).first()
        
        if not db_credential:
            return None
        
        # Decrypt data
        encrypted_data = db_credential.data.get("encrypted")
        decrypted_data = self._decrypt_data(encrypted_data)
        
        # Mask sensitive fields if requested
        if mask_sensitive:
            decrypted_data = self._mask_sensitive_fields(db_credential.type, decrypted_data)
        
        return {
            "id": db_credential.credential_id,
            "name": db_credential.name,
            "type": db_credential.type,
            "data": decrypted_data,
            "createdAt": db_credential.created_at,
            "updatedAt": db_credential.updated_at
        }
    
    async def get_credential_for_use(self, credential_id: str) -> Optional[Dict[str, Any]]:
        """Get unmasked credential data for actual use in workflows"""
        return await self.get_credential(credential_id, mask_sensitive=False)
    
    async def list_credentials(self, skip: int = 0, limit: int = 100, tenant_id: Optional[str] = None) -> List[dict]:
        """List all credentials with masked sensitive fields"""
        query = self.db.query(Credential)
        
        if tenant_id:
            query = query.filter(Credential.tenant_id == tenant_id)
        
        db_credentials = query.offset(skip).limit(limit).all()
        
        credentials = []
        for db_cred in db_credentials:
            encrypted_data = db_cred.data.get("encrypted")
            decrypted_data = self._decrypt_data(encrypted_data)
            masked_data = self._mask_sensitive_fields(db_cred.type, decrypted_data)
            
            credentials.append({
                "id": db_cred.credential_id,
                "name": db_cred.name,
                "type": db_cred.type,
                "data": masked_data,
                "createdAt": db_cred.created_at,
                "updatedAt": db_cred.updated_at
            })
        
        return credentials
    
    async def update_credential(self, credential_id: str, credential_data: CredentialUpdate) -> Optional[dict]:
        """Update a credential"""
        db_credential = self.db.query(Credential).filter(
            Credential.credential_id == credential_id
        ).first()
        
        if not db_credential:
            return None
        
        # Update fields
        if credential_data.name is not None:
            db_credential.name = credential_data.name
        
        if credential_data.type is not None:
            db_credential.type = credential_data.type
        
        if credential_data.data is not None:
            # Encrypt new data
            encrypted_data = self._encrypt_data(credential_data.data)
            db_credential.data = {"encrypted": encrypted_data}
        
        db_credential.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_credential)
        
        # Return with masked data
        encrypted_data = db_credential.data.get("encrypted")
        decrypted_data = self._decrypt_data(encrypted_data)
        masked_data = self._mask_sensitive_fields(db_credential.type, decrypted_data)
        
        return {
            "id": db_credential.credential_id,
            "name": db_credential.name,
            "type": db_credential.type,
            "data": masked_data,
            "createdAt": db_credential.created_at,
            "updatedAt": db_credential.updated_at
        }
    
    async def delete_credential(self, credential_id: str) -> bool:
        """Delete a credential"""
        db_credential = self.db.query(Credential).filter(
            Credential.credential_id == credential_id
        ).first()
        
        if not db_credential:
            return False
        
        self.db.delete(db_credential)
        self.db.commit()
        return True
    
    async def test_credential(self, credential_id: str) -> dict:
        """Test if a credential is valid"""
        credential = await self.get_credential_for_use(credential_id)
        
        if not credential:
            return {"success": False, "message": "Credential not found"}
        
        credential_type = credential["type"]
        credential_data = credential["data"]
        
        # Basic validation based on type
        required_fields = {
            "api_key": ["api_key"],
            "oauth2": ["client_id", "client_secret"],
            "basic_auth": ["username", "password"],
            "database": ["host", "port", "database", "username", "password"],
            "smtp": ["host", "port", "username", "password"],
            "aws": ["access_key_id", "secret_access_key", "region"]
        }
        
        required = required_fields.get(credential_type, [])
        missing = [field for field in required if field not in credential_data or not credential_data[field]]
        
        if missing:
            return {
                "success": False,
                "message": f"Missing required fields: {', '.join(missing)}"
            }
        
        # In a real implementation, you would actually test the credential
        # For now, just validate structure
        return {
            "success": True,
            "message": "Credential structure is valid",
            "type": credential_type
        }
