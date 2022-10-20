import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telegram import Bot

from exceptions import (Error, ExceptionGetAPYError, ExceptionSendMessageError,
                        ExceptionStatusError)

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
        logger.info("Начало отправки сообщения в Telegram чат")
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        raise ExceptionSendMessageError(
            f"Cбой при отправке сообщения '{message}' в Telegram. "
            f"Error: {error}")
    else:
        logger.info(f"В Telegram отправлено сообщение '{message}'")


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    requests_params = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': params
    }
    try:
        logger.info(f"Запрос к эндпоинту '{ENDPOINT}' API-сервиса c "
                    f"параметрами {requests_params}")
        response = requests.get(**requests_params)
        if response.status_code != HTTPStatus.OK:
            message = (f"Сбой в работе программы: Эндпоинт {ENDPOINT} c "
                       f"параметрами {requests_params} недоступен. status_code"
                       f": {response.status_code}, reason: {response.reason}, "
                       f"text: {response.text}")
            raise ExceptionStatusError(message)
    except Exception as error:
        raise ExceptionGetAPYError(
            f"Cбой при запросе к энпоинту '{ENDPOINT}' API-сервиса с "
            f"параметрами {requests_params}."
            f"Error: {error}")
    return response.json()


def check_response(response):
    """Проверяет ответ API на корректность."""
    logger.info("Проверка ответа API на корректность")
    if not isinstance(response, dict):
        message = (f"Ответ API получен в виде {type(response)}, "
                   "а должен быть словарь")
        raise TypeError(message)
    keys = ['current_date', 'homeworks']
    for key in keys:
        if key not in response:
            message = f"В ответе API нет ключа {key}"
            raise KeyError(message)
    homework = response.get('homeworks')
    if not isinstance(homework, list):
        message = (f"API вернул {type(homework)} под ключом homeworks, "
                   "а должен быть список")
        raise TypeError(message)
    return homework


def parse_status(homework):
    """Извлекает из конкретной домашней работы статус этой работы."""
    logger.info("Извлечение из конкретной домашней работы статуса этой работы")
    if "homework_name" not in homework:
        message = "В словаре homework не найден ключ homework_name"
        raise KeyError(message)
    homework_name = homework.get('homework_name')
    if "status" not in homework:
        message = "В словаре homework не найден ключ status"
        raise KeyError(message)
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUSES:
        message = (
            f"В словаре HOMEWORK_STATUSES не найден ключ {homework_status}")
        raise KeyError(message)
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    logger.info("Проверка доступности переменных окружения")
    return all([TELEGRAM_TOKEN, PRACTICUM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        message = ("Доступны не все переменные окружения, которые "
                   "необходимы для работы программы: "
                   "PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID")
        logger.critical(message)
        sys.exit(message)

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
        except Exception as error:
            message_error = f'Сбой в работе программы: {error}'
            logger.error(message_error)
            if not issubclass(error.__class__, Error):
                if message_error != previous_message_error:
                    send_message(bot, message_error)
                    previous_message_error = message_error
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
