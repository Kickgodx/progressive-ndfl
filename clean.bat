@echo off
REM Wrapper script for cleaning build artifacts
REM Calls the actual clean script from build_tools folder

cd /d "%~dp0"
call build_tools\clean.bat

