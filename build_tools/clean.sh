#!/bin/bash

# Change to project root directory
cd "$(dirname "$0")/.." || exit 1

echo "Cleaning build artifacts..."
echo ""

# Удаляем директории сборки
if [ -d "build" ]; then
    rm -rf build
    echo "- Removed build/"
fi

if [ -d "dist" ]; then
    rm -rf dist
    echo "- Removed dist/"
fi

# Удаляем .spec файлы в корне (создаются PyInstaller)
if [ -f "NDFL_Calculator.spec" ]; then
    rm -f "NDFL_Calculator.spec"
    echo "- Removed NDFL_Calculator.spec"
fi

# Удаляем __pycache__
if [ -d "__pycache__" ]; then
    rm -rf __pycache__
    echo "- Removed __pycache__/"
fi

# Рекурсивно удаляем все __pycache__ директории
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "- Removed all __pycache__ directories"

# Удаляем .pyc файлы
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "- Removed all .pyc files"

# Удаляем .pyo файлы
find . -type f -name "*.pyo" -delete 2>/dev/null
echo "- Removed all .pyo files"

# Удаляем .ruff_cache если есть
if [ -d ".ruff_cache" ]; then
    rm -rf .ruff_cache
    echo "- Removed .ruff_cache/"
fi

echo ""
echo "Cleanup complete!"
echo ""

