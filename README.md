# Telegram-bot

### Описание
Телеграм-бот для отслеживания статуса проверки домашней работы на Яндекс.Практикум.
Присылает сообщения, когда статус изменен - взято в проверку, есть замечания, зачтено.


### Стек технологий:  


Python 3.9  
python-dotenv 0.19.0  
python-telegram-bot 13.7  



### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Natulishka/api_final_yatube.git
cd api_final_yatube
```
Cоздать виртуальное окружение:

```
python -m venv venv
```
Aктивировать виртуальное окружение:
```
source venv/Scripts/activate
```
Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Записать необходимые ключи в переменные окружения (файл .env):

- PRACTICUM_TOKEN - токен профиля на Яндекс.Практикуме
- TELEGRAM_TOKEN - токен телеграм-бота
- TELEGRAM_CHAT_ID - свой ID в телеграме

Запустить проект:
```
python homework.py
```
