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

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
    )
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


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
                    [
                        "Средний месячный доход до налогов",
                        float(calculation_data.get("monthly_gross", 0)),
                    ]
                )
                writer.writerow(
                    [
                        "Средний месячный доход после налогов",
                        float(calculation_data.get("monthly_netto", 0)),
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
                "monthly_gross": float(calculation_data.get("monthly_gross", 0)),
                "monthly_netto": float(calculation_data.get("monthly_netto", 0)),
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
            ws[f"A{row}"] = "Средний месячный доход до налогов (руб.)"
            ws[f"B{row}"] = float(calculation_data.get("monthly_gross", 0))
            ws[f"B{row}"].number_format = "#,##0.00"

            row += 1
            ws[f"A{row}"] = "Средний месячный доход после налогов (руб.)"
            ws[f"B{row}"] = float(calculation_data.get("monthly_netto", 0))
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


def export_to_pdf(calculation_data: dict, parent_window=None):
    """Экспорт данных расчета в PDF"""
    if not PDF_AVAILABLE:
        messagebox.showerror(
            "Ошибка",
            "Для экспорта в PDF необходимо установить библиотеку reportlab:\n"
            "pip install reportlab",
        )
        return False

    try:
        filename = filedialog.asksaveasfilename(
            parent=parent_window,
            defaultextension=".pdf",
            filetypes=[("PDF файлы", "*.pdf"), ("Все файлы", "*.*")],
            title="Сохранить данные в PDF",
        )

        if filename:
            # Используем встроенные шрифты reportlab (работают везде)
            font_name = "Helvetica"
            font_name_bold = "Helvetica-Bold"

            # Создаем PDF документ
            doc = SimpleDocTemplate(filename, pagesize=A4)
            elements = []

            # Создаем стили
            styles = getSampleStyleSheet()

            # Заголовок
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontName=font_name_bold,
                fontSize=16,
                alignment=TA_CENTER,
                spaceAfter=12,
            )

            # Обычный текст
            normal_style = ParagraphStyle(
                "CustomNormal",
                parent=styles["Normal"],
                fontName=font_name,
                fontSize=10,
                spaceAfter=6,
            )

            # Добавляем заголовок
            elements.append(
                Paragraph(
                    "Progressive NDFL Calculator (Russian Federation)", title_style
                )
            )
            elements.append(
                Paragraph(
                    f"Calculation date: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
                    normal_style,
                )
            )
            elements.append(Spacer(1, 0.5 * cm))

            # Основные данные
            calc_type_text = (
                "Gross to Net"
                if calculation_data.get("calc_type") == "gross"
                else "Net to Gross"
            )

            data = [
                ["Parameter", "Value"],
                ["Calculation Type", calc_type_text],
                [
                    "Annual Gross Income",
                    f"{float(calculation_data.get('gross_income', 0)):,.2f} RUB".replace(
                        ",", " "
                    ),
                ],
                [
                    "Annual Net Income",
                    f"{float(calculation_data.get('netto_income', 0)):,.2f} RUB".replace(
                        ",", " "
                    ),
                ],
                [
                    "Avg Monthly Gross Income",
                    f"{float(calculation_data.get('monthly_gross', 0)):,.2f} RUB".replace(
                        ",", " "
                    ),
                ],
                [
                    "Avg Monthly Net Income",
                    f"{float(calculation_data.get('monthly_netto', 0)):,.2f} RUB".replace(
                        ",", " "
                    ),
                ],
                [
                    "Total Tax",
                    f"{float(calculation_data.get('total_tax', 0)):,.2f} RUB".replace(
                        ",", " "
                    ),
                ],
                [
                    "Effective Tax Rate",
                    f"{float(calculation_data.get('eff_rate', 0)):.2f}%",
                ],
            ]

            # Создаем таблицу
            table = Table(data, colWidths=[10 * cm, 7 * cm])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), font_name_bold),
                        ("FONTSIZE", (0, 0), (-1, 0), 11),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("FONTNAME", (0, 1), (-1, -1), font_name),
                        ("FONTSIZE", (0, 1), (-1, -1), 10),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            elements.append(table)
            elements.append(Spacer(1, 0.7 * cm))

            # Разбивка по ступеням
            elements.append(Paragraph("<b>Tax Brackets Breakdown</b>", normal_style))
            elements.append(Spacer(1, 0.3 * cm))

            breakdown_data = [
                [
                    "Lower Bound",
                    "Upper Bound",
                    "Rate %",
                    "Taxable\nAmount",
                    "Tax",
                ]
            ]

            for bracket in calculation_data.get("breakdown", []):
                lower, upper, rate, taxable, tax = bracket
                breakdown_data.append(
                    [
                        f"{float(lower) if lower else 0:,.0f}".replace(",", " "),
                        f"{float(upper):,.0f}".replace(",", " ") if upper else "∞",
                        f"{float(rate * 100):.0f}",
                        f"{float(taxable):,.2f}".replace(",", " "),
                        f"{float(tax):,.2f}".replace(",", " "),
                    ]
                )

            breakdown_table = Table(
                breakdown_data, colWidths=[3 * cm, 3 * cm, 2 * cm, 4 * cm, 4 * cm]
            )
            breakdown_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), font_name_bold),
                        ("FONTSIZE", (0, 0), (-1, 0), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("FONTNAME", (0, 1), (-1, -1), font_name),
                        ("FONTSIZE", (0, 1), (-1, -1), 9),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            elements.append(breakdown_table)

            # Примечание
            elements.append(Spacer(1, 0.5 * cm))
            note_style = ParagraphStyle(
                "Note",
                parent=styles["Normal"],
                fontName=font_name,
                fontSize=8,
                textColor=colors.grey,
            )
            elements.append(
                Paragraph(
                    "Note: Progressive tax rates apply only to the amount exceeding each threshold (marginal system). "
                    "Tax brackets (2025): 13% up to 2.4M; 15% 2.4-5M; 18% 5-20M; 20% 20-50M; 22% over 50M RUB.",
                    note_style,
                )
            )

            # Генерируем PDF
            doc.build(elements)

            messagebox.showinfo("Успех", f"Данные сохранены в PDF файл:\n{filename}")
            return True

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить PDF файл:\n{e}")
        return False
