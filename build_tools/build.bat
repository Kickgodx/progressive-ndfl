@echo off
chcp 65001 >nul

REM Change to project root directory
cd /d "%~dp0\.."

echo ========================================
echo Building NDFL Calculator EXE
echo ========================================
echo.

echo Installing dependencies...
pip install -r requirements.txt
echo.

echo Creating EXE file...
echo This may take a few minutes...
echo.

REM Remove old auto-generated spec file if it exists
if exist "NDFL_Calculator.spec" (
    del /q "NDFL_Calculator.spec"
    echo Removed old NDFL_Calculator.spec file
    echo.
)

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "NDFL_Calculator" ^
    --add-data "src;src" ^
    --hidden-import "tkinter" ^
    --hidden-import "matplotlib" ^
    --hidden-import "openpyxl" ^
    --hidden-import "decimal" ^
    --hidden-import "json" ^
    --hidden-import "csv" ^
    --collect-all "matplotlib" ^
    --collect-all "openpyxl" ^
    --noconsole ^
    main.py

echo.
if exist "dist\NDFL_Calculator.exe" (
    echo ========================================
    echo Success! EXE file created:
    echo   dist\NDFL_Calculator.exe
    echo ========================================
    echo.
    echo File size:
    dir "dist\NDFL_Calculator.exe" | find "NDFL_Calculator.exe"
) else (
    echo ========================================
    echo Error creating EXE file
    echo ========================================
)

echo.
pause

