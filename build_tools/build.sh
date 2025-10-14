#!/bin/bash

# Change to project root directory
cd "$(dirname "$0")/.." || exit 1

echo "========================================"
echo "Building NDFL Calculator for $(uname -s)"
echo "========================================"
echo ""

# Определяем платформу
PLATFORM=$(uname -s)
case "$PLATFORM" in
    Darwin*)
        PLATFORM_NAME="macOS"
        OUTPUT_NAME="NDFL_Calculator"
        ;;
    Linux*)
        PLATFORM_NAME="Linux"
        OUTPUT_NAME="NDFL_Calculator"
        ;;
    *)
        echo "Unsupported platform: $PLATFORM"
        exit 1
        ;;
esac

echo "Target platform: $PLATFORM_NAME"
echo ""

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Проверяем/создаем виртуальное окружение
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo ""
fi

# Активируем виртуальное окружение
echo "Activating virtual environment..."
source .venv/bin/activate
echo ""

# Устанавливаем зависимости
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
echo ""

# Создаем исполняемый файл
echo "Creating executable file..."
echo "This may take a few minutes..."
echo ""

pyinstaller \
    --onefile \
    --windowed \
    --name "$OUTPUT_NAME" \
    --add-data "src:src" \
    --hidden-import "tkinter" \
    --hidden-import "matplotlib" \
    --hidden-import "openpyxl" \
    --hidden-import "decimal" \
    --hidden-import "json" \
    --hidden-import "csv" \
    --collect-all "matplotlib" \
    --collect-all "openpyxl" \
    --noconsole \
    main.py

echo ""

# Проверяем результат
if [ -f "dist/$OUTPUT_NAME" ]; then
    echo "========================================"
    echo "Success! Executable created:"
    echo "  dist/$OUTPUT_NAME"
    echo "========================================"
    echo ""
    
    # Делаем файл исполняемым
    chmod +x "dist/$OUTPUT_NAME"
    echo "File marked as executable"
    echo ""
    
    # Показываем размер файла
    echo "File size:"
    ls -lh "dist/$OUTPUT_NAME" | awk '{print $5, $9}'
    echo ""
    
    # Создаем папку history если её нет
    mkdir -p "dist/history"
    echo "Created dist/history/ directory"
    echo ""
    
    echo "To run the application:"
    echo "  ./dist/$OUTPUT_NAME"
    echo ""
else
    echo "========================================"
    echo "Error: Failed to create executable"
    echo "========================================"
    exit 1
fi

# Деактивируем виртуальное окружение
deactivate

echo "Build complete!"
echo ""

