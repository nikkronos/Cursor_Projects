@echo off
chcp 65001 >nul
cd /d "%~dp0"
python extra_analysis.py
pause
