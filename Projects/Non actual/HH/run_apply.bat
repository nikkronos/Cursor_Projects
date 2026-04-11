@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo АВТОМАТИЗАЦИЯ ОТКЛИКОВ НА HEADHUNTER
echo ========================================
echo.
echo Убедитесь, что:
echo 1. Вы залогинены на hh.ru в браузере
echo 2. В env_vars.txt указано сопроводительное письмо
echo.
pause
python scripts\apply_to_vacancies.py
pause






















