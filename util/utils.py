from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.fernet import Fernet
import base64
import os

def generate_encryption_key_pair(secret: str) -> tuple[str, str]:
    # Generate RSA Key Pair
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # Serialize public key to PEM
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    # Serialize private key to PEM (unencrypted)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Encrypt the private key with symmetric key
    # Derive a Fernet key from the secret
    symmetric_key = base64.urlsafe_b64encode(secret.encode('utf-8')[:32].ljust(32, b'0'))  # 32 bytes
    fernet = Fernet(symmetric_key)
    encrypted_private_key = fernet.encrypt(private_pem).decode('utf-8')

    return public_pem, encrypted_private_key
