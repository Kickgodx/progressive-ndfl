"""
Утилиты для валидации ввода
"""

import re
from decimal import Decimal, InvalidOperation


class InputValidator:
    """Класс для валидации пользовательского ввода"""

    @staticmethod
    def validate_income_input(
        value: str, field_name: str = "доход"
    ) -> tuple[bool, str, Decimal]:
        """
        Валидация ввода суммы дохода
        Возвращает (is_valid, error_message, decimal_value)
        """
        if not value or not value.strip():
            return False, f"Поле {field_name} не может быть пустым", Decimal("0")

        # Очищаем от пробелов и подчеркиваний
        cleaned_value = value.strip().replace("_", "").replace(" ", "")

        # Проверяем на наличие только цифр, точек и запятых
        if not re.match(r"^[\d.,]+$", cleaned_value):
            return (
                False,
                f"В поле {field_name} можно вводить только цифры, точки и запятые",
                Decimal("0"),
            )

        # Заменяем запятые на точки для корректного парсинга
        cleaned_value = cleaned_value.replace(",", ".")

        try:
            decimal_value = Decimal(cleaned_value)

            # Проверяем на отрицательные значения
            if decimal_value < 0:
                return (
                    False,
                    f"Значение {field_name} не может быть отрицательным",
                    Decimal("0"),
                )

            # Проверяем на слишком большие значения (больше 1 триллиона)
            if decimal_value > Decimal("1000000000000"):
                return (
                    False,
                    f"Значение {field_name} слишком большое (максимум 1 триллион)",
                    Decimal("0"),
                )

            return True, "", decimal_value

        except InvalidOperation:
            return False, f"Неверный формат числа в поле {field_name}", Decimal("0")

    @staticmethod
    def validate_monthly_input(value: str) -> tuple[bool, str, list]:
        """
        Валидация ввода месячных доходов
        Возвращает (is_valid, error_message, monthly_list)
        """
        if not value or not value.strip():
            return False, "Поле месячных доходов не может быть пустым", []

        try:
            # Разделяем по запятым
            parts = [p.strip() for p in value.split(",") if p.strip() != ""]

            if len(parts) not in (1, 12):
                return (
                    False,
                    "Введите либо 12 чисел по месяцам, либо одно число (будет интерпретировано как одинаковый месячный доход)",
                    [],
                )

            monthly_list = []

            for i, part in enumerate(parts):
                # Валидируем каждую часть
                is_valid, error_msg, decimal_val = InputValidator.validate_income_input(
                    part, f"месячный доход {i + 1}"
                )

                if not is_valid:
                    return False, error_msg, []

                monthly_list.append(decimal_val)

            # Если введено одно число, повторяем его 12 раз
            if len(monthly_list) == 1:
                monthly_list = monthly_list * 12

            return True, "", monthly_list

        except Exception as e:
            return False, f"Ошибка при обработке месячных доходов: {str(e)}", []

    @staticmethod
    def format_currency(amount: Decimal) -> str:
        """Форматирование суммы валюты для отображения"""
        return f"{amount:,.2f}".replace(",", " ").replace(".", ",")

    @staticmethod
    def validate_calculation_inputs(
        annual_input: str, monthly_input: str
    ) -> tuple[bool, str, dict]:
        """
        Комплексная валидация всех полей ввода
        Возвращает (is_valid, error_message, validated_data)
        """
        annual_input = annual_input.strip()
        monthly_input = monthly_input.strip()

        # Проверяем, что введены данные
        if not annual_input and not monthly_input:
            return False, "Введите годовой доход или месячные доходы", {}

        validated_data = {}

        # Валидируем годовой доход, если введен
        if annual_input:
            is_valid, error_msg, annual_decimal = InputValidator.validate_income_input(
                annual_input, "годовой доход"
            )
            if not is_valid:
                return False, error_msg, {}
            validated_data["annual"] = annual_decimal

        # Валидируем месячные доходы, если введены
        if monthly_input:
            is_valid, error_msg, monthly_list = InputValidator.validate_monthly_input(
                monthly_input
            )
            if not is_valid:
                return False, error_msg, {}
            validated_data["monthly"] = monthly_list

        return True, "", validated_data
