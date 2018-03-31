import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


class AESCrypto:
    def __init__(self, key):
        m = hashlib.sha256()
        m.update(key.encode('utf-8'))
        self.key = m.digest()

    def encrypt(self, message):
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        msg_mod = len(message) % AES.block_size
        if msg_mod > 0:
            padding = AES.block_size - msg_mod
            message = message + (' '*padding)

        return base64.b64encode(iv + cipher.encrypt(message)).decode('utf-8')

    def decrypt(self, encode_text):
        cipher_text = base64.b64decode(encode_text)
        iv = cipher_text[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        return cipher.decrypt(cipher_text[16:]).decode('utf8').strip()


def init_crypto(app):
    app.crypto = AESCrypto(app.secret_key)
