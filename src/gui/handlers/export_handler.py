"""
Обработчик экспорта данных
"""

import logging
from tkinter import messagebox
from ...utils import (
    export_to_txt,
    export_to_csv,
    export_to_json,
    export_to_excel,
    export_to_pdf,
)


class ExportHandler:
    """Обработчик экспорта результатов в различные форматы"""

    @staticmethod
    def export_txt(calculation_data, results_text, parent_window):
        """
        Экспорт в текстовый файл

        Args:
            calculation_data: Данные расчета
            results_text: Текст результатов
            parent_window: Родительское окно для диалогов
        """
        if not calculation_data:
            logging.warning("Попытка экспорта в TXT без данных расчета")
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
            return

        try:
            logging.info("Начало экспорта в TXT")
            export_to_txt(results_text, parent_window)
            logging.info("Экспорт в TXT завершен")
        except Exception as e:
            logging.exception(f"Ошибка при экспорте в TXT: {e}")
            raise

    @staticmethod
    def export_csv(calculation_data, parent_window):
        """
        Экспорт в CSV файл

        Args:
            calculation_data: Данные расчета
            parent_window: Родительское окно для диалогов
        """
        if not calculation_data:
            logging.warning("Попытка экспорта в CSV без данных расчета")
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
            return

        try:
            logging.info("Начало экспорта в CSV")
            export_to_csv(calculation_data, parent_window)
            logging.info("Экспорт в CSV завершен")
        except Exception as e:
            logging.exception(f"Ошибка при экспорте в CSV: {e}")
            raise

    @staticmethod
    def export_json(calculation_data, parent_window):
        """
        Экспорт в JSON файл

        Args:
            calculation_data: Данные расчета
            parent_window: Родительское окно для диалогов
        """
        if not calculation_data:
            logging.warning("Попытка экспорта в JSON без данных расчета")
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
            return

        try:
            logging.info("Начало экспорта в JSON")
            export_to_json(calculation_data, parent_window)
            logging.info("Экспорт в JSON завершен")
        except Exception as e:
            logging.exception(f"Ошибка при экспорте в JSON: {e}")
            raise

    @staticmethod
    def export_excel(calculation_data, parent_window):
        """
        Экспорт в Excel файл

        Args:
            calculation_data: Данные расчета
            parent_window: Родительское окно для диалогов
        """
        if not calculation_data:
            logging.warning("Попытка экспорта в Excel без данных расчета")
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
            return

        try:
            logging.info("Начало экспорта в Excel")
            export_to_excel(calculation_data, parent_window)
            logging.info("Экспорт в Excel завершен")
        except Exception as e:
            logging.exception(f"Ошибка при экспорте в Excel: {e}")
            raise

    @staticmethod
    def export_pdf(calculation_data, parent_window):
        """
        Экспорт в PDF файл

        Args:
            calculation_data: Данные расчета
            parent_window: Родительское окно для диалогов
        """
        if not calculation_data:
            logging.warning("Попытка экспорта в PDF без данных расчета")
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
            return

        try:
            logging.info("Начало экспорта в PDF")
            export_to_pdf(calculation_data, parent_window)
            logging.info("Экспорт в PDF завершен")
        except Exception as e:
            logging.exception(f"Ошибка при экспорте в PDF: {e}")
            raise
