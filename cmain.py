import curses
import time
import websocket
import datetime
import json
from string import printable
from colorama import Fore
import cryptography as crypt
from base64 import b64decode, b64encode
from maxtypes import *
from maxsecrets import Secrets
from threading import Thread
from random import randint


# ----- Переменные -----
pub, priv = crypt.loadkeys() # грузим ключи шифрования
secrets = Secrets() # грузим секреты аутентификации

contacts = []
messages = []
printables = list(map(ord, list(printable[:-5])))
ws = None

# ----- Константы -----
SIDEBAR_WIDTH = 20 # ширина списка чатов в процентах
tzone = datetime.timezone(datetime.timedelta(hours=3))



def maxapi():
    global contacts, messages, ws
    # cоздаём websocket соединение
    headers = {
        "Origin": "https://web.max.ru"
    }
    ws = websocket.create_connection("wss://ws-api.oneme.ru/websocket", header=headers)
    
    # кидаем данные входа
    ws.send('{"ver":11,"cmd":0,"seq":3,"opcode":6,"payload":{"userAgent":{"deviceType":"WEB","locale":"ru","deviceLocale":"en","osVersion":"Linux","deviceName":"Chrome","headerUserAgent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36","appVersion":"26.2.2","screen":"1080x1920 1.0x","timezone":"Europe/Moscow"},"deviceId":"'+ secrets.id +'"}}')
    part1 = ws.recv()
    ws.send('{"ver": 11, "cmd": 0, "seq": 1, "opcode": 19, "payload": {"interactive": true, "token": "'+ secrets.token +'", "chatsCount": 40, "chatsSync": 0, "contactsSync": 0, "presenceSync": -1, "draftsSync": 0}}')
    part2 = ws.recv()

    nxt = ws.recv()
    if json.loads(nxt)["opcode"] == 292: # banners
        pass

    # создаём объект сессии из полученных данных
    session = Session(json.loads(part2))


    contacts.clear()
    for i in session.chats:
        if type(i) != Dialog:
            contacts.append([i.id, i.title, i.last])
        else:
            contacts.append([i.id, str(i.id), i.last])

    # принимаем события
    #print("-"*40)
    while True:
        data = json.loads(ws.recv())
        if data["opcode"] == 49:
            messages.clear()
            for i in data["payload"]["messages"]:
                txt = i["text"]
                try:
                    txt = priv.decrypt(b64decode(txt.encode())).decode() 
                except:
                    txt += "\t\t(unsecure)"
                tm = datetime.datetime.fromtimestamp(i["time"]/1000, datetime.UTC).astimezone(tzone).strftime('%H:%M')

                if "sender" in i:
                    txt = f"[{tm}] {i['sender']}: {txt}"
                else:
                    txt = f"[{tm}]: {txt}"
                    
                try:
                    messages.append([1,txt])
                except:
                    messages.append([0,txt])
        # пришло сообщение
        if data["opcode"] == 128:
            try:
                data = priv.decrypt(b64decode(data["payload"]["message"]["text"].encode()))
                #print(f'Получено зашифрованное сообщение {data}')
            except ValueError:
                pass
                #print(f"Получено не зашифрованное сообщение {data['payload']['message']['text']}")





def tui(scr):
    global contacts, messages, ws

    buffer = ""
    scr.clear()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN) 
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)

    curses.curs_set(0)
    mode = 0
    chat_selector = 0
    """
    0 - sidebar
    1 - chat
    2 - text input
    """

    scr.keypad(True)
    #curses.mousemask(curses.BUTTON1_PRESSED)#curses.REPORT_MOUSE_POSITION) | curses.BUTTON1_PRESSED)
    scr.timeout(100)

    while True:
        # ----- State -----
        height, width = scr.getmaxyx()
        sidebar = int(SIDEBAR_WIDTH * width / 100)

        # ----- Draw -----
        scr.clear()
        for y in range(height - 1):
            for x in range(width):
                # Отрисовать sidebar
                if x < sidebar :
                    # Верхняя табличка
                    if y == 0:
                        if x == 1:
                            scr.addch(y, x, "[", curses.color_pair(2))
                        elif x == sidebar - 2:
                            scr.addch(y, x, "]", curses.color_pair(2))
                        elif 1 < x < sidebar - 2:
                            try:
                                scr.addch(y, x, "  CryptoMAX  "[(x-int(time.time()*5))%13], curses.color_pair(2))
                            except:
                                scr.addch(y, x, " ", curses.color_pair(2))
                    # Список чатов
                    else:

                        # Рамка
                        if y == 1:
                            if x == 0:
                                scr.addch(y,x, '┌', curses.color_pair(2))
                            elif x == sidebar - 1:
                                scr.addch(y,x, '┐', curses.color_pair(2))
                            else:
                                scr.addch(y,x, '─', curses.color_pair(2))
                        elif y == height-2:
                            if x == 0:
                                scr.addch(y,x, '└', curses.color_pair(2))
                            elif x == sidebar - 1:
                                scr.addch(y,x, '┘', curses.color_pair(2))
                            else:
                                scr.addch(y,x, '─', curses.color_pair(2))
                        elif x == 0 or x == sidebar - 1:
                            scr.addch(y,x, '│', curses.color_pair(2))
                        

                        elif y != chat_selector + 2:
                            try:
                                scr.addch(y, x, contacts[y-2][1][x-1], curses.color_pair(2))
                            except:
                                scr.addch(y, x, ' ', curses.color_pair(2))
                        else:
                            try:
                                scr.addch(y, x, contacts[y-2][1][x-1], curses.color_pair(1))

                            except:
                                scr.addch(y, x, ' ', curses.color_pair(1))

                # Отрисовать основное окно
                else:
                    try:
                        #if x == sidebar - 1:
                         #   scr.addch(y,x, '│', curses.color_pair(2))
                        
                        if y == 0:
                            if x == sidebar:
                                scr.addch(y,x, '┌', curses.color_pair(2))
                            elif x == width - 1:
                                scr.addch(y,x, '┐', curses.color_pair(2))
                            else:
                                scr.addch(y,x, '─', curses.color_pair(2))
                        elif y == height-2:
                            if x == sidebar:
                                scr.addch(y,x, '└', curses.color_pair(2))
                            elif x == width - 1:
                                scr.addch(y,x, '┘', curses.color_pair(2))
                            else:
                                scr.addch(y,x, '─', curses.color_pair(2))
                        elif y == height - 4:
                            if x == sidebar:
                                scr.addch(y,x, '├', curses.color_pair(2))
                            elif x == width - 1:
                                scr.addch(y,x, '┤', curses.color_pair(2))
                            else:
                                scr.addch(y,x, '─', curses.color_pair(2))

                        elif x == sidebar or x == width - 1:
                            if y != height - 4:
                                scr.addch(y,x, '│', curses.color_pair(2))




                        elif y == height-3:
                            scr.addch(y,x,buffer[x - sidebar - 1], curses.color_pair(2))
                        else:
                            if x == sidebar + 1:
                                scr.addstr(y, x, messages[y][1], curses.color_pair(2))
                            #if x == sidebar + 1:
                            #    scr.addch(y,x, messages[y][1])
                        #elif not messages[y][0]:
                        #    scr.addch(y,x, messages[y][1][x - sidebar - 1], curses.color_pair(2))
                        #else:
                        #    scr.addch(y,x, messages[y][1][x - sidebar - 1], curses.color_pair(3))

                    except:
                        scr.addch(y, x, ' ', curses.color_pair(2))

        scr.refresh()

        # ----- Input -----
        com = scr.getch()

        if com == 27: # exit
            break

        if com == 260: # left
            mode -= 1
            if mode == 0:
                mode = 0
        
        if com == 261: # right
            mode += 1
            if mode == 2:
                mode = 2
        
        if com == 259: # up
            if mode == 0:
                chat_selector -= 1
                if chat_selector <= 0:
                    chat_selector = 0

        if com == 258: # down
            if mode == 0:
                chat_selector += 1
                if chat_selector >= len(contacts):
                    chat_selector = len(contacts) - 1

        if mode == 2:
            if com in printables:
                buffer += chr(com)
            if com == 263:
                buffer = buffer[:-1]
        if com == 10: # enter
            if mode == 0:
                ws.send('{"ver": 11, "cmd": 0, "seq": 12, "opcode": 49, "payload": {"chatId": '+ str(contacts[chat_selector][0]) +', "from": '+ str(contacts[chat_selector][2]) +', "forward": 0, "backward": 30, "getMessages": true}}')
            else:
                ws.send('{"ver": 11, "cmd": 0, "seq": 25, "opcode": 64, "payload": {"chatId": -70993763284398, "message": {"text": "'+b64encode(priv.encrypt(buffer.encode())).decode()+'", "cid": 17714'+str(randint(0,9))+str(randint(0,9))+str(randint(0,9))+'16842, "elements": [], "attaches": []}, "notify": true}}')


    curses.endwin() 


if __name__ == '__main__':
    sb = Thread(target=maxapi) 
    sb.start()
    curses.wrapper(tui)
    sb.join()
