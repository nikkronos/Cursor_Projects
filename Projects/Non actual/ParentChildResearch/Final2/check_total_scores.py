"""
Проверка: исследовали ли корреляцию итогового результата каждого подростка 
по методике Овчаровой с итоговыми результатами других методик
"""
import os
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
newtest_dir = os.path.join(parent_dir, "newtest")

print("=" * 80)
print("ПРОВЕРКА ИТОГОВЫХ РЕЗУЛЬТАТОВ ПО ОВЧАРОВОЙ")
print("=" * 80)

# Загружаем данные
students_file = os.path.join(newtest_dir, "Опрос ученика (Ответы) Новый.csv")
students_df = pd.read_csv(students_file, encoding='utf-8-sig')

print(f"\nЗагружено учеников: {len(students_df)}")

# Находим все вопросы Овчаровой (20 вопросов)
student_cols = students_df.columns.tolist()
ovcharova_cols = []

for col in student_cols:
    col_str = str(col)
    # Вопросы Овчаровой начинаются с "1. Требует", "2. Нравится" и т.д.
    if any(col_str.startswith(f"{i}. ") for i in range(1, 21)):
        if 'Требует' in col_str or 'Нравится' in col_str or 'Предполагает' in col_str or \
           'Соответствует' in col_str or 'Позволяет' in col_str or 'Дает' in col_str or \
           'Является' in col_str or 'Близка' in col_str or 'Избрана' in col_str or \
           'Единственно' in col_str or 'Способствует' in col_str:
            ovcharova_cols.append(col)

print(f"\nНайдено вопросов Овчаровой: {len(ovcharova_cols)}")
if len(ovcharova_cols) > 0:
    print("Примеры:")
    for i, col in enumerate(ovcharova_cols[:5], 1):
        print(f"  {i}. {col}")

# Рассчитываем итоговый балл по Овчаровой для каждого подростка
print("\n" + "=" * 80)
print("РАСЧЁТ ИТОГОВЫХ БАЛЛОВ ПО ОВЧАРОВОЙ")
print("=" * 80)

total_scores = []

for idx, row in students_df.iterrows():
    scores = []
    for col in ovcharova_cols:
        val = row[col]
        try:
            num_val = float(val) if pd.notna(val) else None
            if num_val is not None:
                scores.append(num_val)
        except:
            pass
    
    if len(scores) > 0:
        total_score = sum(scores)
        total_scores.append({
            'student_idx': idx,
            'number': row['Number'] if 'Number' in row and pd.notna(row['Number']) else idx + 1,
            'total_ovcharova': total_score,
            'n_questions': len(scores)
        })

total_scores_df = pd.DataFrame(total_scores)
print(f"\nРассчитано итоговых баллов: {len(total_scores_df)}")
print(f"Средний итоговый балл: {total_scores_df['total_ovcharova'].mean():.2f}")
print(f"Медианный итоговый балл: {total_scores_df['total_ovcharova'].median():.2f}")
print(f"Минимальный балл: {total_scores_df['total_ovcharova'].min():.2f}")
print(f"Максимальный балл: {total_scores_df['total_ovcharova'].max():.2f}")

# Проверяем, есть ли в существующих корреляциях итоговые результаты
existing_correlations = os.path.join(newtest_dir, "correlations_analysis.csv")
existing_corr_df = pd.read_csv(existing_correlations, encoding='utf-8-sig')

print("\n" + "=" * 80)
print("ПРОВЕРКА: ИСПОЛЬЗОВАЛИСЬ ЛИ ИТОГОВЫЕ РЕЗУЛЬТАТЫ?")
print("=" * 80)

# Ищем в существующих корреляциях упоминания итоговых результатов
total_mentioned = False
for col in existing_corr_df.columns:
    if 'итог' in str(col).lower() or 'total' in str(col).lower() or 'сумма' in str(col).lower():
        total_mentioned = True
        break

for idx, row in existing_corr_df.iterrows():
    if 'итог' in str(row['profession_question']).lower() or 'total' in str(row['profession_question']).lower() or \
       'сумма' in str(row['profession_question']).lower():
        total_mentioned = True
        print(f"\n✓ Найдена корреляция с итоговым результатом:")
        print(f"  {row['parent_question'][:60]}...")
        print(f"  {row['profession_question']}")
        break

if not total_mentioned:
    print("\n⚠ ИТОГОВЫЕ РЕЗУЛЬТАТЫ ПО ОВЧАРОВОЙ НЕ ИСПОЛЬЗОВАЛИСЬ В КОРРЕЛЯЦИОННОМ АНАЛИЗЕ")
    print("  В существующих корреляциях используются только отдельные вопросы 12 и 19")
    print("  Итоговый балл (сумма всех 20 вопросов) не рассчитывался")

# Сохраняем итоговые баллы
output_file = os.path.join(script_dir, "итоговые_баллы_овчарова.csv")
total_scores_df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\nИтоговые баллы сохранены: {output_file}")

print("\n" + "=" * 80)
print("Проверка завершена!")
print("=" * 80)
