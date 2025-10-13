"""
Утилиты для экспорта результатов
"""

import csv
import json
from datetime import datetime
from tkinter import filedialog, messagebox

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill

    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


def export_to_txt(results_text: str, parent_window=None):
    """Экспорт результатов в текстовый файл"""
    try:
        filename = filedialog.asksaveasfilename(
            parent=parent_window,
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
            title="Сохранить результаты",
        )

        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("Результаты расчета НДФЛ\n")
                f.write(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
                f.write("=" * 50 + "\n\n")
                f.write(results_text)

            messagebox.showinfo("Успех", f"Результаты сохранены в файл:\n{filename}")
            return True
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")
        return False


def export_to_csv(calculation_data: dict, parent_window=None):
    """Экспорт данных расчета в CSV"""
    try:
        filename = filedialog.asksaveasfilename(
            parent=parent_window,
            defaultextension=".csv",
            filetypes=[("CSV файлы", "*.csv"), ("Все файлы", "*.*")],
            title="Сохранить данные в CSV",
        )

        if filename:
            # Используем UTF-8 с BOM для корректного отображения кириллицы в Excel
            with open(filename, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")

                # Заголовки
                writer.writerow(["Параметр", "Значение"])
                writer.writerow(["Тип расчета", calculation_data.get("calc_type", "")])
                writer.writerow(
                    [
                        "Годовой доход до налогов",
                        calculation_data.get("gross_income", 0),
                    ]
                )
                writer.writerow(
                    [
                        "Годовой доход после налогов",
                        calculation_data.get("netto_income", 0),
                    ]
                )
                writer.writerow(
                    ["Общая сумма налога", calculation_data.get("total_tax", 0)]
                )
                writer.writerow(
                    ["Эффективная ставка", calculation_data.get("eff_rate", 0)]
                )

                # Разбивка по ступеням
                writer.writerow([])
                writer.writerow(["Разбивка по ступеням"])
                writer.writerow(
                    [
                        "Нижняя граница",
                        "Верхняя граница",
                        "Ставка %",
                        "Налогооблагаемая часть",
                        "Налог",
                    ]
                )

                for bracket in calculation_data.get("breakdown", []):
                    lower, upper, rate, taxable, tax = bracket
                    writer.writerow(
                        [
                            float(lower) if lower else 0,
                            float(upper) if upper else "∞",
                            float(rate * 100),
                            float(taxable),
                            float(tax),
                        ]
                    )

            messagebox.showinfo("Успех", f"Данные сохранены в CSV файл:\n{filename}")
            return True
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить CSV файл:\n{e}")
        return False


def export_to_json(calculation_data: dict, parent_window=None):
    """Экспорт данных расчета в JSON"""
    try:
        filename = filedialog.asksaveasfilename(
            parent=parent_window,
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")],
            title="Сохранить данные в JSON",
        )

        if filename:
            # Конвертируем Decimal в float для JSON
            json_data = {
                "timestamp": datetime.now().isoformat(),
                "calculation_type": calculation_data.get("calc_type", ""),
                "gross_income": float(calculation_data.get("gross_income", 0)),
                "netto_income": float(calculation_data.get("netto_income", 0)),
                "total_tax": float(calculation_data.get("total_tax", 0)),
                "effective_rate": float(calculation_data.get("eff_rate", 0)),
                "breakdown": [
                    {
                        "lower_bound": float(bracket[0]) if bracket[0] else 0,
                        "upper_bound": float(bracket[1]) if bracket[1] else None,
                        "rate_percent": float(bracket[2] * 100),
                        "taxable_amount": float(bracket[3]),
                        "tax_amount": float(bracket[4]),
                    }
                    for bracket in calculation_data.get("breakdown", [])
                ],
            }

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("Успех", f"Данные сохранены в JSON файл:\n{filename}")
            return True
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить JSON файл:\n{e}")
        return False


def export_to_excel(calculation_data: dict, parent_window=None):
    """Экспорт данных расчета в Excel"""
    if not EXCEL_AVAILABLE:
        messagebox.showerror(
            "Ошибка",
            "Для экспорта в Excel необходимо установить библиотеку openpyxl:\n"
            "pip install openpyxl",
        )
        return False

    try:
        filename = filedialog.asksaveasfilename(
            parent=parent_window,
            defaultextension=".xlsx",
            filetypes=[("Excel файлы", "*.xlsx"), ("Все файлы", "*.*")],
            title="Сохранить данные в Excel",
        )

        if filename:
            # Создаем новую книгу Excel
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Расчет НДФЛ"

            # Стили
            header_font = Font(bold=True, size=12)
            title_font = Font(bold=True, size=14)
            center_alignment = Alignment(horizontal="center", vertical="center")
            header_fill = PatternFill(
                start_color="E0E0E0", end_color="E0E0E0", fill_type="solid"
            )

            # Заголовок
            ws["A1"] = "Расчет прогрессивного НДФЛ РФ"
            ws["A1"].font = title_font
            ws.merge_cells("A1:D1")
            ws["A1"].alignment = center_alignment

            # Дата
            ws["A2"] = f"Дата расчета: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            ws.merge_cells("A2:D2")
            ws["A2"].alignment = center_alignment

            # Основные данные
            row = 4
            ws[f"A{row}"] = "Параметр"
            ws[f"B{row}"] = "Значение"
            ws[f"A{row}"].font = header_font
            ws[f"B{row}"].font = header_font
            ws[f"A{row}"].fill = header_fill
            ws[f"B{row}"].fill = header_fill

            row += 1
            ws[f"A{row}"] = "Тип расчета"
            ws[f"B{row}"] = calculation_data.get("calc_type", "")

            row += 1
            ws[f"A{row}"] = "Годовой доход до налогов (руб.)"
            ws[f"B{row}"] = float(calculation_data.get("gross_income", 0))
            ws[f"B{row}"].number_format = "#,##0.00"

            row += 1
            ws[f"A{row}"] = "Годовой доход после налогов (руб.)"
            ws[f"B{row}"] = float(calculation_data.get("netto_income", 0))
            ws[f"B{row}"].number_format = "#,##0.00"

            row += 1
            ws[f"A{row}"] = "Общая сумма налога (руб.)"
            ws[f"B{row}"] = float(calculation_data.get("total_tax", 0))
            ws[f"B{row}"].number_format = "#,##0.00"

            row += 1
            ws[f"A{row}"] = "Эффективная ставка (%)"
            ws[f"B{row}"] = float(calculation_data.get("eff_rate", 0))
            ws[f"B{row}"].number_format = "0.00"

            # Разбивка по ступеням
            row += 2
            ws[f"A{row}"] = "Разбивка по ступеням"
            ws[f"A{row}"].font = header_font
            ws.merge_cells(f"A{row}:E{row}")
            ws[f"A{row}"].alignment = center_alignment

            row += 1
            headers = [
                "Нижняя граница",
                "Верхняя граница",
                "Ставка %",
                "Налогооблагаемая часть",
                "Налог",
            ]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=row, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = center_alignment

            row += 1
            for bracket in calculation_data.get("breakdown", []):
                lower, upper, rate, taxable, tax = bracket
                # Нижняя граница
                cell = ws.cell(row=row, column=1, value=float(lower) if lower else 0)
                cell.number_format = "#,##0.00"
                # Верхняя граница
                if upper:
                    cell = ws.cell(row=row, column=2, value=float(upper))
                    cell.number_format = "#,##0.00"
                else:
                    ws.cell(row=row, column=2, value="∞")
                # Ставка %
                cell = ws.cell(row=row, column=3, value=float(rate * 100))
                cell.number_format = "0.00"
                # Налогооблагаемая часть
                cell = ws.cell(row=row, column=4, value=float(taxable))
                cell.number_format = "#,##0.00"
                # Налог
                cell = ws.cell(row=row, column=5, value=float(tax))
                cell.number_format = "#,##0.00"
                row += 1

            # Устанавливаем фиксированную оптимальную ширину колонок
            ws.column_dimensions[
                "A"
            ].width = 38  # Параметры - широкие для длинных названий
            ws.column_dimensions[
                "B"
            ].width = 22  # Значения - достаточно для больших чисел
            ws.column_dimensions["C"].width = 22  # Верхняя граница
            ws.column_dimensions["D"].width = 15  # Ставка %
            ws.column_dimensions["E"].width = 25  # Налогооблагаемая часть
            ws.column_dimensions["F"].width = 22  # Налог (на случай если используется)

            # Сохраняем файл
            wb.save(filename)

            messagebox.showinfo("Успех", f"Данные сохранены в Excel файл:\n{filename}")
            return True

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить Excel файл:\n{e}")
        return False
