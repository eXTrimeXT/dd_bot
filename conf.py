import asyncio
import functools
import itertools
import math
import youtube_dl
from async_timeout import timeout
import discord
from discord.ext import commands
from discord import opus
from discord import FFmpegPCMAudio
import json
import requests
from random import *
import os
# import yt_dlp


#TOKEN = "Njk4NTc3NDM3NTQ1NTk0OTM0.XpH28A.1WPour9onfLqd-GAr8x2iks_8t8" # TSERVER
TOKEN = "MTEzOTE2MjA1MjA4NzI2MzM0Mw.GKYH-F.M4Ijpz3BiCruXN8sRDFAbmx4CP4ONGk7TNhp38"  # БАНДА
ID_OWNER = 552140044379357184  # eXTrime#0522
PREFIX = "!"
VERSION = 3.0
ID_MAIN_CHANNEL = 697731188454064179
ID_FIRST_ROLE = 911565319716356096
IS_LOG = True
IS_MESSAGE_LOG = False


# TODO: Создаём бота
bot = commands.Bot(command_prefix=PREFIX, case_insensitive=True, intents=discord.Intents.all(), help_command=None)


# Логирование
def logger(tag: str, text_error: str):
    if IS_LOG:
        print(f"{tag} : {text_error}")


EMB_HELP = f"""
```Музыка:
join - Вызывает бота в ваш ГК    
invite "ГК" - Вызывает бота в ГК
leave - Очищает очередь, покидает ГК (ALL)
volume 0-100 - Устанавливает громкость (ADMIN)
now - Показывает трек, который играет
pause - Приостанавливает трек
resume - Возобновляет трек
stop - Останавливает трек, очищает очередь
skip - Запускает голосование пропуска трека
queue page - Показывает очередь, можно со страницей
shuffle - Перемешивает очередь
remove - Удаляет трек
loop - Зацикливает трек
playalias - Запускает трек MIYAGI или Shadowraze(Использование: !мш м или !мш ш)
pl ваш запрос - Играет первый найденый трек 
search ваш запрос - Ищет 10 запросов для проигрывания

Приложения:
app 1-3 - Открывает активность
1) Ютуб
2) Ночной покер
3) Шахматы

Мини-игры с ботом:
kbn камень/ножницы/бумага - Простая игра с ботом

Администрирование: (АДМИН)
clear "число" - Очищает чат на "число" сообщений, 100 по умолчанию
wab обращение - Позволяет писать от имени Бота
status текст - Устанавливает статус бота
kick @участник причина - кикает участника=@ник
ban @участник причина - банит участника=@ник
botstop - Бот выходит из аккаунта (OWNER)

Без категории:
version - Версия бота = {VERSION}
ping - Узнать пинг
ava @участник - Показать аву участника 
vk - Группа VK
update - Показывает обновления бота текущей версии
alias - Показывает Псевдонимы команд
help - Показать это сообщение```
"""



EMB_ALIASES = """
```ПСЕВДОНИМЫ:
Музыка:
join - войди
invite - вызвать
leave - выгнать
volume - громкость
now - сейчас
pause - пауза
resume - продолжить
stop - стоп
skip - скип
queue - очередь
shuffle - перемешать
remove - удалить
loop - цикл
playalias - мш
pl - играй
search - ищи

Приложения:
app - приложение

Мини-игры с ботом:
knb - кнб

Модерация:
status - статус
clear - cls
kick - кик 
ban - бан
wab - отбота
botstop - ботстоп

Без категории:
version - v
ping - пинг
ava - ава
vk - вк
update - обновление
alias - псевдонимы
help - h```
"""

TEXT_UPDATE = """
**🕒Обновлено🕒:**
🕒

**❔Добавлено❔:**
❕

**❓Что на доработке❓:**
❗Изменение языка локали
"""


# Обновление библиотеки YOUTUBE
# pip install git+https://github.com/ytdl-org/youtube-dl.git@master#egg=youtube_dl