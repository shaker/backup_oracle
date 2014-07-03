# -*- coding: utf-8 -*-

import os
from datetime import datetime
from datetime import date

#Имя клиента. Вставляется в заголовок письма
client_name = ''

#Срок годности резервных копий в днях
date_expiration = 7

#Шаблон даты. В оракловских названиях каталогов с бэкапами используется
#дата вида год_месяц_день. Будем использовать такой же вид везде
date_template = date.today().strftime('%Y_%m_%d')

#==================#
# Каталоги и файлы #
#==================#

#Каталог, куда будут копироваться резервные копии
#Лучше, чтобы каталог находился на удалённой тачке
dir_share = r''
dir_share_current = os.path.join(dir_share, date_template)

#Каталог, куда будут складываться файлы экспорта
dir_exports = r''
current_export = os.path.join(dir_exports, date_template + '.bkp')

#Каталог с резервными наборами RMAN
dir_backupsets = r''
dir_current_backupset = os.path.join(dir_backupsets, date_template)

#Если база контейнерная (появилось в Oracle 12c), то также необходимо
#указать каталог с резервными наборами базы-контейнера. Работает, если ora_cdb = True
dir_bs_cdb = r''
dir_current_bs_cdb = os.path.join(dir_bs_cdb, date_template)

#Каталог с резервными копиями контрольных файлов при включённой опции
#configure controlfile autobackup on в RMAN
dir_controfile = r''
dir_current_controlfile = os.path.join(dir_controfile, date_template)

#Каталог с логами
dir_logs = r''

#===============================================#
# Параметры для подключения к почтовому серверу #
#===============================================#

#Отправитель (name@domain.ltd)
mail_me = ''

#Получатель (name@domain.ltd)
mail_you = ''

#Заголовок письма
mail_subject = 'Отчёт по резервному копированию от ' + date.today().strftime('%d.%m.%Y') + ' ' + client_name

#SMTP-сервер
mail_smtp = ''

#Логин для аутентификации на почтовом сервере
mail_login = ''

#Пароль для аутентификации на почтовом сервере
mail_pass = ''

#=====================================#
# Параметры для работы с базой Oracle #
#=====================================#

#SID базы данных. Если база контейнерная, то это SID базы-контейнера
ora_sid = ''

#Если база контейнерная, то это SID подключаемой базы
ora_sid_pdb = ''

#Пароль для пользователя sys
ora_sys_pass = ''

#Параметр NLS_LANG для экспорта в переменную окружения NLS_LANG
#Например, AMERICAN_AMERICA.CL8MSWIN1251
ora_nls_lang = r''

#Домашний каталог для экспорта в переменную окружения ORACLE_HOME
ora_home = r''

#Признак того, является ли база контейнерной
ora_cdb = False

#Путь до исполняемых файлов оракла для экспорта в переменную окружения PATH
ora_bin = r''

#============================#
# Параметры для запуска RMAN #
#============================#

#Путь до файла, в который будет записываться скрипт RMAN
rman_script_file = os.path.join(os.path.dirname(__file__), 'rman.rmn')

#Скрипт RMAN
rman_script = '''run {
backup database;
crosscheck backup;
crosscheck archivelog all;
delete noprompt expired archivelog all;
delete noprompt force obsolete;
}'''
