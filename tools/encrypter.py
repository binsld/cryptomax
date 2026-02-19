from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from base64 import b64decode, b64encode

key = PKCS1_OAEP.new(RSA.import_key(b64decode(input("Paste public key: "))))

print(b64encode(key.encrypt(input("Enter message: ").encode())).decode())
