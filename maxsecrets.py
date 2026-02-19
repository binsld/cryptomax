from json import loads

class Secrets:
    def __init__(self):
        self.token, self.id = open(".auth_secret", "r").read().split("\n")

if __name__ == "__main__":
    print("Откройте max на компьютере, войдите в веб-версию, откройте инструменты разработчика и найдите local storage сайта web.max.ru")
    token = loads(input("Скопируйте сюда значение поля __oneme_auth: "))["token"]
    deviceId = input("Скопируйте сюда значение поля __oneme_device_id: ")
    
    open(".auth_secret", "w").write(token + "\n" + deviceId)
