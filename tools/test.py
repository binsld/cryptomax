from os import getcwd

try: 
    open(".crypto_secret", "r").read()
except FileNotFoundError:
    if getcwd().split("/")[-1] == "tools":
        try:
            open("../.crypto_secret", "r").read()
        except FileNotFoundError:
            print("Crypto secret not found")
