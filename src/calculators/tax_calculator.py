#!/usr/bin/env python3
"""
Модуль для расчета прогрессивного НДФЛ РФ
"""

from decimal import Decimal, ROUND_HALF_UP

# --- Налоговые ступени (верхние границы в рублях, ставка как десятичная)
# формат: (upper_bound, rate). upper_bound == None означает "без ограничения" (бесконечность)
TAX_BRACKETS = [
    (2_400_000, Decimal('0.13')),   # до 2.4 млн — 13%
    (5_000_000, Decimal('0.15')),   # >2.4м до 5м — 15%
    (20_000_000, Decimal('0.18')),  # >5м до 20м — 18%
    (50_000_000, Decimal('0.20')),  # >20м до 50м — 20%
    (None, Decimal('0.22')),        # >50м — 22%
]


def quant(x):
    """Округление до копеек, Decimal"""
    return x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_tax_by_annual(income_rub: Decimal):
    """
    Рассчитать налог по маргинальной шкале для годового дохода.
    Возвращает (total_tax, breakdown_list)
    breakdown_list = [ (lower_bound, upper_bound_or_None, rate, taxable_amount, tax_for_this_bracket), ... ]
    """
    income = max(Decimal('0'), income_rub)
    prev = Decimal('0')
    total_tax = Decimal('0')
    breakdown = []

    for bound, rate in TAX_BRACKETS:
        if bound is None:
            taxable = income - prev
            if taxable <= 0:
                taxable = Decimal('0')
            tax = quant(taxable * rate)
            breakdown.append((prev, None, rate, quant(taxable), tax))
            total_tax += tax
            break
        else:
            upper = Decimal(bound)
            # taxable part inside this bracket:
            taxable = min(income, upper) - prev
            if taxable <= 0:
                taxable = Decimal('0')
            tax = quant(taxable * rate)
            breakdown.append((prev, upper, rate, quant(taxable), tax))
            total_tax += tax
            prev = upper

        if income <= prev:
            break

    return quant(total_tax), breakdown


def calculate_gross_from_netto(netto_income: Decimal, precision: Decimal = Decimal('0.01')):
    """
    Рассчитать gross доход из netto дохода.
    Использует бинарный поиск для решения уравнения: gross - НДФЛ(gross) = netto
    Возвращает (gross_income, tax_amount, breakdown)
    """
    if netto_income <= 0:
        return Decimal('0'), Decimal('0'), []
    
    # Начальные границы для бинарного поиска
    # Минимальная gross = netto (если нет налогов)
    # Максимальная gross = netto * 1.5 (грубая оценка для верхней границы)
    low = netto_income
    high = netto_income * Decimal('1.5')
    
    # Увеличиваем верхнюю границу, пока не найдем решение
    while True:
        test_gross = high
        test_tax, _ = calculate_tax_by_annual(test_gross)
        test_netto = test_gross - test_tax
        if test_netto >= netto_income:
            break
        high *= Decimal('2')
    
    # Бинарный поиск
    max_iterations = 100
    for _ in range(max_iterations):
        mid = (low + high) / Decimal('2')
        tax, breakdown = calculate_tax_by_annual(mid)
        netto_result = mid - tax
        
        if abs(netto_result - netto_income) <= precision:
            return quant(mid), tax, breakdown
        
        if netto_result < netto_income:
            low = mid
        else:
            high = mid
    
    # Если не нашли точное решение, возвращаем ближайшее
    final_gross = (low + high) / Decimal('2')
    final_tax, final_breakdown = calculate_tax_by_annual(final_gross)
    return quant(final_gross), final_tax, final_breakdown


def months_when_thresholds_reached(monthly_list):
    """
    Принимает список из 12 Decimal (доходы по месяцам).
    Возвращает список кумулятивных сумм и словарь порогов -> (month_index, cumulative_sum)
    month_index — 1..12 или None если порог не достигнут за год.
    """
    cum = []
    s = Decimal('0')
    for m in monthly_list:
        s += m
        cum.append(quant(s))

    results = {}
    thresholds = [Decimal(b) for b, _ in TAX_BRACKETS if b is not None]
    for t in thresholds:
        reached_month = None
        reached_sum = None
        for idx, csum in enumerate(cum, start=1):
            if csum >= t:
                reached_month = idx
                reached_sum = csum
                break
        results[int(t)] = (reached_month, reached_sum)
    return cum, results
