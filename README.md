backup_oracle
=============

Скрипт для резервного копирования базы Oracle и копирования резервных копий в другое место. 

Скрипт делает следующие вещи:
 1. Создаёт каталог с текущей датой для складирования копий резервных копий. Назовём её "шара".
 2. Создаёт файл со скриптом RMAN.
 3. Запускает резервное копирование с помощью RMAN с вышесозданным скриптом.
 4. Копирует получившиеся файлы в шару.
 5. Удаляет устаревшие каталоги с копиями из шары.
 6. Запускает экспорт базы с помощью EXP.
 7. Копирует получившийся файл в шару.
 8. Удаляет устаревшие файлы экспорта.
 9. Отсылает ошибки на электронную почту.
 10. Пишет ошибки в лог.


Архивные логи не копируются в шару. Соединение с почтовым сервером устанавливается зашифрованное.

Все настройки находятся в файле `conf.py`

Проверялось на Python 2.7.
