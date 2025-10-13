@echo off

REM Change to project root directory
cd /d "%~dp0\.."

echo Cleaning build artifacts...

if exist "build" (
    rmdir /s /q build
    echo - Removed build/
)

if exist "dist" (
    rmdir /s /q dist
    echo - Removed dist/
)

if exist "__pycache__" (
    rmdir /s /q __pycache__
    echo - Removed __pycache__/
)

for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    rmdir /s /q "%%d"
    echo - Removed %%d
)

for /r . %%f in (*.pyc) do @if exist "%%f" (
    del /q "%%f"
    echo - Removed %%f
)

for /r . %%f in (*.pyo) do @if exist "%%f" (
    del /q "%%f"
    echo - Removed %%f
)

echo.
echo Cleanup complete!
pause

