# Инструменты сборки

Эта папка содержит все необходимое для создания исполняемого файла приложения под разные платформы.

## 🚀 Быстрый старт

### Windows

**Из корня проекта:**

```bash
build.bat
```

**Из этой папки:**

```bash
cd build_tools
build.bat
```

**Результат:** `dist/NDFL_Calculator.exe` (~50-80 МБ)

### macOS / Linux

**Из корня проекта:**

```bash
./build.sh
```

**Из этой папки:**

```bash
cd build_tools
./build.sh
```

**Результат:** `dist/NDFL_Calculator` (~50-80 МБ)

---

## 📁 Файлы

| Файл                    | Назначение                          |
| ----------------------- | ----------------------------------- |
| `build.bat`             | Скрипт сборки для Windows           |
| `build.sh`              | Скрипт сборки для macOS/Linux       |
| `clean.bat`             | Очистка артефактов (Windows)        |
| `clean.sh`              | Очистка артефактов (macOS/Linux)    |
| `calculator.spec`       | Конфигурация PyInstaller            |
| `README.md`             | Этот файл - быстрый старт           |
| `BUILD_INSTRUCTIONS.md` | Полная инструкция по сборке         |

---

## 📖 Полная документация

**[BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)** включает:

- 🔧 Автоматическая и ручная сборка
- ⚙️ Параметры PyInstaller
- 📦 Распространение приложения
- 🔍 Устранение проблем
- 🔄 Альтернативные инструменты
- ✅ Тестирование EXE

---

## ⚡ Основные команды

### Собрать приложение

**Windows:**

```bash
build.bat
```

**macOS/Linux:**

```bash
./build.sh
```

### Очистить артефакты

**Windows:**

```bash
clean.bat
```

**macOS/Linux:**

```bash
./clean.sh
```

### Настроить параметры

Отредактируйте `calculator.spec`

---

## 🔧 Требования

- Python 3.8+
- PyInstaller 6.0+
- Все зависимости из `requirements.txt`

Установка:

```bash
pip install -r requirements.txt
```

---

## 📦 Что получится

- ✅ Один исполняемый файл для вашей платформы
- ✅ Не требует установки Python
- ✅ Включает все зависимости
- ✅ Размер: 50-80 МБ
- ✅ Поддерживаемые платформы:
  - Windows (x64)
  - macOS (Intel/Apple Silicon)
  - Linux (x64)

---

## ❓ Проблемы?

См. раздел "Устранение проблем" в [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)
