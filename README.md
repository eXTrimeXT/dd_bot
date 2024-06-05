# Discord Music Bot
## Архитектура файлов Python:
### Основные файлы:
- **[conf](https://github.com/eXTrimeXT/dd_bot/blob/main/conf.py)**
  - Подключение зависимостей
  - Токены
  - Логирование
  - Константные переменные


- **[main](https://github.com/eXTrimeXT/dd_bot/blob/main/main.py) содержит классы:** *[Music](https://github.com/eXTrimeXT/dd_bot/blob/main/Music.py), [MyBot](https://github.com/eXTrimeXT/dd_bot/blob/main/MyBot.py)*
  - Приветствие нового участника
  - Запуск дискорда бота


- **Класс [MyBot](https://github.com/eXTrimeXT/dd_bot/blob/main/MyBot.py)**
  - Версия 
  - Пинг
  - Текст обновления
  - Показать аватарку участника
  - Вывести псевдонимы команд бота
  - Вывод текста help


- **Класс [Music](https://github.com/eXTrimeXT/dd_bot/blob/main/Music.py)**
  - **Класс Music содержит классы *[Song](https://github.com/eXTrimeXT/dd_bot/blob/main/Song.py), [VoiceState](https://github.com/eXTrimeXT/dd_bot/blob/main/VoiceState.py), [YTDLSource](https://github.com/eXTrimeXT/dd_bot/blob/main/YTDLSource.py)***
    - Обращение участника к боту, для запуска треков в ГК
  - **Класс [Song](https://github.com/eXTrimeXT/dd_bot/blob/main/Song.py) содержит класс *[YTDLSource](https://github.com/eXTrimeXT/dd_bot/blob/main/YTDLSource.py):***
    - Создание ресурса
    - Получение вывода

  - **Класс [VoiceState](https://github.com/eXTrimeXT/dd_bot/blob/main/VoiceState.py) содержит классы *[YTDLSource](https://github.com/eXTrimeXT/dd_bot/blob/main/YTDLSource.py):***
    - Полное управление состояния треков
    - Воспроизведение
    - Пауза
    - Зацикливание
    - Громкость
    - Пропуск трека(Голосование)
    - Проигрывание следующего трека
    - Управление очередью треков

  - **Класс [SongQueue](https://github.com/eXTrimeXT/dd_bot/blob/main/SongQueue.py)**
    - Асинхронная абстракция очередей треков
    - Получение текущего трека в очереди
    - Узнать длину очереди
    - Очистить очередь
    - Перемешать треки в очереди
    - Удалить трек из очереди

  - **Класс [YTDLSource](https://github.com/eXTrimeXT/dd_bot/blob/main/YTDLSource.py)**
    - Содержит классы-затычки для обработки исключений: *[VoiceError](https://github.com/eXTrimeXT/dd_bot/blob/main/YTDLSource.py), [YTDLError](https://github.com/eXTrimeXT/dd_bot/blob/main/YTDLSource.py)*
    - Настройка конфигурации звука и ютуба
    - Получение всех необходимых данных трека из ютуба
    - Создание трека 
    - Поиск трека
    - Получение продолжительности трека

## Зависимости
### Классические
Файл [requirements.txt](https://github.com/eXTrimeXT/dd_bot/blob/main/requirements.txt)
- discord.py==2.3.2
- asyncio==3.4.3
- ffmpeg==1.4
- ffmpeg-python==0.2.0
- requests==2.31.0
- *youtube-dl==2021.12.17*

Установка ```python -m pip install -r requirements.txt```

### Дополнительные
- yt_dlp - Альтернативная замена *youtube-dl==2021.12.17*

Установка ```pip install git+https://github.com/ytdl-org/youtube-dl.git@master#egg=youtube_dl```