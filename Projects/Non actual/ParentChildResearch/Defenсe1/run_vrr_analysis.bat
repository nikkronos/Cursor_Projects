@echo off
chcp 65001 >nul
cd /d "%~dp0"
python vrr_scales_analysis.py
pause
