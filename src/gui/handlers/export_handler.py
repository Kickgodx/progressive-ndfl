"""
Обработчик экспорта данных
"""

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
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
            return

        export_to_txt(results_text, parent_window)

    @staticmethod
    def export_csv(calculation_data, parent_window):
        """
        Экспорт в CSV файл

        Args:
            calculation_data: Данные расчета
            parent_window: Родительское окно для диалогов
        """
        if not calculation_data:
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
            return

        export_to_csv(calculation_data, parent_window)

    @staticmethod
    def export_json(calculation_data, parent_window):
        """
        Экспорт в JSON файл

        Args:
            calculation_data: Данные расчета
            parent_window: Родительское окно для диалогов
        """
        if not calculation_data:
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
            return

        export_to_json(calculation_data, parent_window)

    @staticmethod
    def export_excel(calculation_data, parent_window):
        """
        Экспорт в Excel файл

        Args:
            calculation_data: Данные расчета
            parent_window: Родительское окно для диалогов
        """
        if not calculation_data:
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
            return

        export_to_excel(calculation_data, parent_window)

    @staticmethod
    def export_pdf(calculation_data, parent_window):
        """
        Экспорт в PDF файл

        Args:
            calculation_data: Данные расчета
            parent_window: Родительское окно для диалогов
        """
        if not calculation_data:
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
            return

        export_to_pdf(calculation_data, parent_window)
