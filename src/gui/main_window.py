"""
Главное окно приложения
"""

import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal

from ..calculators import (
    calculate_tax_by_annual,
    calculate_gross_from_netto,
    months_when_thresholds_reached,
    quant,
)
from ..utils import (
    export_to_txt,
    export_to_csv,
    export_to_json,
    export_to_excel,
    HistoryManager,
    InputValidator,
    create_charts_frame,
    has_monthly_data,
)


class TaxApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Прогрессивный калькулятор НДФЛ РФ (с 2025)")
        self.geometry("1000x700")
        self.resizable(True, True)
        self.minsize(800, 600)  # Минимальный размер окна

        # Инициализация утилит
        self.history_manager = HistoryManager()
        self.current_calculation_data = {}

        # Настройка горячих клавиш
        self.setup_shortcuts()

        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        # Настройка весов для адаптивности
        frm.grid_columnconfigure(1, weight=1)
        frm.grid_rowconfigure(7, weight=1)

        # Выбор типа расчета
        ttk.Label(frm, text="Тип расчета:", font=("Arial", 10, "bold")).grid(
            column=0, row=0, sticky=tk.W, pady=(0, 5)
        )

        self.calc_type = tk.StringVar(value="gross")
        ttk.Radiobutton(
            frm,
            text="Доход до налогов (gross)",
            variable=self.calc_type,
            value="gross",
            command=self.on_calc_type_change,
        ).grid(column=0, row=1, sticky=tk.W)
        ttk.Radiobutton(
            frm,
            text="Доход после налогов (netto)",
            variable=self.calc_type,
            value="netto",
            command=self.on_calc_type_change,
        ).grid(column=0, row=2, sticky=tk.W, pady=(0, 10))

        # Поля ввода
        self.income_label = ttk.Label(frm, text="Годовой доход (руб.):")
        self.income_label.grid(column=0, row=3, sticky=tk.W)
        self.annual_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.annual_var, width=30).grid(
            column=1, row=3, sticky=tk.W + tk.E
        )

        ttk.Label(frm, text="ИЛИ 12 месячных доходов (через запятую):").grid(
            column=0, row=4, sticky=tk.W, pady=(8, 0)
        )
        self.monthly_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.monthly_var, width=90).grid(
            column=0, columnspan=3, row=5, sticky=tk.W + tk.E
        )

        # Кнопки управления
        button_frame = ttk.Frame(frm)
        button_frame.grid(column=0, row=6, columnspan=3, pady=(12, 6), sticky=tk.W)

        self.calc_btn = ttk.Button(
            button_frame, text="Рассчитать", command=self.on_calculate
        )
        self.calc_btn.grid(column=0, row=0, sticky=tk.W)

        ttk.Button(
            button_frame, text="Пример: 6 000 000", command=self.fill_example
        ).grid(column=1, row=0, padx=(6, 0), sticky=tk.W)

        # Кнопки экспорта
        export_frame = ttk.Frame(frm)
        export_frame.grid(column=0, row=6, columnspan=3, pady=(12, 6), sticky=tk.E)

        ttk.Button(export_frame, text="📄 TXT", command=self.export_txt).grid(
            column=0, row=0, padx=(0, 3)
        )
        ttk.Button(export_frame, text="📊 CSV", command=self.export_csv).grid(
            column=1, row=0, padx=(0, 3)
        )
        ttk.Button(export_frame, text="📋 JSON", command=self.export_json).grid(
            column=2, row=0, padx=(0, 3)
        )
        ttk.Button(export_frame, text="📈 Excel", command=self.export_excel).grid(
            column=3, row=0, padx=(0, 3)
        )

        # Кнопка истории
        history_frame = ttk.Frame(frm)
        history_frame.grid(column=0, row=6, columnspan=3, pady=(12, 6), sticky=tk.E)

        ttk.Button(history_frame, text="📚 История", command=self.show_history).grid(
            column=0, row=0, padx=(0, 3)
        )

        # Создаем Notebook для вкладок
        self.notebook = ttk.Notebook(frm)
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

        # Вкладка с графиками (будет заполняться динамически)
        self.chart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chart_frame, text="📊 Графики", state="disabled")

        # подсказки / источники
        ttk.Label(
            frm,
            text="Ставки: 13% до 2,4M; 15% 2,4–5M; 18% 5–20M; 20% 20–50M; 22% свыше 50M (введено с 2025).",
        ).grid(column=0, row=8, columnspan=3, sticky=tk.W, pady=(8, 0))

    def on_calc_type_change(self):
        """Обновить подписи полей в зависимости от выбранного типа расчета"""
        if self.calc_type.get() == "gross":
            self.income_label.config(text="Годовой доход до налогов (руб.):")
        else:
            self.income_label.config(text="Годовой доход после налогов (руб.):")

    def fill_example(self):
        self.annual_var.set("6000000")
        self.monthly_var.set("")

    def on_calculate(self):
        self.out_text.delete("1.0", tk.END)

        # Валидация ввода с помощью нового валидатора
        annual_input = self.annual_var.get().strip()
        monthly_input = self.monthly_var.get().strip()

        is_valid, error_msg, validated_data = (
            InputValidator.validate_calculation_inputs(annual_input, monthly_input)
        )

        if not is_valid:
            messagebox.showerror("Ошибка ввода", error_msg)
            return

        # Получаем валидированные данные
        if "annual" in validated_data:
            annual = quant(validated_data["annual"])
            monthly = None
        else:
            monthly = [quant(x) for x in validated_data["monthly"]]
            annual = sum(monthly)

        # Определяем тип расчета и выполняем соответствующие вычисления
        calc_type = self.calc_type.get()

        if calc_type == "gross":
            # Обычный расчет: gross -> netto
            gross_income = annual
            total_tax, breakdown = calculate_tax_by_annual(gross_income)
            netto_income = gross_income - total_tax
        else:
            # Обратный расчет: netto -> gross
            netto_income = annual
            gross_income, total_tax, breakdown = calculate_gross_from_netto(
                netto_income
            )

        # Вывод
        out_lines = []
        out_lines.append(
            f"Тип расчета: {'Доход до налогов (gross)' if calc_type == 'gross' else 'Доход после налогов (netto)'}"
        )
        out_lines.append("")
        out_lines.append(
            f"Годовой доход до налогов (gross): {gross_income:,} руб.".replace(",", " ")
        )
        out_lines.append(
            f"Годовой доход после налогов (netto): {netto_income:,} руб.".replace(
                ",", " "
            )
        )
        out_lines.append(
            f"Средний месячный доход до налогов: {gross_income / 12:,} руб.".replace(
                ",", " "
            )
        )
        out_lines.append(
            f"Средний месячный доход после налогов: {netto_income / 12:,} руб.".replace(
                ",", " "
            )
        )
        out_lines.append(
            f"Общая сумма налога: {total_tax:,} руб. (округление до копеек)".replace(
                ",", " "
            )
        )
        eff_rate = (
            (total_tax / gross_income * 100) if gross_income > 0 else Decimal("0")
        )
        out_lines.append(f"Эффективная ставка: {quant(eff_rate):.2f}%")
        out_lines.append("")
        out_lines.append(
            "Разбивка по ступеням (нижняя — верхняя, ставка, налогооблагаемая часть, налог):"
        )
        for lower, upper, rate, taxable, tax in breakdown:
            lb = f"{int(lower):,}".replace(",", " ") if lower is not None else "0"
            ub = f"{int(upper):,}".replace(",", " ") if upper is not None else "∞"
            out_lines.append(
                f"  {lb} — {ub} руб. | {rate * 100:.0f}% | Налогооблагаемая часть: {taxable:,} руб. | Налог: {tax:,} руб.".replace(
                    ",", " "
                )
            )

        # Если имеются месячные — показать кумулятивы и когда достигаются пороги
        if monthly is not None:
            out_lines.append("\nЕжемесячные данные (кумулятивные суммы):")
            # Для месячных данных нужно конвертировать в gross если введены netto
            if calc_type == "netto":
                # Конвертируем каждый месячный netto в gross
                monthly_gross = []
                for netto_month in monthly:
                    gross_month, _, _ = calculate_gross_from_netto(netto_month)
                    monthly_gross.append(gross_month)
                cum, reached = months_when_thresholds_reached(monthly_gross)
                for i, val in enumerate(cum, start=1):
                    # Рассчитываем чистую зарплату за текущий месяц
                    # Налог за весь год до этого месяца
                    if i == 1:
                        # Первый месяц - налог только с этого месяца
                        month_tax, _ = calculate_tax_by_annual(val)
                    else:
                        # Налог с начала года минус налог с предыдущих месяцев
                        total_tax, _ = calculate_tax_by_annual(val)
                        prev_tax, _ = calculate_tax_by_annual(cum[i - 2])
                        month_tax = total_tax - prev_tax

                    month_netto = monthly_gross[i - 1] - month_tax
                    out_lines.append(
                        f"  Месяц {i:2d}: netto = {monthly[i - 1]:,} руб., gross = {monthly_gross[i - 1]:,} руб., кумулятивно gross = {val:,} руб. (чистая зарплата за месяц: {month_netto:,} руб.)".replace(
                            ",", " "
                        )
                    )
            else:
                cum, reached = months_when_thresholds_reached(monthly)
                for i, val in enumerate(cum, start=1):
                    # Рассчитываем чистую зарплату за текущий месяц
                    # Налог за весь год до этого месяца
                    if i == 1:
                        # Первый месяц - налог только с этого месяца
                        month_tax, _ = calculate_tax_by_annual(val)
                    else:
                        # Налог с начала года минус налог с предыдущих месяцев
                        total_tax, _ = calculate_tax_by_annual(val)
                        prev_tax, _ = calculate_tax_by_annual(cum[i - 2])
                        month_tax = total_tax - prev_tax

                    month_netto = monthly[i - 1] - month_tax
                    out_lines.append(
                        f"  Месяц {i:2d}: gross = {monthly[i - 1]:,} руб., кумулятивно = {val:,} руб. (чистая месячная: {month_netto:,} руб.)".replace(
                            ",", " "
                        )
                    )
            out_lines.append("")
            out_lines.append(
                "Когда достигнуты пороги (порог -> месяц, кумулятивная сумма):"
            )
            for threshold, (mth, csum) in reached.items():
                if mth is None:
                    out_lines.append(
                        f"  {threshold:,} руб.: НЕ достигнут в течение года".replace(
                            ",", " "
                        )
                    )
                else:
                    out_lines.append(
                        f"  {threshold:,} руб.: достигнут в месяце {mth}, кумулятивно = {csum:,} руб.".replace(
                            ",", " "
                        )
                    )

        # Пример: показать, какая часть дохода облагается по каждой ставке (полезно для понимания)
        out_lines.append(
            "\nПримечание: повышенные ставки применяются только к сумме превышения соответствующих порогов (маргинальная схема)."
        )
        self.out_text.insert(tk.END, "\n".join(out_lines))

        # Сохраняем данные расчета для экспорта и истории
        self.current_calculation_data = {
            "calc_type": calc_type,
            "gross_income": gross_income,
            "netto_income": netto_income,
            "total_tax": total_tax,
            "eff_rate": eff_rate,
            "breakdown": breakdown,
            "monthly_data": monthly,
            "monthly_gross": f"{gross_income / 12:,.0f}".replace(",", " "),
            "monthly_netto": f"{netto_income / 12:,.0f}".replace(",", " "),
        }

        # Добавляем в историю
        self.history_manager.add_calculation(self.current_calculation_data)

        # Обновляем графики если есть месячные данные
        self.update_charts()

    def setup_shortcuts(self):
        """Настройка горячих клавиш"""
        self.bind("<Control-Return>", lambda e: self.on_calculate())
        self.bind("<Control-s>", lambda e: self.export_txt())
        self.bind("<Control-h>", lambda e: self.show_history())
        self.bind("<F5>", lambda e: self.on_calculate())

    def export_txt(self):
        """Экспорт в текстовый файл"""
        if not self.current_calculation_data:
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
            return

        results_text = self.out_text.get("1.0", tk.END)
        export_to_txt(results_text, self)

    def export_csv(self):
        """Экспорт в CSV файл"""
        if not self.current_calculation_data:
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
            return

        export_to_csv(self.current_calculation_data, self)

    def export_json(self):
        """Экспорт в JSON файл"""
        if not self.current_calculation_data:
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
            return

        export_to_json(self.current_calculation_data, self)

    def export_excel(self):
        """Экспорт в Excel файл"""
        if not self.current_calculation_data:
            messagebox.showwarning("Предупреждение", "Сначала выполните расчет")
            return

        export_to_excel(self.current_calculation_data, self)

    def show_history(self):
        """Показать историю расчетов"""
        history = self.history_manager.get_history(20)  # Последние 20 расчетов

        if not history:
            messagebox.showinfo("История", "История расчетов пуста")
            return

        # Создаем окно истории
        history_window = tk.Toplevel(self)
        history_window.title("История расчетов")
        history_window.geometry("900x400")

        # Список истории
        history_frame = ttk.Frame(history_window)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(
            history_frame, text="Последние расчеты:", font=("Arial", 10, "bold")
        ).pack(anchor=tk.W)

        history_listbox = tk.Listbox(history_frame, height=15)
        history_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # Заполняем список
        for i, calc in enumerate(reversed(history)):
            timestamp = calc["timestamp"][:19].replace("T", " ")
            calc_type = "Gross→Netto" if calc["calc_type"] == "gross" else "Netto→Gross"
            gross = f"{calc['gross_income']:,.0f}".replace(",", " ")
            netto = f"{calc['netto_income']:,.0f}".replace(",", " ")
            monthly_gross = calc["monthly_gross"]
            monthly_netto = calc["monthly_netto"]

            history_listbox.insert(
                tk.END,
                f"{timestamp} | {calc_type} | Gross: {gross} руб. | Netto: {netto} руб. | Monthly AVG Gross: {monthly_gross} руб. | Monthly AVG Netto: {monthly_netto} руб.",
            )

        # Кнопки управления
        button_frame = ttk.Frame(history_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        def load_selected():
            selection = history_listbox.curselection()
            if selection:
                index = len(history) - 1 - selection[0]  # Обратный индекс
                calc = history[index]

                # Заполняем поля
                self.calc_type.set(calc["calc_type"])
                # Обновляем подписи полей после изменения типа расчета
                self.on_calc_type_change()

                if calc["calc_type"] == "gross":
                    self.annual_var.set(str(int(calc["gross_income"])))
                else:
                    self.annual_var.set(str(int(calc["netto_income"])))
                self.monthly_var.set("")

                history_window.destroy()

        ttk.Button(
            button_frame, text="Загрузить выбранный", command=load_selected
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_frame,
            text="Очистить историю",
            command=lambda: self.clear_history(history_window),
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Закрыть", command=history_window.destroy).pack(
            side=tk.RIGHT
        )

    def clear_history(self, parent_window):
        """Очистить историю"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю расчетов?"):
            self.history_manager.clear_history()
            messagebox.showinfo("Успех", "История очищена")
            parent_window.destroy()

    def update_charts(self):
        """Обновить графики"""
        # Проверяем наличие месячных данных
        if has_monthly_data(self.current_calculation_data):
            # Очищаем предыдущие графики
            for widget in self.chart_frame.winfo_children():
                widget.destroy()

            # Создаем новые графики
            monthly_data = self.current_calculation_data.get("monthly_data")
            calc_type = self.current_calculation_data.get("calc_type", "gross")

            # Если введены netto данные, конвертируем в gross для графиков
            if calc_type == "netto":
                from decimal import Decimal

                monthly_gross = []
                for netto_month in monthly_data:
                    # Убеждаемся что данные в Decimal
                    if not isinstance(netto_month, Decimal):
                        netto_month = Decimal(str(netto_month))
                    gross_month, _, _ = calculate_gross_from_netto(netto_month)
                    monthly_gross.append(gross_month)
                monthly_data = monthly_gross
            else:
                # Для gross данных тоже проверяем тип
                from decimal import Decimal

                monthly_data = [
                    d if isinstance(d, Decimal) else Decimal(str(d))
                    for d in monthly_data
                ]

            # Создаем фрейм с графиками
            chart_widget = create_charts_frame(
                self.chart_frame, monthly_data, calc_type
            )
            chart_widget.pack(fill=tk.BOTH, expand=True)

            # Активируем вкладку графиков
            self.notebook.tab(1, state="normal")
        else:
            # Деактивируем вкладку если нет данных
            self.notebook.tab(1, state="disabled")
            # Переключаемся на вкладку результатов
            self.notebook.select(0)
