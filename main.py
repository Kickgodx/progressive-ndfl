import logging
from src.gui import TaxApp
from src.utils import setup_logging, setup_exception_handling, cleanup_old_logs


def main():
    """Запуск приложения"""
    # Настройка логирования
    setup_logging()
    setup_exception_handling()
    cleanup_old_logs()

    logging.info("=" * 50)
    logging.info("Запуск приложения НДФЛ Калькулятор")
    logging.info("=" * 50)

    try:
        app = TaxApp()
        logging.info("Главное окно создано")
        app.mainloop()
        logging.info("Приложение завершено нормально")
    except Exception as e:
        logging.exception(f"Критическая ошибка при запуске приложения: {e}")
        raise


if __name__ == "__main__":
    main()
