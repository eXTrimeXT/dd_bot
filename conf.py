# import asyncio
# import functools
# import itertools
# import math
# from async_timeout import timeout
import discord
from discord.ext import commands
# from discord import opus
# from discord import FFmpegPCMAudio
# import json
# import requests
# from random import *
# import os
# import yt_dlp as youtube_dl
import socket
import sys

CURRENT_HOST = socket.gethostname()
ID_OWNER = 552140044379357184  # eXTrime#0522
PREFIX = "!"
VERSION = 1.0

# Настройки логирования
IS_LOG = True
IS_MESSAGE_LOG = True
PATH_LOG = "./log.txt"
MAX_SIZE_LOG = 1000


# TODO: Создаём бота
bot = commands.Bot(command_prefix=PREFIX, case_insensitive=True, intents=discord.Intents.all(), help_command=None)
# bot.remove_command("help")



def check_log_file():
    is_clear_file = False
    with open(PATH_LOG, 'r', encoding="utf-8") as file:
        line_count = sum(1 for line in file)
        print(f"Количество строк = {line_count}")
        if line_count >= MAX_SIZE_LOG:
            is_clear_file = True
    if is_clear_file:
        is_clear_file = False
        with open(PATH_LOG, "w") as file:
            file.write("")


# Логирование
def logger(tag: str, text_error: str):
    if IS_LOG:
        log_message = f"{tag} : {text_error}"
        print(log_message)
        with open(PATH_LOG, "a", encoding="utf-8") as file:
            file.write(log_message+"\n")
        check_log_file()


EMB_HELP = f"""
```Музыка:
invite      - Вызывает бота в ГК
leave       - Очищает очередь, покидает ГК (ALL)
now         - Показывает трек, который играет
pause       - Приостанавливает трек
resume      - Возобновляет трек
stop        - Останавливает трек, очищает очередь
skip        - Запускает голосование пропуска трека
queue       - Показывает очередь, можно со страницей
shuffle     - Перемешивает очередь
remove      - Удаляет трек
loop        - Зацикливает трек
play        - Играет первый найденный трек 
search      - Ищет 10 запросов для проигрывания

Администрирование: (АДМИН)
botstop     - Отключение бота (ONLY OWNER)
clear       - Очищает чат на 50 сообщений, по умолчанию (ADMIN)
wab         - Позволяет писать от имени Бота (ADMIN)

Дополнительно:
version     - Версия бота = {VERSION}
ping        - Узнать пинг
update      - Показывает обновления бота текущей версии
ava         - Показать аву участника
alias       - Показывает Псевдонимы команд
help        - Показать это сообщение
```
"""





EMB_ALIASES = """
```ПСЕВДОНИМЫ:
Музыка:
invite  - вызвать
leave   - выгнать
now     - сейчас
pause   - пауза
resume  - продолжить
stop    - стоп
skip    - пропуск
queue   - очередь
shuffle - перемешать
remove  - удалить
loop    - зациклить
play    - играй
search  - найди

Приложения:
app     - приложение

Модерация:
status  - статус
clear   - очистить
wab     - отбота

Без категории:
version - версия
ping    - пинг
update  - обновление
ava     - ава
alias   - псевдонимы
help    - помощь

Команды GPT:
gpt35 - ии35
gpt4 - ии4(не стабильный)
```
"""


TEXT_UPDATE = """
**🕒Обновлено🕒:**
🕒

**❔Добавлено❔:**
❕
"""


# Обновление библиотеки YOUTUBE
# pip install git+https://github.com/ytdl-org/youtube-dl.git@master#egg=youtube_dl