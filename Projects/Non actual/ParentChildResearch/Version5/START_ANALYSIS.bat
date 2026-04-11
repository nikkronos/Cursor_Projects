@echo off
chcp 65001
cd /d "%~dp0"
echo Запуск анализа документа v7...
python analyze_v7.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Анализ завершен успешно!
    echo Результаты сохранены в ANALYSIS_RESULTS.txt
) else (
    echo.
    echo ОШИБКА при выполнении анализа!
)
pause




