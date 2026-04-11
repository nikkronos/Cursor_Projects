"""
Полный анализ корреляций с перепроверкой расчётов
Создаёт детальные расчёты для всех корреляций в формате примеров
"""
import os
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr, rankdata
import warnings
warnings.filterwarnings('ignore')

# Определяем пути
script_dir = os.path.dirname(os.path.abspath(__file__))
newtest_dir = os.path.join(os.path.dirname(script_dir), "newtest")

# Загружаем данные
print("=" * 80)
print("ПОЛНЫЙ АНАЛИЗ КОРРЕЛЯЦИЙ С ПЕРЕПРОВЕРКОЙ")
print("=" * 80)

parents_file = os.path.join(newtest_dir, "Опрос для родителей  (Ответы).csv")
students_file = os.path.join(newtest_dir, "Опрос ученика (Ответы) Новый.csv")

print("\n1. Загрузка данных...")
parents_df = pd.read_csv(parents_file, encoding='utf-8-sig')
students_df = pd.read_csv(students_file, encoding='utf-8-sig')

print(f"   Родителей: {len(parents_df)}")
print(f"   Учеников: {len(students_df)}")

# Определяем столбцы
# Вопросы родителей (ВРР Марковской): с 6-го столбца (после метаданных)
parent_questions = parents_df.columns[6:66].tolist()  # 60 вопросов
print(f"\n2. Вопросов родителей (ВРР Марковской): {len(parent_questions)}")

# Вопросы Овчаровой (мотивы выбора профессии): последние 20 столбцов
student_cols = students_df.columns.tolist()

# Находим столбцы с вопросами Овчаровой
q12_col = None
q19_col = None
ovcharova_all_cols = []

for col in student_cols:
    col_str = str(col)
    # Ищем вопросы Овчаровой (начинаются с "1. Требует", "2. Нравится" и т.д.)
    if any(col_str.startswith(f"{i}. ") for i in range(1, 21)):
        if 'Требует' in col_str or 'Нравится' in col_str or 'Предполагает' in col_str or \
           'Соответствует' in col_str or 'Позволяет' in col_str or 'Дает' in col_str or \
           'Является' in col_str or 'Близка' in col_str or 'Избрана' in col_str:
            ovcharova_all_cols.append(col)
            
            if '12. Дает возможности для роста профессионального мастерства' in col_str:
                q12_col = col
            if '19. Позволяет использовать профессиональные умения вне работы' in col_str:
                q19_col = col

print(f"   Найдено вопросов Овчаровой: {len(ovcharova_all_cols)}")
print(f"   Вопрос 12 Овчаровой: {q12_col}")
print(f"   Вопрос 19 Овчаровой: {q19_col}")

if not q12_col or not q19_col:
    print("\nОШИБКА: Не найдены вопросы 12 и 19 Овчаровой!")
    exit(1)

# Сопоставляем пары по Number
print("\n3. Сопоставление пар родитель-ребенок...")
if 'Number' in parents_df.columns and 'Number' in students_df.columns:
    parents_sorted = parents_df.sort_values('Number').reset_index(drop=True)
    students_sorted = students_df.sort_values('Number').reset_index(drop=True)
    
    pairs_data = []
    for i in range(min(len(parents_sorted), len(students_sorted))):
        p_num = parents_sorted.iloc[i]['Number'] if pd.notna(parents_sorted.iloc[i]['Number']) else None
        s_num = students_sorted.iloc[i]['Number'] if pd.notna(students_sorted.iloc[i]['Number']) else None
        
        if p_num is not None and s_num is not None and p_num == s_num:
            pairs_data.append({
                'pair_id': i + 1,
                'parent_idx': i,
                'student_idx': i,
                'number': p_num
            })
    
    print(f"   Найдено пар: {len(pairs_data)}")
else:
    print("   ⚠ Столбец 'Number' не найден")
    pairs_data = [{'pair_id': i+1, 'parent_idx': i, 'student_idx': i, 'number': i+1} 
                  for i in range(min(len(parents_df), len(students_df)))]
    print(f"   Создано пар по порядку: {len(pairs_data)}")

# Перепроверяем все корреляции
print("\n4. Перепроверка корреляций...")

results = []

for parent_q in parent_questions:
    # Получаем данные для вопроса 12
    parent_vals_12 = []
    q12_vals = []
    
    # Получаем данные для вопроса 19
    parent_vals_19 = []
    q19_vals = []
    
    for pair in pairs_data:
        p_idx = pair['parent_idx']
        s_idx = pair['student_idx']
        
        if p_idx < len(parents_sorted) and s_idx < len(students_sorted):
            # Данные для вопроса 12
            p_val = parents_sorted.iloc[p_idx][parent_q]
            s12_val = students_sorted.iloc[s_idx][q12_col]
            
            # Данные для вопроса 19
            s19_val = students_sorted.iloc[s_idx][q19_col]
            
            # Преобразуем в числовые
            try:
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
            r12, p12_pearson = pearsonr(parent_vals_12, q12_vals)
            
            results.append({
                'parent_question': parent_q,
                'ovcharova_question': '12. Дает возможности для роста профессионального мастерства',
                'parent_values': parent_vals_12.copy(),
                'ovcharova_values': q12_vals.copy(),
                'spearman_corr': rho12,
                'spearman_p': p12,
                'pearson_corr': r12,
                'pearson_p': p12_pearson,
                'n': len(parent_vals_12)
            })
        except:
            pass
    
    # Корреляция с вопросом 19
    if len(parent_vals_19) >= 3:
        try:
            rho19, p19 = spearmanr(parent_vals_19, q19_vals)
            r19, p19_pearson = pearsonr(parent_vals_19, q19_vals)
            
            results.append({
                'parent_question': parent_q,
                'ovcharova_question': '19. Позволяет использовать профессиональные умения вне работы',
                'parent_values': parent_vals_19.copy(),
                'ovcharova_values': q19_vals.copy(),
                'spearman_corr': rho19,
                'spearman_p': p19,
                'pearson_corr': r19,
                'pearson_p': p19_pearson,
                'n': len(parent_vals_19)
            })
        except:
            pass

print(f"   Перепроверено корреляций: {len(results)}")

# Сохраняем результаты для детальных расчётов
import pickle
results_file = os.path.join(script_dir, "correlation_results_detailed.pkl")
with open(results_file, 'wb') as f:
    pickle.dump(results, f)

print(f"\n5. Результаты сохранены для детальных расчётов: {results_file}")

# Статистика
significant = [r for r in results if r['spearman_p'] < 0.05]
print(f"\n6. Статистика:")
print(f"   Всего корреляций: {len(results)}")
print(f"   Статистически значимых (p < 0.05): {len(significant)}")
print(f"   Сильных корреляций (|ρ| > 0.3): {len([r for r in results if abs(r['spearman_corr']) > 0.3])}")

# Топ корреляций
top_10 = sorted(results, key=lambda x: abs(x['spearman_corr']), reverse=True)[:10]
print(f"\n7. Топ-10 самых сильных корреляций:")
for i, r in enumerate(top_10, 1):
    sig = "***" if r['spearman_p'] < 0.001 else "**" if r['spearman_p'] < 0.01 else "*" if r['spearman_p'] < 0.05 else ""
    print(f"   {i}. {sig} ρ={r['spearman_corr']:.4f} (p={r['spearman_p']:.4f})")
    print(f"      Родитель: {r['parent_question'][:60]}...")
    print(f"      Овчарова: {r['ovcharova_question'][:60]}...")

print("\n" + "=" * 80)
print("Перепроверка завершена!")
print("=" * 80)
