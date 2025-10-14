"""
Менеджер истории расчетов
"""

import json
from datetime import datetime
from pathlib import Path


class HistoryManager:
    """Менеджер для сохранения и загрузки истории расчетов"""

    def __init__(self, history_file: str = "history/calculation_history.json"):
        self.history_file = Path(history_file)
        # Создаем папку history если её нет
        self.history_file.parent.mkdir(exist_ok=True)
        self.history = self._load_history()

    def _load_history(self):
        """Загрузить историю из файла"""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError, OSError):
                return []
        return []

    def _save_history(self):
        """Сохранить историю в файл"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            return True
        except (OSError, IOError, json.JSONEncodeError):
            return False

    def add_calculation(self, calc_data: dict):
        """Добавить расчет в историю"""
        # Конвертируем monthly_data из Decimal в float для JSON сериализации
        monthly_data = calc_data.get("monthly_data", [])
        if monthly_data:
            monthly_data = [float(x) for x in monthly_data]

        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "calc_type": calc_data.get("calc_type", ""),
            "gross_income": float(calc_data.get("gross_income", 0)),
            "netto_income": float(calc_data.get("netto_income", 0)),
            "total_tax": float(calc_data.get("total_tax", 0)),
            "effective_rate": float(calc_data.get("eff_rate", 0)),
            "monthly_data": monthly_data,
            "monthly_gross": calc_data.get("monthly_gross", 0),
            "monthly_netto": calc_data.get("monthly_netto", 0),
        }

        self.history.append(history_entry)

        # Ограничиваем историю последними 50 расчетами
        if len(self.history) > 50:
            self.history = self.history[-50:]

        self._save_history()

    def get_history(self, limit: int = None):
        """Получить историю расчетов"""
        if limit:
            return self.history[-limit:]
        return self.history

    def clear_history(self):
        """Очистить историю"""
        self.history = []
        self._save_history()

    def delete_calculation(self, index: int):
        """Удалить расчет из истории по индексу"""
        if 0 <= index < len(self.history):
            self.history.pop(index)
            self._save_history()
            return True
        return False

    def get_last_calculation(self):
        """Получить последний расчет"""
        if self.history:
            return self.history[-1]
        return None
