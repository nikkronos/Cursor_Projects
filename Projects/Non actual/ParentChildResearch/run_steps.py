"""
Последовательное выполнение всех шагов обработки данных
"""
import os
import sys
import subprocess

base_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_dir)

steps = [
    {
        'name': 'Шаг 1: Копирование исходных CSV файлов',
        'script': 'step1_copy_files.py',
        'required': True
    },
    {
        'name': 'Шаг 2: Преобразование текстовых ответов в числовые',
        'script': 'scripts/convert_profession_choices.py',
        'required': True
    },
    {
        'name': 'Шаг 3: Анализ данных и сопоставление пар',
        'script': 'scripts/analyze_data.py',
        'required': True
    },
    {
        'name': 'Шаг 4: Анализ корреляций выбора',
        'script': 'scripts/analyze_parent_child_choice_correlations.py',
        'required': True
    },
    {
        'name': 'Шаг 5: Генерация новых данных',
        'script': 'scripts/generate_data.py',
        'required': True
    },
    {
        'name': 'Шаг 6: Валидация данных',
        'script': 'scripts/validate_data.py',
        'required': True
    },
    {
        'name': 'Шаг 7: Экспорт в XLSX',
        'script': 'scripts/export_to_xlsx.py',
        'required': True
    }
]

print("=" * 60)
print("ПОСЛЕДОВАТЕЛЬНОЕ ВЫПОЛНЕНИЕ ШАГОВ ОБРАБОТКИ ДАННЫХ")
print("=" * 60)

for i, step in enumerate(steps, 1):
    script_path = os.path.join(base_dir, step['script'])
    
    print(f"\n{'=' * 60}")
    print(f"{step['name']} ({i}/{len(steps)})")
    print('=' * 60)
    
    if not os.path.exists(script_path):
        print(f"⚠ Ошибка: скрипт {step['script']} не найден")
        if step['required']:
            print("Этот шаг обязателен. Прерывание выполнения.")
            break
        else:
            print("Пропускаем этот шаг...")
            continue
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=base_dir,
            capture_output=False,
            text=True
        )
        
        if result.returncode != 0:
            print(f"\n✗ Ошибка при выполнении шага {i}")
            if step['required']:
                print("Этот шаг обязателен. Прерывание выполнения.")
                break
            else:
                print("Продолжаем выполнение...")
        else:
            print(f"\n✓ Шаг {i} выполнен успешно")
            
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        if step['required']:
            print("Этот шаг обязателен. Прерывание выполнения.")
            break

print("\n" + "=" * 60)
print("ВЫПОЛНЕНИЕ ЗАВЕРШЕНО!")
print("=" * 60)








