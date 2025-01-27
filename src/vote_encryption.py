from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os
import base64

class VoteEncryption:
    _key = None
    
    @classmethod
    def get_key(cls):
        if cls._key is None:
            key_path = os.path.join('data', 'encryption.key')
            if os.path.exists(key_path):
                with open(key_path, 'rb') as f:
                    cls._key = f.read()
            else:
                os.makedirs('data', exist_ok=True)
                cls._key = os.urandom(32)
                with open(key_path, 'wb') as f:
                    f.write(cls._key)
                os.chmod(key_path, 0o400)
        return cls._key

    @classmethod
    def encrypt_vote(cls, data):
        if not data:
            return ''
        try:
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES(cls.get_key()), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data.encode()) + padder.finalize()
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            return base64.b64encode(iv + encrypted_data).decode()
        except Exception as e:
            print(f"Encryption error: {str(e)}")
            return ''

    @classmethod
    def decrypt_vote(cls, encrypted_data):
        if not encrypted_data:
            return ''
        try:
            raw_data = base64.b64decode(encrypted_data)
            iv = raw_data[:16]
            encrypted_content = raw_data[16:]
            
            cipher = Cipher(algorithms.AES(cls.get_key()), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            
            decrypted_padded = decryptor.update(encrypted_content) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
            
            return decrypted.decode()
        except Exception as e:
            print(f"Decryption error: {str(e)}")
            return 'Error decrypting vote'

# Helper functions
def encrypt_vote(president, party):
    return (
        VoteEncryption.encrypt_vote(president),
        VoteEncryption.encrypt_vote(party)
    )

def decrypt_vote(encrypted_vote):
    return VoteEncryption.decrypt_vote(encrypted_vote)
