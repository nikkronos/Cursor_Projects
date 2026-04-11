@echo off
chcp 65001 >nul
echo ========================================
echo Экспорт Главы II в Word документ
echo ========================================
cd /d "%~dp0"
python export_to_word.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Документ успешно создан!
    echo   Файл: ГЛАВА_II_ПОЛНАЯ.docx
) else (
    echo.
    echo ✗ Ошибка при создании документа
)
pause


















