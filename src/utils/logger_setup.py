"""
Модуль настройки логирования для приложения
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


class DualOutput:
    """Класс для дублирования вывода в консоль и файл"""

    def __init__(self, file_handle, original_stream):
        self.file = file_handle
        self.original = original_stream

    def write(self, message):
        """Запись в оба потока"""
        if self.original is not None:
            try:
                self.original.write(message)
                self.original.flush()
            except Exception:
                pass  # Игнорируем ошибки консоли (когда .exe без консоли)
        self.file.write(message)
        self.file.flush()

    def flush(self):
        """Flush обоих потоков"""
        if self.original is not None:
            try:
                self.original.flush()
            except Exception:
                pass
        self.file.flush()


def setup_logging(log_dir: str = "history", log_prefix: str = "app_log"):
    """
    Настройка логирования приложения

    Args:
        log_dir: Директория для логов
        log_prefix: Префикс имени файла лога
    """
    # Создаем папку для логов если её нет
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Создаем имя файла с датой и временем
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"{log_prefix}_{timestamp}.log"
    error_log_file = log_path / f"{log_prefix}_{timestamp}_errors.log"

    # Создаем обработчик для основного лога (INFO и выше)
    main_handler = logging.FileHandler(log_file, encoding="utf-8", mode="w")
    main_handler.setLevel(logging.INFO)
    main_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    # Создаем обработчик для лога ошибок (только ERROR и CRITICAL)
    error_handler = logging.FileHandler(error_log_file, encoding="utf-8", mode="w")
    error_handler.setLevel(logging.WARN)
    error_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s\n%(pathname)s:%(lineno)d\n",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    # Обработчик для консоли (если есть)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    )

    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(main_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)

    # Перенаправляем stderr в файл ошибок (для необработанных исключений)
    try:
        error_file = open(error_log_file, "a", encoding="utf-8")
        sys.stderr = DualOutput(error_file, sys.__stderr__)
    except Exception as e:
        logging.error(f"Не удалось настроить перенаправление stderr: {e}")

    logging.info("Логирование успешно настроено")
    logging.info(f"Основной лог: {log_file}")
    logging.info(f"Лог ошибок: {error_log_file}")

    return log_file, error_log_file


def log_exception(exc_type, exc_value, exc_traceback):
    """
    Обработчик необработанных исключений

    Args:
        exc_type: Тип исключения
        exc_value: Значение исключения
        exc_traceback: Traceback исключения
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # Не логируем KeyboardInterrupt
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.critical(
        "Необработанное исключение",
        exc_info=(exc_type, exc_value, exc_traceback),
    )


def setup_exception_handling():
    """Настройка обработки необработанных исключений"""
    sys.excepthook = log_exception
    logging.info("Обработка исключений настроена")


def cleanup_old_logs(log_dir: str = "history", max_logs: int = 10):
    """
    Очистка старых файлов логов

    Args:
        log_dir: Директория с логами
        max_logs: Максимальное количество файлов логов для хранения
    """
    try:
        log_path = Path(log_dir)
        if not log_path.exists():
            return

        # Получаем все файлы логов
        main_log_files = sorted(
            [
                f
                for f in log_path.glob("app_log_*.log")
                if not f.stem.endswith("_errors")
            ],
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )
        error_log_files = sorted(
            log_path.glob("app_log_*_errors.log"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )

        # Удаляем старые основные логи (оставляем только max_logs последних)
        for log_file in main_log_files[max_logs:]:
            log_file.unlink()
            logging.info(f"Удален старый лог: {log_file}")

        # Удаляем старые логи ошибок (оставляем только max_logs последних)
        for error_file in error_log_files[max_logs:]:
            error_file.unlink()
            logging.info(f"Удален старый лог ошибок: {error_file}")

    except Exception as e:
        logging.warning(f"Ошибка при очистке старых логов: {e}")
