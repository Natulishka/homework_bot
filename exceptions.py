class ExceptionNotEnoughtVariablesError(Exception):
    """Класс исключения при отсутсвии переменных окружения,
    которые необходимы для работы программы.
    """

    def __init__(self, message):
        self.message = message


class ExceptionSendMessageError(Exception):
    """Класс исключения при сбое отправки сообщения."""

    def __init__(self, message):
        self.message = message


class ExceptionTypeError(TypeError):
    """Класс исключения при не корректном типе объекта."""

    def __init__(self, message):
        self.message = message


class ExceptionKeyError(KeyError):
    """Класс исключения при несуществующем ключе."""

    def __init__(self, message):
        self.message = message
