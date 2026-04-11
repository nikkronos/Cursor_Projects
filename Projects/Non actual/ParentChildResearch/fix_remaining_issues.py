"""
Скрипт для исправления оставшихся проблем с преобразованием
"""
import pandas as pd
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
converted_file = os.path.join(base_dir, 'data', 'raw', 'students_survey_converted.csv')

print("Исправление оставшихся проблем...")
df = pd.read_csv(converted_file, encoding='utf-8-sig')

# Находим колонку с вопросом 26
col_26_idx = 64 + 25  # 26-й вопрос (индекс 25)
if col_26_idx < len(df.columns):
    col_26_name = df.columns[col_26_idx]
    print(f"Обработка колонки: {col_26_name}")
    
    fixed_count = 0
    for idx in df.index:
        value = df.at[idx, col_26_name]
        if pd.notna(value):
            value_str = str(value).lower()
            # Если это текст, а не число
            if not str(value).strip().isdigit():
                if 'трейдер' in value_str and 'биржевой' in value_str:
                    df.at[idx, col_26_name] = 2
                    fixed_count += 1
                    print(f"  Исправлена строка {idx+2}: установлено значение 2")
                elif 'преподаватель' in value_str:
                    df.at[idx, col_26_name] = 1
                    fixed_count += 1
                    print(f"  Исправлена строка {idx+2}: установлено значение 1")
    
    if fixed_count > 0:
        df.to_csv(converted_file, index=False, encoding='utf-8-sig')
        print(f"\n✓ Исправлено {fixed_count} значений")
    else:
        print("\n✓ Все значения уже корректны")

print("Готово!")








