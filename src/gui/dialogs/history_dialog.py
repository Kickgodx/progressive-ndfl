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
        self.search_var = None
        self.filtered_history = []
        self.results_label = None
        self.search_active = False  # Флаг активности поиска

    def show(self):
        """Показать окно истории"""
        self.history = self.history_manager.get_history(50)

        if not self.history:
            messagebox.showinfo("История", "История расчетов пуста")
            return None

        # Создаем окно истории
        self.window = tk.Toplevel(self.parent)
        self.window.title("История расчетов")
        self.window.geometry("950x500")

        # Список истории
        history_frame = ttk.Frame(self.window)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(
            history_frame, text="Последние расчеты:", font=("Arial", 10, "bold")
        ).pack(anchor=tk.W)

        # Поле поиска
        search_frame = ttk.Frame(history_frame)
        search_frame.pack(fill=tk.X, pady=(5, 5))

        ttk.Label(search_frame, text="🔍 Поиск:").pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar()

        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Привязываем Enter к поиску
        search_entry.bind("<Return>", lambda e: self._on_search())

        find_btn = ttk.Button(
            search_frame, text="Найти", width=10, command=self._on_search
        )
        find_btn.pack(side=tk.LEFT, padx=(5, 0))

        clear_btn = ttk.Button(
            search_frame, text="Сбросить", width=10, command=self._clear_search
        )
        clear_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Подсказка по поиску и счетчик результатов
        info_frame = ttk.Frame(history_frame)
        info_frame.pack(fill=tk.X, anchor=tk.W)

        ttk.Label(
            info_frame,
            text="Поиск по типу (gross/netto), сумме или дате",
            font=("Arial", 8),
            foreground="gray",
        ).pack(side=tk.LEFT)

        self.results_label = ttk.Label(
            info_frame,
            text="",
            font=("Arial", 8, "bold"),
            foreground="blue",
        )
        self.results_label.pack(side=tk.LEFT, padx=(10, 0))

        self.history_listbox = tk.Listbox(history_frame, height=15)
        self.history_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # Первоначальное заполнение списка
        self._refresh_history_list()

        # Кнопки управления
        self._create_buttons(history_frame)

        return self.window

    def _refresh_history_list(self):
        """Обновить список истории"""
        self.history_listbox.delete(0, tk.END)

        if not self.history:
            return

        # Применяем фильтр если поиск активен
        display_history = self.filtered_history if self.search_active else self.history

        # Обновляем счетчик результатов
        if self.search_active:
            self.results_label.config(
                text=f"Найдено: {len(self.filtered_history)} из {len(self.history)}"
            )
        else:
            self.results_label.config(text=f"Всего записей: {len(self.history)}")

        for i, calc in enumerate(reversed(display_history)):
            timestamp = calc["timestamp"][:19].replace("T", " ")
            calc_type = "Gross→Netto" if calc["calc_type"] == "gross" else "Netto→Gross"
            gross = f"{calc['gross_income']:,.0f}".replace(",", " ")
            netto = f"{calc['netto_income']:,.0f}".replace(",", " ")

            # Форматируем месячные суммы для отображения
            monthly_gross = calc.get("monthly_gross", 0)
            monthly_netto = calc.get("monthly_netto", 0)
            monthly_gross_str = (
                f"{monthly_gross:,.0f}".replace(",", " ")
                if isinstance(monthly_gross, (int, float))
                else str(monthly_gross)
            )
            monthly_netto_str = (
                f"{monthly_netto:,.0f}".replace(",", " ")
                if isinstance(monthly_netto, (int, float))
                else str(monthly_netto)
            )

            self.history_listbox.insert(
                tk.END,
                f"{timestamp} | {calc_type} | Gross: {gross} руб. | Netto: {netto} руб. | Monthly AVG Gross: {monthly_gross_str} руб. | Monthly AVG Netto: {monthly_netto_str} руб.",
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

    def _on_search(self):
        """Обработчик поиска"""
        search_text = self.search_var.get().lower().strip()

        if not search_text:
            self.search_active = False
            self.filtered_history = []
            self._refresh_history_list()
            return

        # Фильтруем историю
        self.filtered_history = []
        for calc in self.history:
            # Поиск по различным полям
            timestamp = calc["timestamp"][:19].replace("T", " ")
            calc_type = "gross" if calc["calc_type"] == "gross" else "netto"
            gross = str(int(calc["gross_income"]))
            netto = str(int(calc["netto_income"]))

            # Получаем месячные суммы как числа
            monthly_gross = calc.get("monthly_gross", 0)
            monthly_netto = calc.get("monthly_netto", 0)

            # Конвертируем в строку для поиска (если число, то без пробелов)
            monthly_gross_str = (
                str(int(monthly_gross))
                if isinstance(monthly_gross, (int, float))
                else str(monthly_gross).replace(" ", "")
            )
            monthly_netto_str = (
                str(int(monthly_netto))
                if isinstance(monthly_netto, (int, float))
                else str(monthly_netto).replace(" ", "")
            )

            # Проверяем совпадение
            if (
                search_text in timestamp.lower()
                or search_text in calc_type.lower()
                or search_text in gross
                or search_text in netto
                or search_text in monthly_gross_str
                or search_text in monthly_netto_str
            ):
                self.filtered_history.append(calc)

        # Активируем поиск
        self.search_active = True

        # Если ничего не найдено, показываем сообщение
        if not self.filtered_history:
            messagebox.showinfo(
                "Поиск",
                f"По запросу '{search_text}' ничего не найдено.\n"
                f"Попробуйте: 'gross', 'netto', или часть суммы/даты.",
            )

        self._refresh_history_list()

    def _clear_search(self):
        """Очистить поиск"""
        self.search_var.set("")
        self.filtered_history = []
        self.search_active = False
        self._refresh_history_list()

    def _load_selected(self):
        """Загрузить выбранный расчет"""
        selection = self.history_listbox.curselection()
        if not selection:
            return

        # Используем правильный список для получения индекса
        display_history = self.filtered_history if self.search_active else self.history
        index = len(display_history) - 1 - selection[0]  # Обратный индекс
        calc = display_history[index]

        # Возвращаем выбранные данные родительскому окну
        self.parent.load_calculation_from_history(calc)
        self.window.destroy()

    def _delete_selected(self):
        """Удалить выбранную запись"""
        selection = self.history_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return

        # Используем правильный список для получения индекса
        display_history = self.filtered_history if self.search_active else self.history
        index = len(display_history) - 1 - selection[0]  # Обратный индекс

        # Находим оригинальный индекс в полной истории
        calc_to_delete = display_history[index]
        original_index = self.history.index(calc_to_delete)

        if self.history_manager.delete_calculation(original_index):
            # Перезагружаем историю из файла
            self.history = self.history_manager.get_history(50)
            # Очищаем поиск и обновляем список
            self._clear_search()
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить запись")

    def _clear_history(self):
        """Очистить всю историю"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю расчетов?"):
            self.history_manager.clear_history()
            self.history = []
            messagebox.showinfo("Успех", "История очищена")
            self.window.destroy()
