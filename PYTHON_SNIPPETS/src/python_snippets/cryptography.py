

import json
from typing import Tuple, Optional
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    load_pem_private_key,
)
from cryptography.exceptions import InvalidSignature


def generate_keys() -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """
    Generate a pair of RSA keys - a private key and a corresponding public key.

    Returns:
        Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]: The generated private and public keys.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    public_key = private_key.public_key()

    return private_key, public_key


def serialize_public_key(public_key: rsa.RSAPublicKey) -> bytes:
    """
    Serialize a public key into a PEM-encoded byte string.

    Args:
        public_key (rsa.RSAPublicKey): The public key to serialize.

    Returns:
        bytes: The serialized public key in PEM format.
    """
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def serialize_private_key(
    private_key: rsa.RSAPrivateKey, encryption_password: bytes = b"Placeholder"
) -> bytes:
    """
    Serialize a private key into a PEM-encoded byte string.

    Args:
        private_key (rsa.RSAPrivateKey): The private key to serialize.
        encryption_password (bytes, optional): The password to use for encryption.

    Returns:
        bytes: The serialized private key in PEM format.
    """
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(encryption_password),
    )


def serialize_keys(
    private_key: rsa.RSAPrivateKey,
    public_key: Optional[rsa.RSAPublicKey] = None,
    encryption_password: bytes = b"Placeholder",
) -> Tuple[bytes, bytes]:
    """
    Serialize a pair of RSA keys into PEM-encoded byte strings.

    Args:
        private_key (rsa.RSAPrivateKey): The private key to serialize.
        public_key (rsa.RSAPublicKey, optional): The public key to serialize.
        encryption_password (bytes, optional): The password to use for encryption.

    Returns:
        Tuple[bytes, bytes]: The serialized private key and public key in PEM format.
    """
    public_key = public_key or private_key.public_key()
    private_bytes = serialize_private_key(private_key, encryption_password)
    public_bytes = serialize_public_key(public_key)

    return private_bytes, public_bytes


def deserialize_public_key(public_bytes: bytes) -> rsa.RSAPublicKey:
    """
    Deserialize a public key from a PEM-encoded byte string.

    Args:
        public_bytes (bytes): The PEM-encoded byte string representing the public key.

    Returns:
        rsa.RSAPublicKey: The deserialized public key.
    """
    return load_pem_public_key(public_bytes, backend=default_backend())


def deserialize_private_key(
    private_bytes: bytes, encryption_password: bytes = b"Placeholder"
) -> rsa.RSAPrivateKey:
    """
    Deserialize a private key from a PEM-encoded byte string with optional encryption password.

    Args:
        private_bytes (bytes): The PEM-encoded byte string representing the private key.
        encryption_password (bytes, optional): The password used for encryption.

    Returns:
        rsa.RSAPrivateKey: The deserialized private key.
    """
    return load_pem_private_key(
        private_bytes, password=encryption_password, backend=default_backend()
    )


def deserialize_keys(
    private_bytes: bytes,
    public_bytes: Optional[bytes] = None,
    encryption_password: bytes = b"Placeholder",
) -> Tuple[rsa.RSAPrivateKey, Optional[rsa.RSAPublicKey]]:
    """
    Deserialize a pair of RSA keys from PEM-encoded byte strings.

    Args:
        private_bytes (bytes): The PEM-encoded byte string representing the private key.
        public_bytes (bytes, optional): The PEM-encoded byte string representing the public key.
        encryption_password (bytes, optional): The password used for encryption.

    Returns:
        Tuple[rsa.RSAPrivateKey, Optional[rsa.RSAPublicKey]]: The deserialized private key and public key.
    """
    private_key = deserialize_private_key(private_bytes, encryption_password)
    public_key = deserialize_public_key(public_bytes) if public_bytes else None

    return private_key, public_key


def sign_data(data: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
    """
    Sign data using the given private key.

    Args:
        data (bytes): The data to be signed.
        private_key (rsa.RSAPrivateKey): The private key to use for signing.

    Returns:
        bytes: The signature of the data.
    """
    return private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )


def verify_signature(
    data: bytes, signature: bytes, public_key: rsa.RSAPublicKey
) -> bool:
    """
    Verify the signature of the given data using the given public key.

    Args:
        data (bytes): The data to be verified.
        signature (bytes): The signature of the data.
        public_key (rsa.RSAPublicKey): The public key to use for verification.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False


def sign_with_metadata(data: bytes, private_key: rsa.RSAPrivateKey, **kwargs) -> bytes:
    """
    Sign data with additional metadata using the provided private key.

    Args:
        data (bytes): The data to be signed.
        private_key (rsa.RSAPrivateKey): The private key to sign the data with.
        **kwargs: Additional keyword arguments representing metadata to include in the signature.

    Returns:
        bytes: The signature of the data with metadata.
    """
    # Construct a dictionary for metadata
    metadata = {}

    # Loop over the keyword arguments to collect metadata
    for key, value in kwargs.items():
        if callable(value):
            value = value()
        elif isinstance(value, tuple) and value and callable(value[0]):
            value = value[0](*value[1:])

        # You might want to perform type checks or serialization here
        metadata[key] = value

    raw = {
        "data": data,
        "metadata": metadata,
    }

    dumped = json.dumps(raw).encode("utf-8")

    return sign_data(dumped, private_key)


def verify_with_metadata(
    data: bytes, signature: bytes, public_key: rsa.RSAPublicKey, **kwargs
) -> bool:
    """
    Verify the signature of the given data with additional metadata using the provided public key.

    Args:
        data (bytes): The data to be verified.
        signature (bytes): The signature of the data.
        public_key (rsa.RSAPublicKey): The public key to use for verification.
        **kwargs: Additional keyword arguments representing metadata to verify against.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    # Construct a dictionary for metadata
    metadata = {}

    # Loop over the keyword arguments to collect metadata
    for key, value in kwargs.items():
        if callable(value):
            value = value()
        elif isinstance(value, tuple) and value and callable(value[0]):
            value = value[0](*value[1:])
        metadata[key] = value

    # Serialize the metadata and data as a byte string
    raw = {
        "data": data,
        "metadata": metadata,
    }
    dumped = json.dumps(raw).encode("utf-8")

    return verify_signature(dumped, signature, public_key)