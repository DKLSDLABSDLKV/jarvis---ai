"""
Encryption Module for Secure Intelligent Desktop Assistant
Data encryption for stored information
"""

import base64
import hashlib
import os
import json
import logging
from pathlib import Path
import sys

# Import config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class DataEncryptor:
    """
    Data Encryption System
    Provides encryption for sensitive data
    """
    
    def __init__(self, key=None):
        """
        Initialize encryptor
        
        Args:
            key: Encryption key (generated if not provided)
        """
        self.logger = logging.getLogger('DesktopAssistant.Encryption')
        self.key = key or self._generate_key()
        
        self.logger.info("Data Encryptor initialized")
    
    def _generate_key(self):
        """Generate encryption key"""
        # Use a fixed key based on machine info for simplicity
        # In production, use proper key management
        key = hashlib.sha256(b"DesktopAssistantSecureKey2024").digest()
        return base64.urlsafe_b64encode(key)
    
    def _pad_data(self, data):
        """Pad data for encryption"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Add padding
        padding = 16 - (len(data) % 16)
        data += bytes([padding] * padding)
        
        return data
    
    def _unpad_data(self, data):
        """Remove padding from decrypted data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Remove padding
        padding = data[-1]
        return data[:-padding]
    
    def encrypt(self, data):
        """
        Encrypt data
        
        Args:
            data: Data to encrypt (string or dict)
            
        Returns:
            Base64 encoded encrypted string
        """
        try:
            # Convert to JSON if dict
            if isinstance(data, dict):
                data = json.dumps(data)
            
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Simple XOR encryption for demonstration
            # In production, use cryptography library with proper AES
            key_bytes = self.key[:len(data)]
            
            encrypted = bytearray()
            for i, byte in enumerate(data):
                key_byte = key_bytes[i % len(key_bytes)]
                encrypted.append(byte ^ key_byte)
            
            return base64.b64encode(bytes(encrypted)).decode('utf-8')
        
        except Exception as e:
            self.logger.error(f"Encryption error: {e}")
            return None
    
    def decrypt(self, encrypted_data):
        """
        Decrypt data
        
        Args:
            encrypted_data: Base64 encoded encrypted string
            
        Returns:
            Decrypted string or dict
        """
        try:
            # Decode base64
            encrypted = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Decrypt using XOR
            key_bytes = self.key
            
            decrypted = bytearray()
            for i, byte in enumerate(encrypted):
                key_byte = key_bytes[i % len(key_bytes)]
                decrypted.append(byte ^ key_byte)
            
            # Remove padding
            result = self._unpad_data(bytes(decrypted))
            
            # Try to parse as JSON
            try:
                return json.loads(result.decode('utf-8'))
            except:
                return result.decode('utf-8')
        
        except Exception as e:
            self.logger.error(f"Decryption error: {e}")
            return None
    
    def encrypt_file(self, file_path, output_path=None):
        """
        Encrypt a file
        
        Args:
            file_path: Path to file
            output_path: Output path (optional)
            
        Returns:
            True if successful
        """
        try:
            # Read file
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Encrypt
            encrypted = self.encrypt(data)
            
            # Write to output
            if output_path is None:
                output_path = file_path + '.encrypted'
            
            with open(output_path, 'w') as f:
                f.write(encrypted)
            
            self.logger.info(f"Encrypted file: {file_path} -> {output_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"File encryption error: {e}")
            return False
    
    def decrypt_file(self, encrypted_path, output_path=None):
        """
        Decrypt a file
        
        Args:
            encrypted_path: Path to encrypted file
            output_path: Output path (optional)
            
        Returns:
            True if successful
        """
        try:
            # Read encrypted file
            with open(encrypted_path, 'r') as f:
                encrypted_data = f.read()
            
            # Decrypt
            decrypted = self.decrypt(encrypted_data)
            
            if decrypted is None:
                return False
            
            # Write to output
            if output_path is None:
                if encrypted_path.endswith('.encrypted'):
                    output_path = encrypted_path[:-10]
                else:
                    output_path = encrypted_path + '.decrypted'
            
            with open(output_path, 'wb') as f:
                if isinstance(decrypted, str):
                    f.write(decrypted.encode('utf-8'))
                else:
                    f.write(decrypted)
            
            self.logger.info(f"Decrypted file: {encrypted_path} -> {output_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"File decryption error: {e}")
            return False
    
    def hash_password(self, password):
        """
        Hash password
        
        Args:
            password: Password to hash
            
        Returns:
            Hashed password string
        """
        # Use SHA-256 with salt
        salt = b"DesktopAssistantSalt"
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return base64.b64encode(hashed).decode('utf-8')
    
    def verify_password(self, password, hashed):
        """
        Verify password against hash
        
        Args:
            password: Password to verify
            hashed: Hashed password
            
        Returns:
            True if password matches
        """
        return self.hash_password(password) == hashed
    
    def encrypt_dict(self, data):
        """
        Encrypt dictionary
        
        Args:
            data: Dictionary to encrypt
            
        Returns:
            Encrypted string
        """
        return self.encrypt(data)
    
    def decrypt_dict(self, encrypted_data):
        """
        Decrypt to dictionary
        
        Args:
            encrypted_data: Encrypted string
            
        Returns:
            Decrypted dictionary
        """
        return self.decrypt(encrypted_data)
    
    def encrypt_credentials(self, credentials):
        """
        Encrypt credentials
        
        Args:
            credentials: Dict of credentials
            
        Returns:
            Encrypted string
        """
        return self.encrypt(credentials)
    
    def decrypt_credentials(self, encrypted_data):
        """
        Decrypt credentials
        
        Args:
            encrypted_data: Encrypted string
            
        Returns:
            Decrypted credentials dict
        """
        return self.decrypt(encrypted_data)


# ============================================
# Main function for testing
# ============================================

def test_encryption():
    """Test encryption"""
    print("Testing Encryption...")
    
    encryptor = DataEncryptor()
    
    # Test string encryption
    print("\n" + "="*60)
    print("Testing String Encryption:")
    print("="*60)
    
    test_string = "Hello, this is a secret message!"
    
    print(f"Original: {test_string}")
    
    encrypted = encryptor.encrypt(test_string)
    print(f"Encrypted: {encrypted}")
    
    decrypted = encryptor.encrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    
    # Test dictionary encryption
    print("\n" + "="*60)
    print("Testing Dictionary Encryption:")
    print("="*60)
    
    test_dict = {
        "username": "admin",
        "password": "secret123",
        "api_key": "sk-1234567890"
    }
    
    print(f"Original: {test_dict}")
    
    encrypted_dict = encryptor.encrypt_dict(test_dict)
    print(f"Encrypted: {encrypted_dict}")
    
    decrypted_dict = encryptor.decrypt_dict(encrypted_dict)
    print(f"Decrypted: {decrypted_dict}")
    
    # Test password hashing
    print("\n" + "="*60)
    print("Testing Password Hashing:")
    print("="*60)
    
    password = "mySecurePassword123"
    hashed = encryptor.hash_password(password)
    print(f"Password: {password}")
    print(f"Hashed: {hashed}")
    print(f"Verified: {encryptor.verify_password(password, hashed)}")
    print(f"Wrong password: {encryptor.verify_password('wrong', hashed)}")
    
    return encryptor


if __name__ == "__main__":
    test_encryption()
