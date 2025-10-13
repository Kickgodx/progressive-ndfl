"""
Утилиты для создания графиков
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from decimal import Decimal


def create_charts_frame(parent, monthly_data, calc_type="gross"):
    """
    Создать фрейм с графиками

    Args:
        parent: родительский виджет
        monthly_data: список месячных доходов (gross) в Decimal
        calc_type: тип расчета ('gross' или 'netto')

    Returns:
        frame с графиками
    """
    from ..calculators import calculate_tax_by_annual

    # Создаем фрейм для графиков
    frame = tk.Frame(parent)

    # Рассчитываем данные для графиков
    cumulative_gross = []
    cumulative_tax = []
    monthly_netto = []

    cum_sum = Decimal(0)
    for i, monthly_income in enumerate(monthly_data):
        # Убеждаемся, что monthly_income - это Decimal
        if not isinstance(monthly_income, Decimal):
            monthly_income = Decimal(str(monthly_income))

        cum_sum += monthly_income
        cumulative_gross.append(cum_sum)

        # Рассчитываем налог
        total_tax, _ = calculate_tax_by_annual(cum_sum)
        cumulative_tax.append(total_tax)

        # Рассчитываем чистую месячную зарплату
        if i == 0:
            month_tax = total_tax
        else:
            prev_tax, _ = calculate_tax_by_annual(cumulative_gross[i - 1])
            month_tax = total_tax - prev_tax

        month_netto = monthly_income - month_tax
        monthly_netto.append(month_netto)

    # Конвертируем Decimal в float для matplotlib
    cumulative_gross_float = [float(x) for x in cumulative_gross]
    cumulative_tax_float = [float(x) for x in cumulative_tax]
    monthly_netto_float = [float(x) for x in monthly_netto]

    # Создаем фигуру с двумя подграфиками
    fig = Figure(figsize=(10, 8), dpi=100)

    # График 1: Кумулятивный доход и налог
    ax1 = fig.add_subplot(2, 1, 1)
    months = list(range(1, 13))

    ax1.plot(
        months,
        cumulative_gross_float,
        marker="o",
        linewidth=2,
        label="Кумулятивный доход",
        color="#2E86AB",
    )
    ax1.plot(
        months,
        cumulative_tax_float,
        marker="s",
        linewidth=2,
        label="Кумулятивный налог",
        color="#A23B72",
    )

    ax1.set_xlabel("Месяц", fontsize=11)
    ax1.set_ylabel("Сумма (руб.)", fontsize=11)
    ax1.set_title(
        "Кумулятивный доход и налог по месяцам", fontsize=13, fontweight="bold"
    )
    ax1.legend(loc="upper left", fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(months)

    # Форматируем ось Y с разделителями тысяч
    ax1.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, p: f"{x:,.0f}".replace(",", " "))
    )

    # График 2: Чистая месячная зарплата
    ax2 = fig.add_subplot(2, 1, 2)

    colors = [
        "#06A77D" if netto >= monthly_netto_float[0] else "#F18F01"
        for netto in monthly_netto_float
    ]
    bars = ax2.bar(
        months,
        monthly_netto_float,
        color=colors,
        alpha=0.7,
        edgecolor="black",
        linewidth=0.5,
    )

    # Добавляем линию средней зарплаты
    avg_netto = sum(monthly_netto_float) / len(monthly_netto_float)
    ax2.axhline(
        y=avg_netto,
        color="red",
        linestyle="--",
        linewidth=1.5,
        label=f"Средняя: {avg_netto:,.0f} руб.".replace(",", " "),
    )

    ax2.set_xlabel("Месяц", fontsize=11)
    ax2.set_ylabel("Чистая зарплата (руб.)", fontsize=11)
    ax2.set_title("Чистая месячная зарплата", fontsize=13, fontweight="bold")
    ax2.legend(loc="lower right", fontsize=10)
    ax2.grid(True, alpha=0.3, axis="y")
    ax2.set_xticks(months)

    # Форматируем ось Y с разделителями тысяч
    ax2.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, p: f"{x:,.0f}".replace(",", " "))
    )

    # Добавляем значения на столбцы (каждый третий месяц для читаемости)
    for i in [0, 3, 6, 9, 11]:
        height = bars[i].get_height()
        ax2.text(
            bars[i].get_x() + bars[i].get_width() / 2.0,
            height,
            f"{int(height):,}".replace(",", " "),
            ha="center",
            va="bottom",
            fontsize=8,
        )

    fig.tight_layout(pad=3.0)

    # Встраиваем график в tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    return frame


def has_monthly_data(calc_data):
    """
    Проверить наличие месячных данных

    Args:
        calc_data: словарь с данными расчета

    Returns:
        bool: True если есть месячные данные
    """
    monthly = calc_data.get("monthly_data")
    return monthly is not None and len(monthly) == 12
