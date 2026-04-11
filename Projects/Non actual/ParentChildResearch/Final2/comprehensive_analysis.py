"""
Комплексный анализ корреляций:
1. Перепроверка всех расчётов
2. Создание детальных расчётов в формате примеров
3. Проверка итоговых результатов по Овчаровой
4. Объяснение выбора вопросов 12 и 19
"""
import os
import sys
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr, rankdata
import warnings
warnings.filterwarnings('ignore')

# Добавляем путь к newtest для импорта данных
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
newtest_dir = os.path.join(parent_dir, "newtest")

# Загружаем данные
print("=" * 80)
print("КОМПЛЕКСНЫЙ АНАЛИЗ КОРРЕЛЯЦИЙ")
print("=" * 80)

parents_file = os.path.join(newtest_dir, "Опрос для родителей  (Ответы).csv")
students_file = os.path.join(newtest_dir, "Опрос ученика (Ответы) Новый.csv")
existing_correlations = os.path.join(newtest_dir, "correlations_analysis.csv")

print("\n1. Загрузка данных...")
parents_df = pd.read_csv(parents_file, encoding='utf-8-sig')
students_df = pd.read_csv(students_file, encoding='utf-8-sig')
existing_corr_df = pd.read_csv(existing_correlations, encoding='utf-8-sig')

print(f"   Родителей: {len(parents_df)}")
print(f"   Учеников: {len(students_df)}")
print(f"   Существующих корреляций: {len(existing_corr_df)}")

# Определяем структуру данных
# Родители: столбцы 0-5 - метаданные, столбцы 6-65 - 60 вопросов ВРР Марковской
parent_meta_cols = parents_df.columns[:6].tolist()
parent_questions = parents_df.columns[6:66].tolist()

print(f"\n2. Структура данных родителей:")
print(f"   Метаданные: {len(parent_meta_cols)} столбцов")
print(f"   Вопросы ВРР Марковской: {len(parent_questions)}")

# Ученики: ищем вопросы Овчаровой (последние 20 столбцов)
student_cols = students_df.columns.tolist()

# Находим вопросы Овчаровой
q12_col = None
q19_col = None
ovcharova_cols = []

for col in student_cols:
    col_str = str(col)
    # Вопросы Овчаровой начинаются с "1. Требует", "2. Нравится" и т.д.
    if col_str.startswith("1. Требует") or col_str.startswith("2. Нравится") or \
       col_str.startswith("12. Дает возможности") or col_str.startswith("19. Позволяет использовать"):
        ovcharova_cols.append(col)
        
        if "12. Дает возможности для роста профессионального мастерства" in col_str:
            q12_col = col
        if "19. Позволяет использовать профессиональные умения вне работы" in col_str:
            q19_col = col

print(f"\n3. Структура данных учеников:")
print(f"   Всего столбцов: {len(student_cols)}")
print(f"   Найдено вопросов Овчаровой: {len(ovcharova_cols)}")
print(f"   Вопрос 12: {q12_col}")
print(f"   Вопрос 19: {q19_col}")

if not q12_col or not q19_col:
    print("\nОШИБКА: Не найдены вопросы 12 и 19 Овчаровой!")
    sys.exit(1)

# Сопоставляем пары
print("\n4. Сопоставление пар родитель-ребенок...")
if 'Number' in parents_df.columns and 'Number' in students_df.columns:
    parents_sorted = parents_df.sort_values('Number').reset_index(drop=True)
    students_sorted = students_df.sort_values('Number').reset_index(drop=True)
    
    pairs = []
    for i in range(min(len(parents_sorted), len(students_sorted))):
        p_num = parents_sorted.iloc[i]['Number'] if pd.notna(parents_sorted.iloc[i]['Number']) else None
        s_num = students_sorted.iloc[i]['Number'] if pd.notna(students_sorted.iloc[i]['Number']) else None
        
        if p_num is not None and s_num is not None and p_num == s_num:
            pairs.append({
                'pair_id': len(pairs) + 1,
                'parent_idx': i,
                'student_idx': i,
                'number': p_num
            })
    
    print(f"   Найдено пар: {len(pairs)}")
else:
    print("   ⚠ Столбец 'Number' не найден, используем порядковый номер")
    pairs = [{'pair_id': i+1, 'parent_idx': i, 'student_idx': i, 'number': i+1} 
             for i in range(min(len(parents_df), len(students_df)))]
    parents_sorted = parents_df.reset_index(drop=True)
    students_sorted = students_df.reset_index(drop=True)

# Перепроверяем корреляции
print("\n5. Перепроверка корреляций...")

verified_results = []

for parent_q in parent_questions:
    # Для вопроса 12
    parent_vals_12 = []
    q12_vals = []
    
    # Для вопроса 19
    parent_vals_19 = []
    q19_vals = []
    
    for pair in pairs:
        p_idx = pair['parent_idx']
        s_idx = pair['student_idx']
        
        if p_idx < len(parents_sorted) and s_idx < len(students_sorted):
            try:
                p_val = parents_sorted.iloc[p_idx][parent_q]
                s12_val = students_sorted.iloc[s_idx][q12_col]
                s19_val = students_sorted.iloc[s_idx][q19_col]
                
                p_num = float(p_val) if pd.notna(p_val) else None
                s12_num = float(s12_val) if pd.notna(s12_val) else None
                s19_num = float(s19_val) if pd.notna(s19_val) else None
                
                if p_num is not None and s12_num is not None:
                    parent_vals_12.append(p_num)
                    q12_vals.append(s12_num)
                
                if p_num is not None and s19_num is not None:
                    parent_vals_19.append(p_num)
                    q19_vals.append(s19_num)
            except:
                pass
    
    # Корреляция с вопросом 12
    if len(parent_vals_12) >= 3:
        try:
            rho12, p12 = spearmanr(parent_vals_12, q12_vals)
            r12, p12_p = pearsonr(parent_vals_12, q12_vals)
            
            verified_results.append({
                'parent_question': parent_q,
                'ovcharova_question': '12. Дает возможности для роста профессионального мастерства',
                'parent_values': parent_vals_12,
                'ovcharova_values': q12_vals,
                'spearman_corr': rho12,
                'spearman_p': p12,
                'pearson_corr': r12,
                'pearson_p': p12_p,
                'n': len(parent_vals_12)
            })
        except Exception as e:
            print(f"   Ошибка при расчёте корреляции для {parent_q[:30]}... с вопросом 12: {e}")
    
    # Корреляция с вопросом 19
    if len(parent_vals_19) >= 3:
        try:
            rho19, p19 = spearmanr(parent_vals_19, q19_vals)
            r19, p19_p = pearsonr(parent_vals_19, q19_vals)
            
            verified_results.append({
                'parent_question': parent_q,
                'ovcharova_question': '19. Позволяет использовать профессиональные умения вне работы',
                'parent_values': parent_vals_19,
                'ovcharova_values': q19_vals,
                'spearman_corr': rho19,
                'spearman_p': p19,
                'pearson_corr': r19,
                'pearson_p': p19_p,
                'n': len(parent_vals_19)
            })
        except Exception as e:
            print(f"   Ошибка при расчёте корреляции для {parent_q[:30]}... с вопросом 19: {e}")

print(f"   Перепроверено корреляций: {len(verified_results)}")

# Сравнение с существующими результатами
print("\n6. Сравнение с существующими результатами...")
matches = 0
mismatches = 0

for verified in verified_results:
    # Ищем соответствующую строку в существующих результатах
    existing = existing_corr_df[
        (existing_corr_df['parent_question'] == verified['parent_question']) &
        (existing_corr_df['profession_question'] == verified['ovcharova_question'])
    ]
    
    if len(existing) > 0:
        existing_row = existing.iloc[0]
        existing_rho = existing_row['spearman_correlation']
        verified_rho = verified['spearman_corr']
        
        # Сравниваем с точностью до 0.001
        if abs(existing_rho - verified_rho) < 0.001:
            matches += 1
        else:
            mismatches += 1
            print(f"   ⚠ Расхождение: {verified['parent_question'][:40]}...")
            print(f"      Существующее: {existing_rho:.6f}, Перепроверенное: {verified_rho:.6f}")

print(f"   Совпадений: {matches}")
print(f"   Расхождений: {mismatches}")

# Сохраняем результаты
results_file = os.path.join(script_dir, "verified_correlations.csv")
results_df = pd.DataFrame([{
    'parent_question': r['parent_question'],
    'ovcharova_question': r['ovcharova_question'],
    'spearman_correlation': r['spearman_corr'],
    'spearman_p_value': r['spearman_p'],
    'pearson_correlation': r['pearson_corr'],
    'pearson_p_value': r['pearson_p'],
    'n_pairs': r['n']
} for r in verified_results])

results_df.to_csv(results_file, index=False, encoding='utf-8-sig')
print(f"\n7. Результаты сохранены: {results_file}")

# Сохраняем детальные данные для расчётов
import pickle
detailed_file = os.path.join(script_dir, "detailed_correlation_data.pkl")
with open(detailed_file, 'wb') as f:
    pickle.dump(verified_results, f)
print(f"   Детальные данные сохранены: {detailed_file}")

# Статистика
significant = [r for r in verified_results if r['spearman_p'] < 0.05]
strong = [r for r in verified_results if abs(r['spearman_corr']) > 0.3]

print(f"\n8. Статистика:")
print(f"   Всего корреляций: {len(verified_results)}")
print(f"   Статистически значимых (p < 0.05): {len(significant)}")
print(f"   Сильных корреляций (|ρ| > 0.3): {len(strong)}")

# Топ корреляций
top_10 = sorted(verified_results, key=lambda x: abs(x['spearman_corr']), reverse=True)[:10]
print(f"\n9. Топ-10 самых сильных корреляций:")
for i, r in enumerate(top_10, 1):
    sig = "***" if r['spearman_p'] < 0.001 else "**" if r['spearman_p'] < 0.01 else "*" if r['spearman_p'] < 0.05 else ""
    print(f"   {i}. {sig} ρ={r['spearman_corr']:.4f} (p={r['spearman_p']:.4f}, n={r['n']})")
    print(f"      Родитель: {r['parent_question'][:70]}")
    print(f"      Овчарова: {r['ovcharova_question'][:70]}")

print("\n" + "=" * 80)
print("Перепроверка завершена!")
print("=" * 80)
