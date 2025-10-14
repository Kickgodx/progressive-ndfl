"""
Диалоговое окно истории расчетов
"""

import tkinter as tk
from tkinter import ttk, messagebox


class HistoryDialog:
    """Диалоговое окно для отображения и управления историей расчетов"""

    def __init__(self, parent, history_manager):
        """
        Инициализация диалога истории

        Args:
            parent: Родительское окно
            history_manager: Менеджер истории
        """
        self.parent = parent
        self.history_manager = history_manager
        self.window = None
        self.history = []
        self.history_listbox = None

    def show(self):
        """Показать окно истории"""
        self.history = self.history_manager.get_history(20)

        if not self.history:
            messagebox.showinfo("История", "История расчетов пуста")
            return None

        # Создаем окно истории
        self.window = tk.Toplevel(self.parent)
        self.window.title("История расчетов")
        self.window.geometry("900x400")

        # Список истории
        history_frame = ttk.Frame(self.window)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(
            history_frame, text="Последние расчеты:", font=("Arial", 10, "bold")
        ).pack(anchor=tk.W)

        self.history_listbox = tk.Listbox(history_frame, height=15)
        self.history_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # Первоначальное заполнение списка
        self._refresh_history_list()

        # Кнопки управления
        self._create_buttons(history_frame)

        return self.window

    def _refresh_history_list(self):
        """Обновить список истории"""
        self.history = self.history_manager.get_history(20)
        self.history_listbox.delete(0, tk.END)

        if not self.history:
            self.window.destroy()
            messagebox.showinfo("История", "История расчетов пуста")
            return

        for i, calc in enumerate(reversed(self.history)):
            timestamp = calc["timestamp"][:19].replace("T", " ")
            calc_type = (
                "Gross→Netto" if calc["calc_type"] == "gross" else "Netto→Gross"
            )
            gross = f"{calc['gross_income']:,.0f}".replace(",", " ")
            netto = f"{calc['netto_income']:,.0f}".replace(",", " ")
            monthly_gross = calc["monthly_gross"]
            monthly_netto = calc["monthly_netto"]

            self.history_listbox.insert(
                tk.END,
                f"{timestamp} | {calc_type} | Gross: {gross} руб. | Netto: {netto} руб. | Monthly AVG Gross: {monthly_gross} руб. | Monthly AVG Netto: {monthly_netto} руб.",
            )

    def _create_buttons(self, parent_frame):
        """Создать кнопки управления"""
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(
            button_frame, text="Загрузить выбранный", command=self._load_selected
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            button_frame, text="Удалить выбранный", command=self._delete_selected
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            button_frame, text="Очистить историю", command=self._clear_history
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(button_frame, text="Закрыть", command=self.window.destroy).pack(
            side=tk.RIGHT
        )

    def _load_selected(self):
        """Загрузить выбранный расчет"""
        selection = self.history_listbox.curselection()
        if not selection:
            return

        index = len(self.history) - 1 - selection[0]  # Обратный индекс
        calc = self.history[index]

        # Возвращаем выбранные данные родительскому окну
        self.parent.load_calculation_from_history(calc)
        self.window.destroy()

    def _delete_selected(self):
        """Удалить выбранную запись"""
        selection = self.history_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return

        index = len(self.history) - 1 - selection[0]  # Обратный индекс
        if self.history_manager.delete_calculation(index):
            # Обновляем список на месте без уведомления
            self._refresh_history_list()
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить запись")

    def _clear_history(self):
        """Очистить всю историю"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю расчетов?"):
            self.history_manager.clear_history()
            messagebox.showinfo("Успех", "История очищена")
            self.window.destroy()

