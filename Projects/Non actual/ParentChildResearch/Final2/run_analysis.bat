@echo off
chcp 65001 >nul
cd /d "%~dp0"
python full_correlation_analysis.py
pause
