import os
import hashlib
import base64

from cryptography.exceptions import InvalidSignature
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from fastapi import HTTPException

from config.constants.keys import Keys
from util.logger import logger


def generate_encryption_key_pair() -> tuple[str, str]:
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
    symmetric_key = base64.urlsafe_b64encode(Keys.RSA_PAIR_SECRET.encode('utf-8')[:32].ljust(32, b'0'))  # 32 bytes
    fernet = Fernet(symmetric_key)
    encrypted_private_key = fernet.encrypt(private_pem).decode('utf-8')

    return public_pem, encrypted_private_key


def encrypt_data(plaintext: bytes, rsa_public_key_pem: str) -> bytes:
    # 1. Load RSA public key
    public_key = serialization.load_pem_public_key(rsa_public_key_pem.encode())

    # 2. Generate AES key and IV
    aes_key = os.urandom(32)  # 256-bit AES key
    iv = os.urandom(12)  # GCM standard IV size

    # 3. Encrypt data using AES-GCM
    encryptor = Cipher(
        algorithms.AES(aes_key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    tag = encryptor.tag  # 16 bytes

    # 4. Encrypt AES key using RSA
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 5. Bundle and return
    return (
            encrypted_aes_key + Keys.AES_RSA_SEPARATOR +
            iv + Keys.AES_RSA_SEPARATOR +
            tag + Keys.AES_RSA_SEPARATOR +
            ciphertext
    )


def sign_data(data: bytes, private_key_pem: str) -> bytes:
    private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
    return private_key.sign(
        data,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )


def compute_sha256sum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_public_key(pem_str: str):
    key = serialization.load_pem_public_key(pem_str.encode())
    return key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def decrypt_private_key(encrypted_private_key: str) -> str:
    # Re-derive Fernet key from shared secret
    symmetric_key = base64.urlsafe_b64encode(Keys.RSA_PAIR_SECRET.encode('utf-8')[:32].ljust(32, b'0'))
    fernet = Fernet(symmetric_key)

    decrypted_bytes = fernet.decrypt(encrypted_private_key.encode())
    return decrypted_bytes.decode('utf-8')  # PEM-formatted private key


def decrypt_data(blob: bytes, enc_priv: str, org_pub_pem: str) -> bytes:
    # 1. Split signature / encrypted payload
    sig, encrypted_payload = blob.split(Keys.SIGNATURE_SEPARATOR, 1)

    # 2. Split AES‑RSA bundle
    encrypted_aes_key, iv, tag, ciphertext = encrypted_payload.split(Keys.AES_RSA_SEPARATOR)

    # 3. Decrypt the owner’s private key (PEM) using your Fernet helper
    private_pem_str = decrypt_private_key(enc_priv)
    private_key = serialization.load_pem_private_key(
        private_pem_str.encode('utf-8'),
        password=None
    )

    # 4. RSA‑decrypt the AES key
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 5. AES‑GCM decrypt the ciphertext
    decrypt = Cipher(
        algorithms.AES(aes_key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()
    plaintext = decrypt.update(ciphertext) + decrypt.finalize()

    # 6. Verify the issuer’s signature
    org_public = serialization.load_pem_public_key(org_pub_pem.encode('utf-8'))
    org_public.verify(
        sig,
        plaintext,
        padding.PSS(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return plaintext