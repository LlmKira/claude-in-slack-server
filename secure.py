import os
import base64
from Cryptodome.Cipher import ChaCha20
import hashlib

# Read the encryption key from the environment variable
key_str = os.environ.get('ENCRYPTION_KEY')
key = hashlib.sha256(key_str.encode()).digest()


def encrypt_token(token):
    """Encrypts a user's access token"""
    cipher = ChaCha20.new(key=key)
    encrypted_token = cipher.encrypt(token.encode())
    return base64.urlsafe_b64encode(encrypted_token).decode()


def decrypt_token(encrypted_token):
    """Decrypts a user's access token"""
    cipher = ChaCha20.new(key=key)
    encrypted_token_bytes = base64.urlsafe_b64decode(encrypted_token.encode())
    decrypted_token = cipher.decrypt(encrypted_token_bytes)
    return decrypted_token.decode()
