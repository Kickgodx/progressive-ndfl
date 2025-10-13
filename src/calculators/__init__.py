"""
Модули для расчетов
"""

from .tax_calculator import (
    calculate_tax_by_annual,
    calculate_gross_from_netto,
    months_when_thresholds_reached,
    quant,
    TAX_BRACKETS,
)

__all__ = [
    "calculate_tax_by_annual",
    "calculate_gross_from_netto",
    "months_when_thresholds_reached",
    "quant",
    "TAX_BRACKETS",
]
