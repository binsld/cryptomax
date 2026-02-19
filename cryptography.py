from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64encode


# создать новую пару ключей шифрования
def newkey() -> None:
    priv = RSA.generate(3072)
    pub = priv.public_key()
    
    open(".crypto_secret", "wb").write(b64encode(pub.export_key(format="DER")) + b"\n-----DELIMITER-----\n" + priv.export_key(format="PEM"))


# загрузить пару ключей шифрования
def loadkeys() -> tuple:
    try:
        pub, priv = open(".crypto_secret", "rb").read().split(b"\n-----DELIMITER-----\n")
        pub = pub.decode() # чтобы поставить его в профиль
        priv = PKCS1_OAEP.new(RSA.import_key(priv)) # чтобы дешифровать сообщения 
    except FileNotFoundError:
        return None, None
    return pub, priv


if __name__ == "__main__":
    newkey()
    print(loadkeys()[0])
    print("New keypair generated")
