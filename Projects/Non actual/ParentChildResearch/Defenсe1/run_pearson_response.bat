@echo off
chcp 65001 >nul
cd /d "%~dp0"
python create_pearson_response_doc.py
if errorlevel 1 pause
