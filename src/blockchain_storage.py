import json
import os
import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

class BlockchainStorage:
    def __init__(self, filename="blockchain.json"):
        self.filename = filename
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        self.key_path = os.path.join('data', 'private_key.pem')
        self.blockchain_path = os.path.join('data', filename)
        self.private_key = self._generate_or_load_keys()

    def _generate_or_load_keys(self):
        try:
            if not os.path.exists(self.key_path):
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
                # Save private key
                with open(self.key_path, "wb") as f:
                    pem = private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    )
                    f.write(pem)
                os.chmod(self.key_path, 0o400)  # Read-only
            else:
                with open(self.key_path, "rb") as f:
                    private_key = serialization.load_pem_private_key(
                        f.read(),
                        password=None
                    )
            return private_key
        except Exception as e:
            raise Exception(f"Error handling keys: {str(e)}")

    def save_blockchain(self, chain):
        try:
            if os.path.exists(self.blockchain_path):
                os.chmod(self.blockchain_path, 0o600)
                
            data = {
                'chain': chain,
                'signature': None
            }
            
            # Sign the chain data
            signature = self._sign_data(json.dumps(chain).encode())
            data['signature'] = signature.hex()
            
            with open(self.blockchain_path, 'w') as f:
                json.dump(data, f, indent=4)
                
            os.chmod(self.blockchain_path, 0o400)  # Read-only
            
        except Exception as e:
            raise Exception(f"Error saving blockchain: {str(e)}")

    def _sign_data(self, data):
        return self.private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def _verify_signature(self, data, signature):
        try:
            public_key = self.private_key.public_key()
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    def load_blockchain(self):
        try:
            if not os.path.exists(self.blockchain_path):
                return None
                
            with open(self.blockchain_path, 'r') as f:
                data = json.load(f)
                
            # Verify signature
            if self._verify_signature(
                json.dumps(data['chain']).encode(),
                bytes.fromhex(data['signature'])
            ):
                return data['chain']
            raise ValueError("Blockchain signature verification failed")
            
        except Exception as e:
            raise Exception(f"Error loading blockchain: {str(e)}")