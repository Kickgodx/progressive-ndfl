"""
Обработчик логики расчетов
"""

from decimal import Decimal
from ...calculators import (
    calculate_tax_by_annual,
    calculate_gross_from_netto,
    months_when_thresholds_reached,
    quant,
)
from ...utils import InputValidator


class CalculationHandler:
    """Обработчик расчетов налогов"""

    @staticmethod
    def validate_inputs(annual_input, monthly_input):
        """
        Валидация входных данных

        Args:
            annual_input: Годовой доход (строка)
            monthly_input: Месячные доходы (строка)

        Returns:
            tuple: (is_valid, error_msg, validated_data)
        """
        return InputValidator.validate_calculation_inputs(annual_input, monthly_input)

    @staticmethod
    def perform_calculation(validated_data, calc_type):
        """
        Выполнить расчет

        Args:
            validated_data: Валидированные данные
            calc_type: Тип расчета ('gross' или 'netto')

        Returns:
            dict: Результаты расчета
        """
        # Получаем валидированные данные
        if "annual" in validated_data:
            annual = quant(validated_data["annual"])
            monthly = None
        else:
            monthly = [quant(x) for x in validated_data["monthly"]]
            annual = sum(monthly)

        # Определяем тип расчета и выполняем соответствующие вычисления
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

        # Эффективная ставка
        eff_rate = (
            (total_tax / gross_income * 100) if gross_income > 0 else Decimal("0")
        )

        return {
            "calc_type": calc_type,
            "gross_income": gross_income,
            "netto_income": netto_income,
            "total_tax": total_tax,
            "eff_rate": eff_rate,
            "breakdown": breakdown,
            "monthly_data": monthly,
            "monthly_gross": float(gross_income / 12),
            "monthly_netto": float(netto_income / 12),
        }

    @staticmethod
    def format_results(calc_data):
        """
        Форматировать результаты расчета в текст

        Args:
            calc_data: Данные расчета

        Returns:
            str: Отформатированный текст результатов
        """
        calc_type = calc_data["calc_type"]
        gross_income = calc_data["gross_income"]
        netto_income = calc_data["netto_income"]
        total_tax = calc_data["total_tax"]
        eff_rate = calc_data["eff_rate"]
        breakdown = calc_data["breakdown"]
        monthly = calc_data["monthly_data"]

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
            out_lines.extend(
                CalculationHandler._format_monthly_data(monthly, calc_type)
            )

        out_lines.append(
            "\nПримечание: повышенные ставки применяются только к сумме превышения соответствующих порогов (маргинальная схема)."
        )

        return "\n".join(out_lines)

    @staticmethod
    def _format_monthly_data(monthly, calc_type):
        """Форматировать месячные данные"""
        out_lines = []
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
                if i == 1:
                    month_tax, _ = calculate_tax_by_annual(val)
                else:
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
                if i == 1:
                    month_tax, _ = calculate_tax_by_annual(val)
                else:
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

        return out_lines
