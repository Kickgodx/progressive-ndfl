@echo off
REM Wrapper script for building EXE
REM Calls the actual build script from build_tools folder

cd /d "%~dp0"
call build_tools\build.bat

