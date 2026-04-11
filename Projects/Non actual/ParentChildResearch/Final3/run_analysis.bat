@echo off
chcp 65001 >nul
cd /d "%~dp0"
python enhanced_analysis.py
pause
