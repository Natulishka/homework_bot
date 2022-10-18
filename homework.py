import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telegram import Bot

import exceptions

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
fileHandler = logging.FileHandler("logfile.log", encoding='utf-8')
streamHandler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger.setLevel(logging.INFO)
streamHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)
logger.addHandler(streamHandler)
logger.addHandler(fileHandler)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception:
        raise exceptions.ExceptionSendMessageError(
            f"Cбой при отправке сообщения '{message}' в Telegram")
    else:
        logger.info(f"В Telegram отправлено сообщение '{message}'")


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != HTTPStatus.OK:
        message = (f"Сбой в работе программы: Эндпоинт {ENDPOINT} недоступен."
                   " Код ответа API: {response.status_code}")
        raise exceptions.ExceptionSendMessageError(message)
    return response.json()


def check_response(response):
    """Проверяет ответ API на корректность."""
    if not isinstance(response, dict):
        message = "Ответ API получен не в виде словаря"
        raise exceptions.ExceptionTypeError(message)
    keys = ['current_date', 'homeworks']
    for key in keys:
        if key not in response:
            message = f"В ответе API нет ключа {key}"
            raise exceptions.ExceptionKeyError(message)
    homework = response.get('homeworks')
    if not isinstance(homework, list):
        message = "API вернул не список под ключом homeworks"
        raise exceptions.ExceptionTypeError(message)
    else:
        return homework


def parse_status(homework):
    """Извлекает из конкретной домашней работы статус этой работы."""
    if "homework_name" not in homework or "status" not in homework:
        message = "В словаре homework не найден ключ homework_name"
        raise exceptions.ExceptionKeyError(message)
    homework_name = homework.get('homework_name')
    if "status" not in homework:
        message = "В словаре homework не найден ключ status"
        raise exceptions.ExceptionKeyError(message)
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUSES:
        message = (
            f"В словаре HOMEWORK_STATUSES не найден ключ {homework_status}")
        raise exceptions.ExceptionKeyError(message)
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return all([TELEGRAM_TOKEN, PRACTICUM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        message = ("Доступны не все переменные окружения, которые "
                   "необходимы для работы программы")
        logger.critical(message)
        raise exceptions.ExceptionNotEnoughtVariablesError(message)

    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    previous_message_error = ''

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if len(homework) > 0:
                message = parse_status(homework[0])
                send_message(bot, message)
            else:
                logger.debug("В ответе API отсутсвуют новые статусы")
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)
        except Exception as error:
            message_error = f'Сбой в работе программы: {error}'
            logger.error(message_error)
            if message_error != previous_message_error:
                send_message(bot, message_error)
            previous_message_error = message_error
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
