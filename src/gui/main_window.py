#!/usr/bin/env python3
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
    quant
)


class TaxApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Прогрессивный калькулятор НДФЛ РФ (с 2025)")
        self.geometry("1000x700")
        self.resizable(True, True)
        self.minsize(800, 600)  # Минимальный размер окна

        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)
        
        # Настройка весов для адаптивности
        frm.grid_columnconfigure(1, weight=1)
        frm.grid_rowconfigure(7, weight=1)

        # Выбор типа расчета
        ttk.Label(frm, text="Тип расчета:", font=('Arial', 10, 'bold')).grid(column=0, row=0, sticky=tk.W, pady=(0,5))
        
        self.calc_type = tk.StringVar(value="gross")
        ttk.Radiobutton(frm, text="Доход до налогов (gross)", variable=self.calc_type, value="gross", 
                       command=self.on_calc_type_change).grid(column=0, row=1, sticky=tk.W)
        ttk.Radiobutton(frm, text="Доход после налогов (netto)", variable=self.calc_type, value="netto",
                       command=self.on_calc_type_change).grid(column=0, row=2, sticky=tk.W, pady=(0,10))

        # Поля ввода
        self.income_label = ttk.Label(frm, text="Годовой доход (руб.):")
        self.income_label.grid(column=0, row=3, sticky=tk.W)
        self.annual_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.annual_var, width=30).grid(column=1, row=3, sticky=tk.W+tk.E)

        ttk.Label(frm, text="ИЛИ 12 месячных доходов (через запятую):").grid(column=0, row=4, sticky=tk.W, pady=(8,0))
        self.monthly_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.monthly_var, width=90).grid(column=0, columnspan=3, row=5, sticky=tk.W+tk.E)

        self.calc_btn = ttk.Button(frm, text="Рассчитать", command=self.on_calculate)
        self.calc_btn.grid(column=0, row=6, pady=(12, 6), sticky=tk.W)

        ttk.Button(frm, text="Пример: 6 000 000", command=self.fill_example).grid(column=1, row=6, padx=(6,0), sticky=tk.W)

        self.out_text = tk.Text(frm, width=120, height=30, wrap=tk.WORD)
        self.out_text.grid(column=0, row=7, columnspan=3, pady=(10,0), sticky=tk.W+tk.E+tk.N+tk.S)

        # подсказки / источники
        ttk.Label(frm, text="Ставки: 13% до 2,4M; 15% 2,4–5M; 18% 5–20M; 20% 20–50M; 22% свыше 50M (введено с 2025).").grid(column=0, row=8, columnspan=3, sticky=tk.W, pady=(8,0))

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
        self.out_text.delete('1.0', tk.END)
        # читаем месячные, если заданы
        months_str = self.monthly_var.get().strip()
        monthly = None
        if months_str:
            try:
                parts = [p.strip() for p in months_str.split(',') if p.strip() != '']
                if len(parts) not in (1, 12):
                    raise ValueError("Введите либо 12 чисел по месяцам, либо одно число (будет интерпретировано как одинаковый месячный доход).")
                # если одно число — повторим 12 раз
                if len(parts) == 1:
                    val = Decimal(parts[0].replace('_',''))
                    monthly = [quant(val) for _ in range(12)]
                else:
                    monthly = [quant(Decimal(x.replace('_',''))) for x in parts]
            except Exception as e:
                messagebox.showerror("Ошибка ввода месячных", f"Неверный формат месячных доходов: {e}")
                return

        # если месячные заданы, суммируем в годовой
        annual_input = self.annual_var.get().strip()
        if annual_input == "" and monthly is None:
            messagebox.showinfo("Нет данных", "Введите годовой доход или месячные доходы.")
            return

        if annual_input:
            try:
                annual = quant(Decimal(annual_input.replace('_','')))
            except Exception as e:
                messagebox.showerror("Ошибка ввода", f"Неверный формат годового дохода: {e}")
                return
        else:
            annual = sum(monthly) if monthly is not None else Decimal('0')

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
            gross_income, total_tax, breakdown = calculate_gross_from_netto(netto_income)

        # Вывод
        out_lines = []
        out_lines.append(f"Тип расчета: {'Доход до налогов (gross)' if calc_type == 'gross' else 'Доход после налогов (netto)'}")
        out_lines.append("")
        out_lines.append(f"Годовой доход до налогов (gross): {gross_income:,} руб.".replace(',', ' '))
        out_lines.append(f"Годовой доход после налогов (netto): {netto_income:,} руб.".replace(',', ' '))
        out_lines.append(f"Средний месячный доход до налогов: {gross_income / 12:,} руб.".replace(',', ' '))
        out_lines.append(f"Средний месячный доход после налогов: {netto_income / 12:,} руб.".replace(',', ' '))
        out_lines.append(f"Общая сумма налога: {total_tax:,} руб. (округление до копеек)".replace(',', ' '))
        eff_rate = (total_tax / gross_income * 100) if gross_income > 0 else Decimal('0')
        out_lines.append(f"Эффективная ставка: {quant(eff_rate):.2f}%")
        out_lines.append("")
        out_lines.append("Разбивка по ступеням (нижняя — верхняя, ставка, налогооблагаемая часть, налог):")
        for lower, upper, rate, taxable, tax in breakdown:
            lb = f"{int(lower):,}".replace(',', ' ') if lower is not None else "0"
            ub = f"{int(upper):,}".replace(',', ' ') if upper is not None else "∞"
            out_lines.append(f"  {lb} — {ub} руб. | {rate * 100:.0f}% | Налогооблагаемая часть: {taxable:,} руб. | Налог: {tax:,} руб.".replace(',', ' '))

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
                        prev_tax, _ = calculate_tax_by_annual(cum[i-2])
                        month_tax = total_tax - prev_tax
                    
                    month_netto = monthly_gross[i-1] - month_tax
                    out_lines.append(f"  Месяц {i:2d}: netto = {monthly[i-1]:,} руб., gross = {monthly_gross[i-1]:,} руб., кумулятивно gross = {val:,} руб. (чистая зарплата за месяц: {month_netto:,} руб.)".replace(',', ' '))
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
                        prev_tax, _ = calculate_tax_by_annual(cum[i-2])
                        month_tax = total_tax - prev_tax
                    
                    month_netto = monthly[i-1] - month_tax
                    out_lines.append(f"  Месяц {i:2d}: gross = {monthly[i-1]:,} руб., кумулятивно = {val:,} руб. (чистая месячная: {month_netto:,} руб.)".replace(',', ' '))
            out_lines.append("")
            out_lines.append("Когда достигнуты пороги (порог -> месяц, кумулятивная сумма):")
            for threshold, (mth, csum) in reached.items():
                if mth is None:
                    out_lines.append(f"  {threshold:,} руб.: НЕ достигнут в течение года".replace(',', ' '))
                else:
                    out_lines.append(f"  {threshold:,} руб.: достигнут в месяце {mth}, кумулятивно = {csum:,} руб.".replace(',', ' '))

        # Пример: показать, какая часть дохода облагается по каждой ставке (полезно для понимания)
        out_lines.append("\nПримечание: повышенные ставки применяются только к сумме превышения соответствующих порогов (маргинальная схема).")
        self.out_text.insert(tk.END, "\n".join(out_lines))
