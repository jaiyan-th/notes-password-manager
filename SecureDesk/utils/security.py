"""
Security utilities for password encryption and secure operations
"""

import os
import secrets
import string
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class PasswordEncryption:
    """Handle password encryption and decryption for password entries"""
    
    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        """Derive encryption key from user password and salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    @staticmethod
    def encrypt_password(password: str, user_id: int) -> str:
        """
        Encrypt a password using user-specific key derivation
        
        Args:
            password: Plain text password to encrypt
            user_id: User ID for salt generation
            
        Returns:
            Base64 encoded encrypted password with salt
        """
        # Generate salt based on user_id for consistency
        salt = f"user_{user_id}_salt".encode()[:16].ljust(16, b'0')
        
        # Derive key from a master key and user-specific salt
        master_key = os.environ.get('MASTER_KEY', 'default-master-key-change-in-production')
        key = PasswordEncryption._derive_key(master_key, salt)
        
        # Create Fernet cipher
        fernet = Fernet(key)
        
        # Encrypt password
        encrypted_password = fernet.encrypt(password.encode())
        
        # Return base64 encoded result
        return base64.urlsafe_b64encode(encrypted_password).decode()
    
    @staticmethod
    def decrypt_password(encrypted_password: str, user_id: int) -> str:
        """
        Decrypt a password using user-specific key derivation
        
        Args:
            encrypted_password: Base64 encoded encrypted password
            user_id: User ID for salt generation
            
        Returns:
            Decrypted plain text password
        """
        try:
            # Generate same salt as encryption
            salt = f"user_{user_id}_salt".encode()[:16].ljust(16, b'0')
            
            # Derive same key
            master_key = os.environ.get('MASTER_KEY', 'default-master-key-change-in-production')
            key = PasswordEncryption._derive_key(master_key, salt)
            
            # Create Fernet cipher
            fernet = Fernet(key)
            
            # Decode and decrypt
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode())
            decrypted_password = fernet.decrypt(encrypted_bytes)
            
            return decrypted_password.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt password: {str(e)}")

class PasswordGenerator:
    """Generate secure passwords"""
    
    @staticmethod
    def generate_password(length: int = 16, include_symbols: bool = True) -> str:
        """
        Generate a secure random password
        
        Args:
            length: Password length (minimum 8)
            include_symbols: Whether to include special characters
            
        Returns:
            Generated password string
        """
        if length < 8:
            raise ValueError("Password length must be at least 8 characters")
        
        # Define character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?" if include_symbols else ""
        
        # Ensure at least one character from each required set
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits)
        ]
        
        if include_symbols:
            password.append(secrets.choice(symbols))
        
        # Fill remaining length with random characters from all sets
        all_chars = lowercase + uppercase + digits + symbols
        for _ in range(length - len(password)):
            password.append(secrets.choice(all_chars))
        
        # Shuffle the password list
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    @staticmethod
    def check_password_strength(password: str) -> dict:
        """
        Check password strength and return analysis
        
        Args:
            password: Password to analyze
            
        Returns:
            Dictionary with strength analysis
        """
        analysis = {
            'length': len(password),
            'has_lowercase': any(c.islower() for c in password),
            'has_uppercase': any(c.isupper() for c in password),
            'has_digits': any(c.isdigit() for c in password),
            'has_symbols': any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password),
            'score': 0,
            'strength': 'Very Weak'
        }
        
        # Calculate strength score
        if analysis['length'] >= 8:
            analysis['score'] += 1
        if analysis['length'] >= 12:
            analysis['score'] += 1
        if analysis['has_lowercase']:
            analysis['score'] += 1
        if analysis['has_uppercase']:
            analysis['score'] += 1
        if analysis['has_digits']:
            analysis['score'] += 1
        if analysis['has_symbols']:
            analysis['score'] += 1
        
        # Determine strength level
        if analysis['score'] >= 5:
            analysis['strength'] = 'Strong'
        elif analysis['score'] >= 4:
            analysis['strength'] = 'Good'
        elif analysis['score'] >= 3:
            analysis['strength'] = 'Fair'
        elif analysis['score'] >= 2:
            analysis['strength'] = 'Weak'
        
        return analysis

def generate_csrf_token() -> str:
    """Generate a secure CSRF token"""
    return secrets.token_urlsafe(32)

def secure_filename(filename: str) -> str:
    """
    Generate a secure filename by removing dangerous characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path components and dangerous characters
    filename = os.path.basename(filename)
    filename = ''.join(c for c in filename if c.isalnum() or c in '._-')
    
    # Ensure filename is not empty and not too long
    if not filename:
        filename = 'file'
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename