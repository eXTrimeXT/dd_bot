from pathlib import Path
import requests
import zipfile
import subprocess
import os

python_name_exe = "python_3_9_1.exe"
DIR_NAME = Path("C:\\dd_bot-main")

if not Path(python_name_exe).exists():
    print("Скачивание Python_3_9_1")
    print("НАЖМИ НА ГАЛОЧКУ СНИЗУ!!!")
    response = requests.get("https://www.python.org/ftp/python/3.9.1/python-3.9.1-amd64.exe")
    with open(python_name_exe, 'wb') as file:
        file.write(response.content)
    print('Python_3_9_1 скачан!')
    # Запустить исполняемый файл
    subprocess.Popen(Path(python_name_exe))
    exit()

if not DIR_NAME.exists():
    print("Скачивание репозитория...")
    response = requests.get('https://github.com/eXTrimeXT/dd_bot/archive/refs/heads/main.zip')
    with open('file.zip', 'wb') as file:
        file.write(response.content)
    print('Репозиторий скачан!')
    print("Распаковка архива...")
    os.system("python -m zipfile -e file.zip C:\\")
    os.system("del file.zip")
    print("Архив извлечён!")

print("Проверка зависимостей...")
os.system("python -m pip install --upgrade pip")
os.system(f"python -m pip install -r {DIR_NAME}\\requirements.txt")
# os.system("pip install git+https://github.com/ytdl-org/youtube-dl.git@master#egg=youtube_dl")
print("Зависимости в порядке...")

print("Уставнока прошла успешно!")
os.system("pause")