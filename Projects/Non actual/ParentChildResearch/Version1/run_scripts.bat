@echo off
chcp 65001 >nul
echo ========================================
echo Генерация графиков для Главы II
echo ========================================
cd /d "%~dp0"
python generate_charts.py
pause


















