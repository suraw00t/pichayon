import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class AESCrypto:
    def __init__(self, key):
        m = hashlib.sha256()
        m.update(key.encode("utf-8"))
        self.key = m.digest()

    def encrypt(self, message):
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        msg_mod = len(message) % AES.block_size
        if msg_mod > 0:
            padding = AES.block_size - msg_mod
            message = message + (" " * padding)

        padded_message = pad(message.encode("utf-8"), AES.block_size)
        ciphertext_bytes = cipher.encrypt(padded_message)
        ciphertext = base64.b64encode(iv + ciphertext_bytes).decode("utf-8")
        
        return ciphertext

    def decrypt(self, encode_text):
        cipher_text = base64.b64decode(encode_text)
        iv = cipher_text[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_bytes =  cipher.decrypt(cipher_text[16:])
        plaintext_bytes = unpad(decrypted_bytes, AES.block_size)
        plaintext =  plaintext_bytes.decode('utf-8').strip()

        return plaintext


def init_crypto(app):
    app.crypto = AESCrypto(app.secret_key)
