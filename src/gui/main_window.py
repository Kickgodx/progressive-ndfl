"""
Главное окно приложения
"""

import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal

from ..calculators import calculate_gross_from_netto
from ..utils import HistoryManager, create_charts_frame, has_monthly_data
from .dialogs import HistoryDialog
from .handlers import CalculationHandler, ExportHandler


class TaxApp(tk.Tk):
    """Главное окно калькулятора НДФЛ"""

    def __init__(self):
        super().__init__()
        self.title("Прогрессивный калькулятор НДФЛ РФ (с 2025)")
        self.geometry("1000x700")
        self.resizable(True, True)
        self.minsize(800, 600)

        # Инициализация компонентов
        self.history_manager = HistoryManager()
        self.calculation_handler = CalculationHandler()
        self.export_handler = ExportHandler()
        self.current_calculation_data = {}

        # Настройка горячих клавиш
        self._setup_shortcuts()

        # Создание интерфейса
        self._create_ui()

    def _create_ui(self):
        """Создать пользовательский интерфейс"""
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        # Настройка весов для адаптивности
        frm.grid_columnconfigure(1, weight=1)
        frm.grid_rowconfigure(7, weight=1)

        # Виджеты интерфейса
        self._create_calculation_type_section(frm)
        self._create_input_section(frm)
        self._create_buttons_section(frm)
        self._create_results_section(frm)
        self._create_footer(frm)

    def _create_calculation_type_section(self, parent):
        """Создать секцию выбора типа расчета"""
        ttk.Label(parent, text="Тип расчета:", font=("Arial", 10, "bold")).grid(
            column=0, row=0, sticky=tk.W, pady=(0, 5)
        )

        self.calc_type = tk.StringVar(value="gross")
        ttk.Radiobutton(
            parent,
            text="Доход до налогов (gross)",
            variable=self.calc_type,
            value="gross",
            command=self._on_calc_type_change,
        ).grid(column=0, row=1, sticky=tk.W)

        ttk.Radiobutton(
            parent,
            text="Доход после налогов (netto)",
            variable=self.calc_type,
            value="netto",
            command=self._on_calc_type_change,
        ).grid(column=0, row=2, sticky=tk.W, pady=(0, 10))

    def _create_input_section(self, parent):
        """Создать секцию ввода данных"""
        self.income_label = ttk.Label(parent, text="Годовой доход (руб.):")
        self.income_label.grid(column=0, row=3, sticky=tk.W)

        self.annual_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.annual_var, width=30).grid(
            column=1, row=3, sticky=tk.W + tk.E
        )

        ttk.Label(parent, text="ИЛИ 12 месячных доходов (через запятую):").grid(
            column=0, row=4, sticky=tk.W, pady=(8, 0)
        )

        self.monthly_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.monthly_var, width=90).grid(
            column=0, columnspan=3, row=5, sticky=tk.W + tk.E
        )

    def _create_buttons_section(self, parent):
        """Создать секцию кнопок"""
        # Кнопки управления
        button_frame = ttk.Frame(parent)
        button_frame.grid(column=0, row=6, columnspan=3, pady=(12, 6), sticky=tk.W)

        self.calc_btn = ttk.Button(
            button_frame, text="Рассчитать", command=self._on_calculate
        )
        self.calc_btn.grid(column=0, row=0, sticky=tk.W)

        ttk.Button(
            button_frame, text="Пример: 6 000 000", command=self._fill_example
        ).grid(column=1, row=0, padx=(6, 0), sticky=tk.W)

        # Кнопки экспорта
        export_frame = ttk.Frame(parent)
        export_frame.grid(column=0, row=6, columnspan=3, pady=(12, 6), sticky=tk.E)

        ttk.Button(export_frame, text="📄 TXT", command=self._export_txt).grid(
            column=0, row=0, padx=(0, 3)
        )
        ttk.Button(export_frame, text="📊 CSV", command=self._export_csv).grid(
            column=1, row=0, padx=(0, 3)
        )
        ttk.Button(export_frame, text="📋 JSON", command=self._export_json).grid(
            column=2, row=0, padx=(0, 3)
        )
        ttk.Button(export_frame, text="📈 Excel", command=self._export_excel).grid(
            column=3, row=0, padx=(0, 3)
        )

        # Кнопка истории
        history_frame = ttk.Frame(parent)
        history_frame.grid(column=0, row=6, columnspan=3, pady=(12, 6), sticky=tk.E)

        ttk.Button(history_frame, text="📚 История", command=self._show_history).grid(
            column=0, row=0, padx=(0, 3)
        )

    def _create_results_section(self, parent):
        """Создать секцию результатов"""
        # Создаем Notebook для вкладок
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(
            column=0,
            row=7,
            columnspan=3,
            pady=(10, 0),
            sticky=tk.W + tk.E + tk.N + tk.S,
        )

        # Вкладка с текстовым выводом
        text_frame = ttk.Frame(self.notebook)
        self.notebook.add(text_frame, text="📄 Результаты")

        self.out_text = tk.Text(text_frame, width=120, height=30, wrap=tk.WORD)
        self.out_text.pack(fill=tk.BOTH, expand=True)

        # Вкладка с графиками
        self.chart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chart_frame, text="📊 Графики", state="disabled")

    def _create_footer(self, parent):
        """Создать футер с подсказками"""
        ttk.Label(
            parent,
            text="Ставки: 13% до 2,4M; 15% 2,4–5M; 18% 5–20M; 20% 20–50M; 22% свыше 50M (введено с 2025).",
        ).grid(column=0, row=8, columnspan=3, sticky=tk.W, pady=(8, 0))

    def _setup_shortcuts(self):
        """Настройка горячих клавиш"""
        self.bind("<Control-Return>", lambda e: self._on_calculate())
        self.bind("<Control-s>", lambda e: self._export_txt())
        self.bind("<Control-h>", lambda e: self._show_history())
        self.bind("<F5>", lambda e: self._on_calculate())

    def _on_calc_type_change(self):
        """Обработчик изменения типа расчета"""
        if self.calc_type.get() == "gross":
            self.income_label.config(text="Годовой доход до налогов (руб.):")
        else:
            self.income_label.config(text="Годовой доход после налогов (руб.):")

    def _fill_example(self):
        """Заполнить пример данных"""
        self.annual_var.set("6000000")
        self.monthly_var.set("")

    def _on_calculate(self):
        """Обработчик кнопки расчета"""
        self.out_text.delete("1.0", tk.END)

        # Валидация ввода
        annual_input = self.annual_var.get().strip()
        monthly_input = self.monthly_var.get().strip()

        is_valid, error_msg, validated_data = self.calculation_handler.validate_inputs(
            annual_input, monthly_input
        )

        if not is_valid:
            messagebox.showerror("Ошибка ввода", error_msg)
            return

        # Выполняем расчет
        calc_type = self.calc_type.get()
        self.current_calculation_data = self.calculation_handler.perform_calculation(
            validated_data, calc_type
        )

        # Форматируем и выводим результаты
        results_text = self.calculation_handler.format_results(
            self.current_calculation_data
        )
        self.out_text.insert(tk.END, results_text)

        # Добавляем в историю
        self.history_manager.add_calculation(self.current_calculation_data)

        # Обновляем графики
        self._update_charts()

    def _export_txt(self):
        """Экспорт в TXT"""
        results_text = self.out_text.get("1.0", tk.END)
        self.export_handler.export_txt(
            self.current_calculation_data, results_text, self
        )

    def _export_csv(self):
        """Экспорт в CSV"""
        self.export_handler.export_csv(self.current_calculation_data, self)

    def _export_json(self):
        """Экспорт в JSON"""
        self.export_handler.export_json(self.current_calculation_data, self)

    def _export_excel(self):
        """Экспорт в Excel"""
        self.export_handler.export_excel(self.current_calculation_data, self)

    def _show_history(self):
        """Показать историю расчетов"""
        dialog = HistoryDialog(self, self.history_manager)
        dialog.show()

    def load_calculation_from_history(self, calc_data):
        """
        Загрузить расчет из истории

        Args:
            calc_data: Данные расчета из истории
        """
        # Заполняем поля
        self.calc_type.set(calc_data["calc_type"])
        self._on_calc_type_change()

        if calc_data["calc_type"] == "gross":
            self.annual_var.set(str(int(calc_data["gross_income"])))
        else:
            self.annual_var.set(str(int(calc_data["netto_income"])))
        self.monthly_var.set("")

    def _update_charts(self):
        """Обновить графики"""
        if not has_monthly_data(self.current_calculation_data):
            self.notebook.tab(1, state="disabled")
            self.notebook.select(0)
            return

        # Очищаем предыдущие графики
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Получаем данные
        monthly_data = self.current_calculation_data.get("monthly_data")
        calc_type = self.current_calculation_data.get("calc_type", "gross")

        # Конвертируем netto в gross если нужно
        if calc_type == "netto":
            monthly_gross = []
            for netto_month in monthly_data:
                if not isinstance(netto_month, Decimal):
                    netto_month = Decimal(str(netto_month))
                gross_month, _, _ = calculate_gross_from_netto(netto_month)
                monthly_gross.append(gross_month)
            monthly_data = monthly_gross
        else:
            monthly_data = [
                d if isinstance(d, Decimal) else Decimal(str(d)) for d in monthly_data
            ]

        # Создаем графики
        chart_widget = create_charts_frame(self.chart_frame, monthly_data, calc_type)
        chart_widget.pack(fill=tk.BOTH, expand=True)

        # Активируем вкладку графиков
        self.notebook.tab(1, state="normal")
