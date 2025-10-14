"""
Утилиты для создания всплывающих подсказок (tooltips)
"""

import tkinter as tk


class ToolTip:
    """
    Класс для создания всплывающих подсказок при наведении на виджеты
    """

    def __init__(self, widget, text, delay=500):
        """
        Инициализация tooltip

        Args:
            widget: виджет tkinter
            text: текст подсказки
            delay: задержка перед показом в мс
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tip_window = None
        self.id_after = None

        # Привязываем события
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Button-1>", self.on_leave)

    def on_enter(self, event=None):
        """Обработчик входа курсора на виджет"""
        self.schedule_show()

    def on_leave(self, event=None):
        """Обработчик выхода курсора с виджета"""
        self.cancel_show()
        self.hide()

    def schedule_show(self):
        """Запланировать показ подсказки"""
        self.cancel_show()
        self.id_after = self.widget.after(self.delay, self.show)

    def cancel_show(self):
        """Отменить запланированный показ"""
        if self.id_after:
            self.widget.after_cancel(self.id_after)
            self.id_after = None

    def show(self):
        """Показать подсказку"""
        if self.tip_window or not self.text:
            return

        # Получаем координаты виджета
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        # Создаем окно подсказки
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Убираем рамку окна
        tw.wm_geometry(f"+{x}+{y}")

        # Создаем метку с текстом
        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#FFFFE0",
            foreground="#000000",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Arial", 9),
            padx=8,
            pady=6,
        )
        label.pack()

    def hide(self):
        """Скрыть подсказку"""
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


def create_tooltip(widget, text, delay=500):
    """
    Создать tooltip для виджета

    Args:
        widget: виджет tkinter
        text: текст подсказки
        delay: задержка перед показом в мс

    Returns:
        ToolTip: объект tooltip
    """
    return ToolTip(widget, text, delay)
