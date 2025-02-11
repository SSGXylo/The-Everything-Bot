"""
Encryption utilities for sensitive data.
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
from typing import Any, Union
from ..config import ENCRYPTION_KEY

class Encryptor:
    """Handles encryption and decryption of sensitive data."""
    
    def __init__(self):
        """Initialize the encryptor with the encryption key."""
        # Generate a key from the encryption key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'ticket_bot_salt',  # Constant salt is fine for this use case
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(ENCRYPTION_KEY.encode()))
        self._fernet = Fernet(key)
    
    def encrypt_data(self, data: Union[str, dict, list]) -> str:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt
            
        Returns:
            str: Encrypted data as a string
        """
        if isinstance(data, (dict, list)):
            data = json.dumps(data)
        encrypted = self._fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data: str) -> Any:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Encrypted data to decrypt
            
        Returns:
            Any: Decrypted data
        """
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self._fernet.decrypt(decoded)
            try:
                # Try to parse as JSON
                return json.loads(decrypted)
            except json.JSONDecodeError:
                # Return as string if not JSON
                return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {e}")

# Global encryptor instance
encryptor = Encryptor()
