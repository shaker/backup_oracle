#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Скрипт для запуска резервного копирования базы Oracle.
Скрипт выполняет следующие действия: запускает резервное копирование с помощью RMAN,
делает экспорт базы с помощью утилиты EXP, копирует резервные копии RMAN и файл
экспорта в специально предназначенный для этого каталог и удаляет устаревшие 
копии резервных копий. Возникшие ошибки скрипт шлёт на мыло и пишет в лог.
Скрипт RMAN формируется автоматически функцией create_rman_script().
Проверялось на Python 2.7.
'''

import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from datetime import date
import os
import sys
import shutil
import platform
import conf

errors = []

def error(message):
	message = datetime.today().strftime("%H:%M:%S") + ' ' + message
	errors.append(message)
	return message
	
def errors_to_log():
	file_path = os.path.join(conf.dir_logs, 'backup.' + conf.date_template + '.log')
	file = open(file_path, 'a')
	for err in errors:
		file.write(err + '\n')
	file.close()

def errors_to_mail():
	err_text = ''
	for err in errors:
		err_text = err_text + err + '\n'
	send_email(err_text)
	
def send_email(message):
	msg = MIMEText(message, 'plain', 'utf-8')

	msg['Subject'] = conf.mail_subject
	msg['From'] = conf.mail_me
	msg['To'] = conf.mail_you
	
	try:
		s = smtplib.SMTP_SSL(conf.mail_smtp)
		s.login(conf.mail_login, conf.mail_pass)
		s.sendmail(conf.mail_me, [conf.mail_you], msg.as_string())
	except Exception as e:
		error("Ошибка при отправке почты: {0}".format(e))
		pass
	finally:
		s.quit()
		
def copy_files(src, dst):
	src_files = os.listdir(src)
	for file in src_files:
		full_name = os.path.join(src, file)
		if os.path.isfile(full_name):
			shutil.copy(full_name, dst)
			
def rm_expiry_dirs(dir):
	dirs = os.listdir(dir)
	for d in dirs:
		full_name = os.path.join(dir, d)
		if os.path.isdir(full_name):
			diff = date.today() - datetime.strptime(d, '%Y_%m_%d').date()
			diff = diff.days
			if (diff > conf.date_expiration):
				shutil.rmtree(full_name)
				
def rm_expiry_files(dir):
	files = os.listdir(dir)
	for file in files:
		full_name = os.path.join(dir, file)
		file = os.path.splitext(file)[0]
		if os.path.isfile(full_name):
			diff = date.today() - datetime.strptime(file, '%Y_%m_%d').date()
			diff = diff.days
			if (diff > conf.date_expiration):
				os.remove(full_name)
				
def create_rman_script():
	try:
		file = open(conf.rman_script_file, 'w')
		file.write(conf.rman_script)
	except Exception as rs:
		error('Произошла ошибка при создании файла скрипта RMAN: {0}'.format(rs))
		pass
	finally:
		file.close()
				
def start_rman(): #bachup mafaka!
	os.environ['PATH'] = os.environ['PATH'] + os.pathsep + conf.ora_bin
	os.environ['ORACLE_HOME'] = conf.ora_home
	os.environ['ORACLE_SID'] = conf.ora_sid
	
	rman_exec = "rman target sys/" + conf.ora_sys_pass + "@" + conf.ora_sid + " nocatalog cmdfile='" + conf.rman_script_file + "' log=\"'" + os.path.join(conf.dir_logs, 'rman.' + datetime.today().strftime('%Y_%m_%d_%H-%M-%S') + '.log') + "'\""
	
	return os.system(rman_exec)
		
def start_export():
	if conf.ora_cdb:
		ora_sid_exp = conf.ora_sid_pdb
	else:
		ora_sid_exp = conf.ora_sid
	
	os.environ['PATH'] = os.environ['PATH'] + os.pathsep + conf.ora_bin
	os.environ['ORACLE_SID'] = ora_sid_exp
	os.environ['NLS_LANG'] = conf.ora_nls_lang
	os.environ['ORACLE_HOME'] = conf.ora_home
	
	export_exec = "exp userid='sys/" + conf.ora_sys_pass + "@" + ora_sid_exp + " as sysdba' file=" + conf.current_export + " compress='N' owner='pc' log=\"'" + os.path.join(conf.dir_logs, 'export.' + datetime.today().strftime('%Y_%m_%d_%H-%M-%S') + '.log') + "'\""
	
	return os.system(export_exec)
	
def current_share_exists():
	if os.path.exists(conf.dir_share_current):
		return True
	else:
		return False

if not current_share_exists():
	if not os.path.exists(conf.dir_share):
		error('Шара не смонтирована')
	else:
		try:
			os.mkdir(conf.dir_share_current)
		except Exception as md:
			error('Не смогли создать папку в шаре: {0}'.format(md))
			pass
			
create_rman_script()
		
if start_rman() > 0:
	error('Резервное копирование с помощью утилиты RMAN завершилось неудачно.')
else:
	if current_share_exists():
		try:
			copy_files(conf.dir_current_backupset, conf.dir_share_current)
			copy_files(conf.dir_current_controlfile, conf.dir_share_current)
			if conf.ora_cdb:
				copy_files(conf.dir_current_bs_cdb, conf.dir_share_current)
		except Exception as sr:
			error('Не удалось скопировать резервные копии RMAN: {0}'.format(sr))
			pass
		else:	
			try:
				rm_expiry_dirs(conf.dir_share)
			except Exception as rd:
				error('Не смогли удалить устаревшие копии резервных копий: {0}'.format(rd))
				pass			
	
if start_export() > 0:
	error('Экспорт базы данных с помощью утилиты EXP завершился неудачно.')
else:
	if current_share_exists():
		try:
			shutil.copy(conf.current_export, conf.dir_share_current)
		except Exception as sc:
			error('Не удалось скопировать файл экспорта: {0}'.format(sc))
			pass
		else:
			try:
				rm_expiry_files(conf.dir_exports)
			except Exception as ef:
				error('Не смогли удалить устаревшие файлы экспорта: {0}'.format(ef))
				pass
			
if len(errors) == 0:
	errors.append('Резервное копирование завершилось без ошибок.')

errors_to_mail()
errors_to_log()
