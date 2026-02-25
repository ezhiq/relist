import logging
import colorlog
from colorlog import ColoredFormatter


def setup_colored_logging(log_level=logging.INFO):
    """
    Настройка цветного логгирования с разными цветами для имен модулей
    INFO - цвет модуля, остальные уровни - стандартные цвета
    """

    class ModuleNameColoredFormatter(ColoredFormatter):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Цвета для модулей (используются только для INFO)
            self.module_colors = {
                'funpay': 'light_magenta',
                'avtovud': 'light_blue',
                'buyers': 'light_green',
                'raise_tg': 'light_yellow',
            }

            # ANSI коды цветов
            self.color_codes = {
                'light_magenta': '\033[95m',
                'light_blue': '\033[94m',
                'light_green': '\033[92m',
                'light_yellow': '\033[93m',
                'light_cyan': '\033[96m',
                'white': '\033[97m',
                'cyan': '\033[96m',
                'green': '\033[92m',
                'yellow': '\033[93m',
                'red': '\033[91m',
                'dark_red': '\033[31m',
                'red_bg': '\033[97;101m',  # white on red
                'reset': '\033[0m'
            }

        def get_module_color(self, module_name):
            """Определить цвет для модуля"""
            for key, color in self.module_colors.items():
                if key in module_name.lower():
                    return color
            return 'white'

        def format(self, record):
            # Определяем цвет модуля
            module_color = self.get_module_color(record.name)
            module_color_code = self.color_codes.get(module_color, self.color_codes['white'])

            # Определяем цвета в зависимости от уровня
            level = record.levelname

            if level == 'INFO':
                # Для INFO используем цвет модуля для всего сообщения
                timestamp_color = module_color_code
                module_color = module_color_code
                message_color = module_color_code
                level_color = module_color_code
            elif level == 'WARNING':
                # Желтый для WARNING
                timestamp_color = self.color_codes['yellow']
                module_color = self.color_codes['yellow']
                message_color = self.color_codes['yellow']
                level_color = self.color_codes['yellow']
            elif level == 'ERROR':
                # Красный для ERROR
                timestamp_color = self.color_codes['red']
                module_color = self.color_codes['red']
                message_color = self.color_codes['red']
                level_color = self.color_codes['red']
            elif level == 'CRITICAL':
                # Темно-красный/белый на красном для CRITICAL
                timestamp_color = self.color_codes['red_bg']
                module_color = self.color_codes['red_bg']
                message_color = self.color_codes['red_bg']
                level_color = self.color_codes['red_bg']
            else:  # DEBUG и другие
                # Для DEBUG используем голубой
                timestamp_color = self.color_codes['cyan']
                module_color = self.color_codes['cyan']
                message_color = self.color_codes['cyan']
                level_color = self.color_codes['cyan']

            # Форматируем с цветами
            timestamp = self.formatTime(record)
            module_name = record.name
            level_name = record.levelname
            message = record.getMessage()

            formatted = (
                f"{timestamp_color}{timestamp}{self.color_codes['reset']} - "
                f"{module_color}{module_name:20}{self.color_codes['reset']} - "
                f"{level_color}{level_name:8}{self.color_codes['reset']} - "
                f"{message_color}{message}{self.color_codes['reset']}"
            )

            return formatted

    formatter = ModuleNameColoredFormatter(
        '%(asctime)s - %(name)-20s - %(levelname)-8s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Получаем корневой логгер
    root_logger = logging.getLogger()

    # Очищаем существующие обработчики
    if root_logger.handlers:
        root_logger.handlers.clear()

    # Создаем и добавляем обработчик
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    # Отключаем распространение для дочерних логгеров
    root_logger.propagate = False

    return root_logger


# Автоматически настраиваем при импорте
logger = setup_colored_logging()


# Дополнительные логгеры для удобства
def get_module_logger(module_name):
    """Получить логгер для конкретного модуля"""
    logger = logging.getLogger(module_name)
    return logger