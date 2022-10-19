class Error(Exception):
    """Базовый класс для исключений, которые не нужно отправлять в Telegram."""


class ExceptionSendMessageError(Error):
    """Класс исключения при сбое отправки сообщения."""

    def __init__(self, message):
        self.message = message


class ExceptionStatusError(Exception):
    """Класс исключения при не корректном статусе ответа."""

    def __init__(self, message):
        self.message = message


class ExceptionGetAPYError(Exception):
    """Класс исключения при ошибке запроса к API."""

    def __init__(self, message):
        self.message = message
