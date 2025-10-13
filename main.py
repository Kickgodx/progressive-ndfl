#!/usr/bin/env python3
"""
Главный файл приложения - Калькулятор прогрессивного НДФЛ РФ
"""

from src.gui import TaxApp


def main():
    """Запуск приложения"""
    app = TaxApp()
    app.mainloop()


if __name__ == '__main__':
    main()
