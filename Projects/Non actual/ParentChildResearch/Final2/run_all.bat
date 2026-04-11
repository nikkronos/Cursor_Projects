@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo ЗАПУСК ПОЛНОГО АНАЛИЗА
echo ========================================
echo.
echo 1. Перепроверка корреляций...
python comprehensive_analysis.py
echo.
echo 2. Проверка итоговых результатов...
python check_total_scores.py
echo.
echo 3. Анализ выбора вопросов...
python explain_question_selection.py
echo.
echo 4. Создание документа с объяснениями...
python explanation_document.py
echo.
echo 5. Создание полного итогового отчёта...
python create_complete_report.py
echo.
echo ========================================
echo ВСЕ СКРИПТЫ ВЫПОЛНЕНЫ!
echo ========================================
pause
