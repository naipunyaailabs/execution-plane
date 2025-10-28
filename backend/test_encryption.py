import hashlib
import base64
from cryptography.fernet import Fernet

def test_encryption():
    # Test encryption/decryption
    test_key = "test_api_key_12345"
    
    # Generate encryption key (same as in AgentService)
    key_source = b'default_secret_key_for_development_only'
    encryption_key = base64.urlsafe_b64encode(hashlib.sha256(key_source).digest())
    
    # Encrypt
    f = Fernet(encryption_key)
    encrypted = f.encrypt(test_key.encode()).decode()
    print(f"Encrypted: {encrypted}")
    
    # Decrypt
    decrypted = f.decrypt(encrypted.encode()).decode()
    print(f"Decrypted: {decrypted}")
    
    # Verify
    assert decrypted == test_key
    print("Encryption/decryption test passed!")

if __name__ == "__main__":
    test_encryption()