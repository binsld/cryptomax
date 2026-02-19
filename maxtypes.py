class Dialog:
    def __init__(self, data):
        self.id = data["id"]
        self.cid = data["cid"]
        self.owner = data["owner"]
        self.last = data["lastMessage"]["time"]
        
        try:
            self.isBot = bool(data["hasBots"])
        except KeyError:
            self.isBot = False


    def __repr__(self):
        return f"Dialog(id={self.id!r}, cid={self.cid!r}, owner={self.owner!r})"

class Chat:
    def __init__(self, data):
        self.title = data["title"]
        self.id = data["id"]
        self.cid = "plug" #data["cid"]
        self.access = data["access"]
        self.last = data["lastMessage"]["time"]

    def __repr__(self):
        return f"Chat(id={self.id!r}, cid={self.cid!r}, title={self.title!r}"

class Channel:
    def __init__(self, data):
        self.title = data["title"]
        self.link = data["link"]
        self.id = data["id"]
        self.access = data["access"]
        self.last = data["lastMessage"]["time"]

    def __repr__(self):
        return f"Channel(id={self.id!r}), title={self.title!r}"

class Session:

    def __init__(self, data):
        self.name = data["payload"]["profile"]["contact"]["names"][0]["name"]
        self.firstName = data["payload"]["profile"]["contact"]["names"][0]["firstName"]
        self.lastName = data["payload"]["profile"]["contact"]["names"][0]["lastName"]
        self.description = data["payload"]["profile"]["contact"]["description"]
        self.phone = data["payload"]["profile"]["contact"]["phone"]
        self.id = data["payload"]["profile"]["contact"]["id"]
        self.chats = []
        for i in data["payload"]["chats"]:
            if i["type"] == "DIALOG":
                self.chats.append(Dialog(i))
            if i["type"] == "CHANNEL":
                self.chats.append(Channel(i))
            if i["type"] == "CHAT":
                self.chats.append(Chat(i))
        # print(self.chats)

    def __repr__(self):
        return f"Session(id={self.id!r}, name={self.name!r}, description={self.description!r}, phone={self.phone!r})"
