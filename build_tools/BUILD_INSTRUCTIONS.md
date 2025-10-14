# Полная инструкция по сборке

## 📋 Содержание

1. [Быстрая сборка](#быстрая-сборка)
2. [Ручная сборка](#ручная-сборка)
3. [Параметры PyInstaller](#параметры-pyinstaller)
4. [Распространение](#распространение)
5. [Устранение проблем](#устранение-проблем)
6. [Альтернативные инструменты](#альтернативные-инструменты)
7. [Тестирование](#тестирование)
8. [Кросс-платформенная сборка](#кросс-платформенная-сборка)

---

## Быстрая сборка

### Автоматическая сборка (рекомендуется)

**Windows:**

Из корня проекта:

```bash
build.bat
```

**macOS / Linux:**

Из корня проекта:

```bash
./build.sh
```

Скрипт автоматически:

- Установит зависимости
- Создаст виртуальное окружение (для Unix)
- Соберет исполняемый файл с оптимальными настройками
- Покажет результат

**Готовые файлы:**

- Windows: `dist/NDFL_Calculator.exe`
- macOS/Linux: `dist/NDFL_Calculator`

**Время сборки:** 2-5 минут

---

## Ручная сборка

### Шаг 1: Установка зависимостей

```bash
pip install -r requirements.txt
```

### Шаг 2: Сборка EXE

**Вариант А - Простая сборка:**

```bash
pyinstaller --onefile --windowed --name "NDFL_Calculator" main.py
```

**Вариант Б - С настройками (рекомендуется):**

```bash
cd build_tools
pyinstaller calculator.spec
```

### Шаг 3: Результат

EXE файл: `dist/NDFL_Calculator.exe`

---

## Параметры PyInstaller

### Основные параметры

| Параметр          | Описание                          |
| ----------------- | --------------------------------- |
| `--onefile`       | Создать один EXE файл             |
| `--windowed`      | Скрыть консольное окно            |
| `--noconsole`     | То же что `--windowed`            |
| `--name`          | Имя выходного файла               |
| `--add-data`      | Добавить файлы/папки в сборку     |
| `--hidden-import` | Явно указать импортируемые модули |
| `--collect-all`   | Собрать все файлы библиотеки      |
| `--icon`          | Добавить иконку (формат .ico)     |

### Пример с иконкой

```bash
pyinstaller --onefile --windowed --icon=icon.ico --name "NDFL_Calculator" main.py
```

### Настройка через spec файл

Отредактируйте `build_tools/calculator.spec` для тонкой настройки:

- Список скрытых импортов
- Исключаемые модули
- Дополнительные файлы
- Параметры компрессии

---

## Распространение

### Что включено в EXE

- ✅ Python интерпретатор
- ✅ Tkinter (GUI)
- ✅ Matplotlib (графики)
- ✅ OpenPyXL (Excel)
- ✅ Весь код приложения
- ✅ Все зависимости

### Размер файла

**Ожидаемый размер:** 50-80 МБ

Это нормально, т.к. включает полный Python и все библиотеки.

### Использование

1. **Скопируйте** `dist/NDFL_Calculator.exe` на любой ПК с Windows
2. **Запустите** двойным кликом
3. **Не требуется** установка Python или зависимостей

### Важно

- Папка `history/` создается автоматически при первом запуске
- История сохраняется рядом с EXE файлом
- Антивирус может выдать предупреждение (ложное срабатывание)

---

## Устранение проблем

### Проблема: Антивирус блокирует EXE

**Причина:** Ложное срабатывание (упакованные Python приложения часто помечаются)

**Решение:**

1. Добавьте файл в исключения антивируса
2. Или используйте цифровую подпись (для коммерческого распространения)

### Проблема: Ошибка при сборке

**Решение:**

```bash
# Переустановите зависимости
pip install -r requirements.txt --upgrade

# Очистите кэш
clean.bat

# Попробуйте снова
build.bat
```

### Проблема: Ошибка при запуске EXE

**Возможные причины:**

1. Отсутствуют системные библиотеки (редко на Windows)
2. Антивирус блокирует
3. Недостаточно прав (запустите от администратора)

**Решение:**

- Проверьте логи в папке `build/`
- Запустите EXE из командной строки для просмотра ошибок
- Пересоберите с флагом `--debug`

### Проблема: Большой размер файла

**Решение - исключите ненужные модули:**

```bash
pyinstaller --onefile --windowed ^
    --exclude-module pytest ^
    --exclude-module setuptools ^
    --exclude-module pip ^
    --name "NDFL_Calculator" main.py
```

**Дополнительно - используйте UPX компрессию:**

1. Скачайте UPX: <https://upx.github.io/>
2. Добавьте в PATH
3. PyInstaller автоматически использует UPX если он доступен

### Проблема: Долгий запуск EXE

**Причина:** При первом запуске EXE распаковывается во временную папку

**Решение:**

- Это нормально для `--onefile` режима
- Для более быстрого запуска используйте `--onedir` вместо `--onefile`
- Или используйте SSD диск

---

## Альтернативные инструменты

Если PyInstaller не подходит:

### 1. cx_Freeze

```bash
pip install cx_Freeze
cxfreeze main.py --target-dir dist
```

**Плюсы:** Стабильный, хорошо документирован
**Минусы:** Более сложная настройка

### 2. py2exe (только Windows)

```bash
pip install py2exe
python setup.py py2exe
```

**Плюсы:** Оптимизирован для Windows
**Минусы:** Требует setup.py, только Windows

### 3. Nuitka

```bash
pip install nuitka
python -m nuitka --onefile --windows-disable-console main.py
```

**Плюсы:** Компилирует в C++, быстрее работает
**Минусы:** Долгая компиляция, сложнее настройка

---

## Тестирование

### Базовое тестирование

После создания EXE:

1. **Запустите** на компьютере где собирали
2. **Проверьте все функции:**
   - ✅ Расчет gross/netto
   - ✅ Месячные данные
   - ✅ Графики
   - ✅ Экспорт (TXT, CSV, JSON, Excel)
   - ✅ История расчетов
   - ✅ Горячие клавиши

### Расширенное тестирование

1. **Скопируйте** EXE в отдельную папку
2. **Запустите** на другом ПК без Python
3. **Проверьте** на разных версиях Windows:
   - Windows 10
   - Windows 11
   - Windows Server (если нужно)

### Чек-лист перед распространением

- [ ] EXE запускается без ошибок
- [ ] Все функции работают корректно
- [ ] Создается папка `history/`
- [ ] История сохраняется и загружается
- [ ] Экспорт во все форматы работает
- [ ] Графики отображаются правильно
- [ ] Нет критических предупреждений антивируса
- [ ] Размер файла приемлемый
- [ ] Протестировано на чистой системе

---

## Дополнительная информация

### Полезные ссылки

- **PyInstaller:** <https://pyinstaller.org/>
- **UPX компрессия:** <https://upx.github.io/>
- **Документация Python:** <https://docs.python.org/>

### Структура сборки

```text
progressive_ndfl/
├── build/              # Временные файлы сборки
├── dist/               # Готовый EXE файл
│   └── NDFL_Calculator.exe
└── build_tools/
    └── calculator.spec # Конфигурация
```

### Очистка

Для очистки артефактов сборки:

```bash
clean.bat
```

Удаляет:

- `build/` - временные файлы
- `dist/` - готовые файлы
- `__pycache__/` - кэш Python
- `*.pyc`, `*.pyo` - скомпилированные файлы

---

## Обновление приложения

При обновлении кода:

1. Внесите изменения в исходный код
2. Протестируйте через `python main.py`
3. Очистите старую сборку: `clean.bat`
4. Соберите новый EXE: `build.bat`
5. Протестируйте новый EXE
6. Распространите обновление

**Рекомендация:** Используйте версионирование в имени файла:

```bash
pyinstaller --name "NDFL_Calculator_v1.0" main.py
```

---

## Кросс-платформенная сборка

### Общая информация

PyInstaller создает исполняемые файлы **только для текущей платформы**. Это означает:

- **Windows → Windows EXE** (.exe)
- **macOS → macOS приложение** (без расширения)
- **Linux → Linux бинарник** (без расширения)

**Важно:** Нельзя собрать Windows EXE на macOS или наоборот!

### Сборка для разных платформ

#### Windows

```bash
# На Windows машине
build.bat
# Результат: dist/NDFL_Calculator.exe
```

#### macOS

```bash
# На macOS машине
chmod +x build.sh  # Первый раз
./build.sh
# Результат: dist/NDFL_Calculator
```

**Особенности macOS:**

- Автоматически создается виртуальное окружение
- Поддержка Intel и Apple Silicon (M1/M2/M3)
- Файл автоматически помечается как исполняемый

#### Linux

```bash
# На Linux машине
chmod +x build.sh  # Первый раз
./build.sh
# Результат: dist/NDFL_Calculator
```

**Особенности Linux:**

- Требуется `python3-tk` (обычно уже установлен)
- Файл автоматически помечается как исполняемый
- Работает на большинстве дистрибутивов (Ubuntu, Fedora, Debian, etc.)

### Стратегии распространения

#### Вариант 1: Сборка на каждой платформе

**Рекомендуется** для официального релиза.

1. Соберите на Windows машине → `NDFL_Calculator.exe`
2. Соберите на macOS машине → `NDFL_Calculator_macOS`
3. Соберите на Linux машине → `NDFL_Calculator_Linux`
4. Распространите все три файла

#### Вариант 2: GitHub Actions / CI/CD

Автоматическая сборка для всех платформ через GitHub Actions.

Пример `.github/workflows/build.yml`:

```yaml
name: Build

on: [push, pull_request]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: .\build_tools\build.bat
      - uses: actions/upload-artifact@v3
        with:
          name: Windows
          path: dist/NDFL_Calculator.exe

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: chmod +x build_tools/build.sh
      - run: ./build_tools/build.sh
      - uses: actions/upload-artifact@v3
        with:
          name: macOS
          path: dist/NDFL_Calculator

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: sudo apt-get install -y python3-tk
      - run: chmod +x build_tools/build.sh
      - run: ./build_tools/build.sh
      - uses: actions/upload-artifact@v3
        with:
          name: Linux
          path: dist/NDFL_Calculator
```

#### Вариант 3: Только исходный код

Для open-source проектов - пользователи сами собирают для своей платформы.

### Требования по платформам

#### Требования для Windows

- Windows 10 или новее (64-bit)
- Не требует установленного Python

#### Требования для macOS

- macOS 10.15 (Catalina) или новее
- Intel или Apple Silicon (M1/M2/M3)
- Не требует установленного Python

#### Требования для Linux

- Большинство современных дистрибутивов
- x86_64 архитектура
- Не требует установленного Python

### Размеры исполняемых файлов

Примерные размеры после сборки:

- **Windows:** 50-80 МБ (.exe)
- **macOS:** 55-85 МБ
- **Linux:** 50-75 МБ

Размер зависит от:

- Версии Python
- Количества зависимостей
- Использования UPX компрессии

### Тестирование кросс-платформенных сборок

**Минимальный набор тестов:**

1. ✅ Приложение запускается
2. ✅ GUI отображается корректно
3. ✅ Расчеты работают
4. ✅ Экспорт файлов работает
5. ✅ История сохраняется

**Тестовые платформы:**

- Windows 10/11
- macOS 12+ (Monterey и новее)
- Ubuntu 20.04/22.04 LTS

### Устранение проблем по платформам

#### macOS: "App can't be opened"

```bash
# Разблокировка приложения
xattr -cr dist/NDFL_Calculator
```

#### Linux: "Permission denied"

```bash
# Сделать исполняемым
chmod +x dist/NDFL_Calculator
```

#### Все платформы: tkinter не найден

Убедитесь, что tkinter установлен:

```bash
# Windows - обычно включен
# macOS - обычно включен
# Linux - установить пакет
sudo apt-get install python3-tk  # Ubuntu/Debian
sudo dnf install python3-tkinter  # Fedora
```

### Полезные команды

```bash
# Проверка платформы
python -c "import platform; print(platform.system())"

# Проверка tkinter
python -c "import tkinter; print('OK')"

# Проверка размера файла
# Windows
dir dist\NDFL_Calculator.exe
# macOS/Linux
ls -lh dist/NDFL_Calculator

# Запуск собранного приложения
# Windows
dist\NDFL_Calculator.exe
# macOS/Linux
./dist/NDFL_Calculator
```

---

**Дата обновления документации:** 2025-10-15
