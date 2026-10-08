"""
Enterprise Security Layer
Encryption, API key management, auth, rate limiting
"""

from typing import Optional, Dict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os
import secrets
from datetime import datetime, timedelta
import jwt
from utils.logger import logger
from config.settings import DEBUG
import hashlib


class EncryptionManager:
    """Handles encryption/decryption of sensitive data"""
    
    def __init__(self):
        # Get master encryption key from environment or generate
        master_key = os.getenv("MASTER_ENCRYPTION_KEY")
        if not master_key:
            if DEBUG:
                logger.warning("No MASTER_ENCRYPTION_KEY set. Using development key.")
                master_key = Fernet.generate_key().decode()
            else:
                raise ValueError("MASTER_ENCRYPTION_KEY required in production")
        
        self.cipher = Fernet(master_key.encode() if isinstance(master_key, str) else master_key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        encrypted = self.cipher.encrypt(data.encode())
        return encrypted.decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()


class APIKeyManager:
    """Secure API key storage and management"""
    
    def __init__(self):
        self.encryption_manager = EncryptionManager()
        self.rate_limits: Dict[str, list] = {}
    
    def secure_store_key(self, user_id: str, key_type: str, key_value: str) -> str:
        """Securely store API key"""
        
        try:
            encrypted_key = self.encryption_manager.encrypt(key_value)
            logger.info(f"API key stored securely for user {user_id}")
            return encrypted_key
        except Exception as e:
            logger.error(f"Error storing API key: {str(e)}")
            raise
    
    def retrieve_key(self, user_id: str, encrypted_key: str) -> str:
        """Retrieve and decrypt API key"""
        
        try:
            decrypted_key = self.encryption_manager.decrypt(encrypted_key)
            logger.info(f"API key retrieved for user {user_id}")
            return decrypted_key
        except Exception as e:
            logger.error(f"Error retrieving API key: {str(e)}")
            raise ValueError("Failed to decrypt API key")
    
    def rotate_key(self, old_encrypted_key: str, new_key_value: str) -> str:
        """Rotate API key to new value"""
        
        try:
            # Verify old key works
            self.encryption_manager.decrypt(old_encrypted_key)
            
            # Store new key
            new_encrypted = self.encryption_manager.encrypt(new_key_value)
            
            logger.info("API key rotated successfully")
            return new_encrypted
        except Exception as e:
            logger.error(f"Error rotating API key: {str(e)}")
            raise


class AuthenticationManager:
    """JWT-based authentication"""
    
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
        self.algorithm = "HS256"
        self.token_expiry = 24  # hours
    
    def create_token(self, user_id: str, email: str) -> str:
        """Create JWT authentication token"""
        
        try:
            payload = {
                "user_id": user_id,
                "email": email,
                "exp": datetime.utcnow() + timedelta(hours=self.token_expiry),
                "iat": datetime.utcnow()
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Token created for user {user_id}")
            
            return token
        except Exception as e:
            logger.error(f"Error creating token: {str(e)}")
            raise
    
    def verify_token(self, token: str) -> Dict:
        """Verify and decode JWT token"""
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.error("Token expired")
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            logger.error("Invalid token")
            raise ValueError("Invalid token")
    
    def refresh_token(self, old_token: str) -> str:
        """Refresh expiring token"""
        
        try:
            payload = self.verify_token(old_token)
            # Remove old timestamps
            payload.pop("exp", None)
            payload.pop("iat", None)
            
            # Create new token
            return self.create_token(payload["user_id"], payload["email"])
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            raise


class RateLimiter:
    """Request rate limiting"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, user_id: str) -> bool:
        """Check if user can make request"""
        
        now = datetime.utcnow()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Remove old requests outside window
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if (now - req_time).seconds < self.window_seconds
        ]
        
        # Check limit
        if len(self.requests[user_id]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return False
        
        # Record new request
        self.requests[user_id].append(now)
        return True
    
    def get_remaining(self, user_id: str) -> int:
        """Get remaining requests for user"""
        
        if user_id not in self.requests:
            return self.max_requests
        
        now = datetime.utcnow()
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if (now - req_time).seconds < self.window_seconds
        ]
        
        return max(0, self.max_requests - len(self.requests[user_id]))


class SecureFileManager:
    """Secure file upload and storage"""
    
    ALLOWED_EXTENSIONS = {
        'video': {'mp4', 'mov', 'avi', 'mkv'},
        'audio': {'mp3', 'wav', 'aac', 'm4a'},
        'image': {'jpg', 'jpeg', 'png', 'webp'},
        'document': {'pdf', 'txt', 'json'}
    }
    
    MAX_FILE_SIZES = {
        'video': 5 * 1024 * 1024 * 1024,  # 5GB
        'audio': 500 * 1024 * 1024,  # 500MB
        'image': 50 * 1024 * 1024,  # 50MB
        'document': 10 * 1024 * 1024  # 10MB
    }
    
    @staticmethod
    def validate_upload(filename: str, file_type: str, file_size: int) -> bool:
        """Validate file upload"""
        
        try:
            # Check file extension
            ext = filename.rsplit('.', 1)[-1].lower()
            allowed = SecureFileManager.ALLOWED_EXTENSIONS.get(file_type, set())
            
            if ext not in allowed:
                logger.warning(f"Invalid file type: {ext}")
                return False
            
            # Check file size
            max_size = SecureFileManager.MAX_FILE_SIZES.get(file_type, 100 * 1024 * 1024)
            if file_size > max_size:
                logger.warning(f"File size exceeds limit: {file_size}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating upload: {str(e)}")
            return False
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Remove dangerous characters from filename"""
        
        # Keep only alphanumeric, dash, underscore, dot
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Limit length
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        name = name[:100]
        
        return f"{name}.{ext}" if ext else name
    
    @staticmethod
    def generate_file_hash(file_data: bytes) -> str:
        """Generate hash of file for integrity checking"""
        
        return hashlib.sha256(file_data).hexdigest()


class ComplianceManager:
    """Handle GDPR, privacy, and compliance"""
    
    @staticmethod
    def mask_sensitive_data(data: Dict) -> Dict:
        """Mask sensitive fields in logs/outputs"""
        
        sensitive_fields = [
            'api_key', 'token', 'password', 'secret',
            'credentials', 'access_token', 'refresh_token'
        ]
        
        masked_data = data.copy()
        
        for field in sensitive_fields:
            if field in masked_data:
                value = str(masked_data[field])
                if len(value) > 4:
                    masked_data[field] = f"***{value[-4:]}"
                else:
                    masked_data[field] = "***"
        
        return masked_data
    
    @staticmethod
    def log_access(user_id: str, action: str, resource: str,
                   granted: bool, reason: str = ""):
        """Log access attempts for audit trail"""
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "granted": granted,
            "reason": reason
        }
        
        logger.info(f"Access log: {log_entry}")


# Global instances
encryption_manager = EncryptionManager()
api_key_manager = APIKeyManager()
auth_manager = AuthenticationManager()
rate_limiter = RateLimiter()
compliance_manager = ComplianceManager()
