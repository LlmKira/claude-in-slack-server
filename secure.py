import os
import base64
from Cryptodome.Cipher import ChaCha20
import hashlib

# Read the encryption key from the environment variable
key_str = os.environ.get('ENCRYPTION_KEY')
key = hashlib.sha256(key_str.encode()).digest()


def encrypt_token(token):
    cipher = ChaCha20.new(key=key)
    nonce = cipher.nonce
    ciphertext = cipher.encrypt(token.encode('utf-8'))
    return base64.b64encode(nonce + ciphertext).decode('utf-8')


def decrypt_token(ciphertext):
    decoded_ciphertext = base64.b64decode(ciphertext.encode('utf-8'))
    nonce = decoded_ciphertext[:8]
    ciphertext = decoded_ciphertext[8:]
    cipher = ChaCha20.new(key=key, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext.decode('utf-8')
