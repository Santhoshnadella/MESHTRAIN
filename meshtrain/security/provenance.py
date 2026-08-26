import hashlib
import json
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

class ModelVerifier:
    """
    MeshProtect V13: Verifies the cryptographic provenance of AI models.
    Ensures that downloaded model weights or configurations haven't been tampered with
    and originate from a trusted author.
    """
    
    @staticmethod
    def generate_keypair():
        """Generates a new Ed25519 keypair for model signing."""
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        priv_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        pub_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return priv_bytes, pub_bytes

    @staticmethod
    def sign_model_hash(model_hash: str, private_key_bytes: bytes) -> str:
        """Signs a model hash (e.g., SHA256 of weights) with the author's private key."""
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
        signature = private_key.sign(model_hash.encode('utf-8'))
        return base64.b64encode(signature).decode('utf-8')

    @staticmethod
    def verify_model(model_hash: str, signature_b64: str, public_key_bytes: bytes) -> bool:
        """Verifies that the model hash matches the provided signature from the author."""
        try:
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            signature = base64.b64decode(signature_b64)
            public_key.verify(signature, model_hash.encode('utf-8'))
            return True
        except InvalidSignature:
            return False
        except Exception as e:
            print(f"[ModelVerifier] Verification error: {e}")
            return False
