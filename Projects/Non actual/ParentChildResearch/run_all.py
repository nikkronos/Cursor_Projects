"""
Главный скрипт для запуска всех скриптов обработки данных в правильной последовательности
"""
import os
import sys
import subprocess

base_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_dir)

scripts = [
    'scripts/convert_profession_choices.py',  # 1. Преобразование текстовых ответов в числовые
    'scripts/analyze_data.py',  # 2. Анализ данных и сопоставление пар
    'scripts/analyze_parent_child_choice_correlations.py',  # 3. Анализ корреляций выбора
    'scripts/generate_data.py',  # 4. Генерация новых данных
    'scripts/validate_data.py',  # 5. Валидация данных
    'scripts/export_to_xlsx.py',  # 6. Экспорт в XLSX
]

print("=" * 60)
print("ЗАПУСК ПОЛНОГО ЦИКЛА ОБРАБОТКИ ДАННЫХ")
print("=" * 60)

for i, script in enumerate(scripts, 1):
    script_path = os.path.join(base_dir, script)
    
    if not os.path.exists(script_path):
        print(f"\n⚠ Предупреждение: скрипт {script} не найден, пропускаем...")
        continue
    
    print(f"\n{'=' * 60}")
    print(f"Шаг {i}/{len(scripts)}: {script}")
    print('=' * 60)
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=base_dir,
            capture_output=False,
            text=True
        )
        
        if result.returncode != 0:
            print(f"\n✗ Ошибка при выполнении {script}")
            print("Продолжить выполнение? (y/n): ", end='')
            response = input().strip().lower()
            if response != 'y':
                print("Выполнение прервано пользователем.")
                break
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        print("Продолжить выполнение? (y/n): ", end='')
        response = input().strip().lower()
        if response != 'y':
            print("Выполнение прервано пользователем.")
            break

print("\n" + "=" * 60)
print("ВСЕ СКРИПТЫ ВЫПОЛНЕНЫ!")
print("=" * 60)








