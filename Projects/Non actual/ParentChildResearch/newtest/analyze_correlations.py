"""Анализ корреляций между установками родителей и выбором профессии детьми"""
import os
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr
import warnings
warnings.filterwarnings('ignore')

# Определяем путь к папке со скриптом
script_dir = os.path.dirname(os.path.abspath(__file__))

# Файлы для анализа
parents_file = os.path.join(script_dir, "Опрос для родителей  (Ответы).csv")
students_file = os.path.join(script_dir, "Опрос ученика (Ответы) Новый.csv")

print("=" * 80)
print("АНАЛИЗ КОРРЕЛЯЦИЙ: ВЛИЯНИЕ УСТАНОВОК РОДИТЕЛЕЙ НА ВЫБОР ПРОФЕССИИ ДЕТЬМИ")
print("=" * 80)

# Загружаем данные
print("\n1. Загрузка данных...")
parents_df = pd.read_csv(parents_file, encoding='utf-8-sig')
students_df = pd.read_csv(students_file, encoding='utf-8-sig')

print(f"   Загружено родителей: {len(parents_df)}")
print(f"   Загружено учеников: {len(students_df)}")
print(f"   Столбцов у родителей: {len(parents_df.columns)}")
print(f"   Столбцов у учеников: {len(students_df.columns)}")

# Показываем первые несколько столбцов для понимания структуры
print("\n2. Анализ структуры данных...")
print("\n   Первые столбцы родителей:")
for i, col in enumerate(parents_df.columns[:10]):
    print(f"      {i}: {col}")

print("\n   Первые столбцы учеников:")
for i, col in enumerate(students_df.columns[:10]):
    print(f"      {i}: {col}")

# Ищем столбец Number для сопоставления пар
print("\n3. Сопоставление пар родитель-ребенок...")
if 'Number' in parents_df.columns and 'Number' in students_df.columns:
    # Сортируем по Number
    parents_df = parents_df.sort_values('Number').reset_index(drop=True)
    students_df = students_df.sort_values('Number').reset_index(drop=True)
    
    # Создаем пары
    pairs = []
    for i in range(min(len(parents_df), len(students_df))):
        parent_num = parents_df.iloc[i]['Number'] if pd.notna(parents_df.iloc[i]['Number']) else None
        student_num = students_df.iloc[i]['Number'] if pd.notna(students_df.iloc[i]['Number']) else None
        
        if parent_num is not None and student_num is not None and parent_num == student_num:
            pairs.append({
                'pair_id': i + 1,
                'parent_index': i,
                'student_index': i,
                'number': parent_num
            })
    
    print(f"   Найдено пар: {len(pairs)}")
else:
    print("   ⚠ Столбец 'Number' не найден. Используем порядковый номер строки.")
    pairs = []
    for i in range(min(len(parents_df), len(students_df))):
        pairs.append({
            'pair_id': i + 1,
            'parent_index': i,
            'student_index': i,
            'number': i + 1
        })
    print(f"   Создано пар: {len(pairs)}")

pairs_df = pd.DataFrame(pairs)

# Определяем столбцы с ответами родителей (исключая метаданные)
# Обычно первые столбцы - это метаданные (Number, имя, дата и т.д.)
print("\n4. Определение столбцов с данными...")

# Ищем столбцы с вопросами родителей (обычно это числовые или текстовые ответы)
# Пропускаем первые несколько столбцов (метаданные)
parent_meta_cols = ['Number']
for col in parents_df.columns:
    if col not in parent_meta_cols and not col.startswith('Unnamed'):
        parent_meta_cols.append(col)
        if len(parent_meta_cols) >= 5:  # Первые 5 столбцов обычно метаданные
            break

parent_data_start = len(parent_meta_cols)
print(f"   Столбцы метаданных родителей: {parent_data_start}")
print(f"   Столбцы с ответами родителей: {len(parents_df.columns) - parent_data_start}")

# Ищем столбцы с выбором профессии у детей
# Обычно это вопросы о профессиях (ProfQ или похожие)
student_prof_cols = []
for col in students_df.columns:
    col_lower = str(col).lower()
    if 'prof' in col_lower or 'професс' in col_lower or 'проф' in col_lower:
        student_prof_cols.append(col)

print(f"   Найдено столбцов с выбором профессии у детей: {len(student_prof_cols)}")
if student_prof_cols:
    print(f"   Примеры: {student_prof_cols[:5]}")

# Ищем столбцы с ответами детей (вопросы, установки)
student_meta_cols = ['Number']
for col in students_df.columns:
    if col not in student_meta_cols and not col.startswith('Unnamed'):
        student_meta_cols.append(col)
        if len(student_meta_cols) >= 5:
            break

student_data_start = len(student_meta_cols)
print(f"   Столбцы метаданных учеников: {student_data_start}")
print(f"   Столбцы с ответами учеников: {len(students_df.columns) - student_data_start}")

# Функция для преобразования текстовых ответов в числовые
def text_to_numeric(value):
    """Преобразует текстовые ответы в числовые значения"""
    if pd.isna(value):
        return np.nan
    
    value_str = str(value).strip().lower()
    
    # Если уже число, возвращаем как есть
    try:
        return float(value)
    except:
        pass
    
    # Преобразование текстовых ответов
    # Типичные ответы в психологических опросах: "да/нет", "согласен/не согласен", шкала Лайкерта и т.д.
    mapping = {
        'да': 1, 'нет': 0,
        'согласен': 1, 'не согласен': 0,
        'полностью согласен': 5, 'согласен': 4, 'нейтрально': 3, 'не согласен': 2, 'полностью не согласен': 1,
        'всегда': 5, 'часто': 4, 'иногда': 3, 'редко': 2, 'никогда': 1,
        'очень важно': 5, 'важно': 4, 'нейтрально': 3, 'не важно': 2, 'совсем не важно': 1,
    }
    
    for key, num in mapping.items():
        if key in value_str:
            return num
    
    # Если не найдено соответствие, пытаемся найти числа в тексте
    import re
    numbers = re.findall(r'\d+', value_str)
    if numbers:
        return float(numbers[0])
    
    # Если ничего не найдено, возвращаем NaN
    return np.nan

# Функция для кодирования категориальных данных
def encode_categorical(series):
    """Кодирует категориальные данные в числовые"""
    unique_vals = series.dropna().unique()
    if len(unique_vals) <= 2:
        # Бинарные данные
        mapping = {val: i for i, val in enumerate(sorted(unique_vals))}
    else:
        # Множественные категории - используем порядковое кодирование
        mapping = {val: i for i, val in enumerate(sorted(unique_vals))}
    
    return series.map(mapping)

print("\n5. Преобразование текстовых данных в числовые...")

# Преобразуем ответы родителей
parent_answer_cols = parents_df.columns[parent_data_start:]
print(f"   Обработка {len(parent_answer_cols)} столбцов ответов родителей...")

parent_numeric_data = {}
for col in parent_answer_cols:
    # Пробуем сначала как числовые
    numeric_vals = pd.to_numeric(parents_df[col], errors='coerce')
    
    # Если много NaN, пробуем текстовое преобразование
    if numeric_vals.isna().sum() > len(numeric_vals) * 0.5:
        numeric_vals = parents_df[col].apply(text_to_numeric)
    
    # Если все еще много NaN, используем категориальное кодирование
    if numeric_vals.isna().sum() > len(numeric_vals) * 0.5:
        numeric_vals = encode_categorical(parents_df[col])
    
    parent_numeric_data[col] = numeric_vals

# Преобразуем ответы детей о профессии
print(f"   Обработка столбцов выбора профессии у детей...")

student_prof_numeric = {}
if student_prof_cols:
    for col in student_prof_cols:
        numeric_vals = pd.to_numeric(students_df[col], errors='coerce')
        if numeric_vals.isna().sum() > len(numeric_vals) * 0.5:
            numeric_vals = students_df[col].apply(text_to_numeric)
        if numeric_vals.isna().sum() > len(numeric_vals) * 0.5:
            numeric_vals = encode_categorical(students_df[col])
        student_prof_numeric[col] = numeric_vals
else:
    # Если не найдены столбцы с профессией, ищем в последних столбцах
    print("   ⚠ Столбцы с профессией не найдены автоматически. Ищем в последних столбцах...")
    last_cols = students_df.columns[-20:]  # Последние 20 столбцов
    for col in last_cols:
        if col not in student_meta_cols:
            numeric_vals = pd.to_numeric(students_df[col], errors='coerce')
            if numeric_vals.isna().sum() < len(numeric_vals) * 0.8:  # Если меньше 80% NaN
                student_prof_numeric[col] = numeric_vals

print(f"   Найдено {len(student_prof_numeric)} столбцов с данными о профессии")

print("\n6. Расчет корреляций между установками родителей и выбором профессии детьми...")

correlations_results = []

for pair_idx, pair in pairs_df.iterrows():
    parent_idx = pair['parent_index']
    student_idx = pair['student_index']
    
    # Получаем ответы родителей
    parent_answers = {}
    for col in parent_answer_cols:
        val = parent_numeric_data[col].iloc[parent_idx]
        if pd.notna(val):
            parent_answers[col] = val
    
    # Получаем выбор профессии ребенком
    student_prof_answers = {}
    for col, series in student_prof_numeric.items():
        val = series.iloc[student_idx]
        if pd.notna(val):
            student_prof_answers[col] = val
    
    # Сохраняем данные для последующего анализа
    for parent_col, parent_val in parent_answers.items():
        for prof_col, prof_val in student_prof_answers.items():
            correlations_results.append({
                'pair_id': pair['pair_id'],
                'parent_question': parent_col,
                'profession_question': prof_col,
                'parent_answer': parent_val,
                'child_profession_choice': prof_val
            })

# Преобразуем в DataFrame
correlations_data_df = pd.DataFrame(correlations_results)

print(f"   Собрано {len(correlations_data_df)} пар данных для анализа")

# Рассчитываем корреляции для каждой комбинации вопросов
print("\n7. Расчет статистических корреляций...")

final_correlations = []

# Группируем по комбинациям вопросов
for (parent_q, prof_q), group in correlations_data_df.groupby(['parent_question', 'profession_question']):
    parent_vals = group['parent_answer'].values
    prof_vals = group['child_profession_choice'].values
    
    # Удаляем NaN
    mask = ~(np.isnan(parent_vals) | np.isnan(prof_vals))
    parent_clean = parent_vals[mask]
    prof_clean = prof_vals[mask]
    
    if len(parent_clean) >= 3:  # Минимум 3 пары для корреляции
        try:
            # Коэффициент Спирмена (для ранговых данных)
            spearman_corr, spearman_p = spearmanr(parent_clean, prof_clean)
            
            # Коэффициент Пирсона (для линейных зависимостей)
            pearson_corr, pearson_p = pearsonr(parent_clean, prof_clean)
            
            final_correlations.append({
                'parent_question': parent_q,
                'profession_question': prof_q,
                'spearman_correlation': spearman_corr,
                'spearman_p_value': spearman_p,
                'pearson_correlation': pearson_corr,
                'pearson_p_value': pearson_p,
                'n_pairs': len(parent_clean)
            })
        except Exception as e:
            pass  # Игнорируем ошибки

correlations_df = pd.DataFrame(final_correlations)

print(f"   Рассчитано корреляций: {len(correlations_df)}")

# Сохраняем результаты
output_file = os.path.join(script_dir, "correlations_analysis.csv")
correlations_df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n8. Результаты сохранены в: {output_file}")

# Выводим статистику
print("\n" + "=" * 80)
print("РЕЗУЛЬТАТЫ АНАЛИЗА")
print("=" * 80)

if len(correlations_df) > 0:
    print(f"\nОбщая статистика (коэффициент Спирмена):")
    print(f"  Средняя корреляция: {correlations_df['spearman_correlation'].mean():.4f}")
    print(f"  Медианная корреляция: {correlations_df['spearman_correlation'].median():.4f}")
    print(f"  Минимальная корреляция: {correlations_df['spearman_correlation'].min():.4f}")
    print(f"  Максимальная корреляция: {correlations_df['spearman_correlation'].max():.4f}")
    
    # Статистически значимые корреляции (p < 0.05)
    significant = correlations_df[correlations_df['spearman_p_value'] < 0.05]
    print(f"\n  Статистически значимых корреляций (p < 0.05): {len(significant)}")
    if len(significant) > 0:
        print(f"  Средняя значимая корреляция: {significant['spearman_correlation'].mean():.4f}")
    
    # Топ-20 самых сильных корреляций
    top_correlations = correlations_df.nlargest(20, 'spearman_correlation')
    print(f"\nТоп-20 самых сильных корреляций (коэффициент Спирмена):")
    for idx, row in top_correlations.iterrows():
        sig_mark = "***" if row['spearman_p_value'] < 0.001 else "**" if row['spearman_p_value'] < 0.01 else "*" if row['spearman_p_value'] < 0.05 else ""
        print(f"  {sig_mark} Вопрос родителя '{row['parent_question'][:50]}...' <-> "
              f"Профессия '{row['profession_question'][:50]}...': "
              f"{row['spearman_correlation']:.4f} (p={row['spearman_p_value']:.4f}, n={row['n_pairs']})")
    
    # Выводы
    print("\n" + "=" * 80)
    print("ВЫВОДЫ")
    print("=" * 80)
    
    strong_correlations = correlations_df[abs(correlations_df['spearman_correlation']) > 0.3]
    if len(strong_correlations) > 0:
        print(f"\n✓ Найдено {len(strong_correlations)} сильных корреляций (|r| > 0.3)")
        print("  Это указывает на наличие связи между установками родителей и выбором профессии детьми.")
    else:
        print("\n⚠ Сильных корреляций не найдено (|r| > 0.3)")
        print("  Это может указывать на отсутствие прямой связи или необходимость более глубокого анализа.")
    
    if len(significant) > 0:
        print(f"\n✓ Найдено {len(significant)} статистически значимых корреляций (p < 0.05)")
        print("  Гипотеза о влиянии установок родителей на выбор профессии детьми ПОДТВЕРЖДЕНА.")
    else:
        print(f"\n⚠ Статистически значимых корреляций не найдено (p < 0.05)")
        print("  Гипотеза о влиянии установок родителей на выбор профессии детьми НЕ ПОДТВЕРЖДЕНА.")
else:
    print("\n⚠ Не удалось рассчитать корреляции. Проверьте структуру данных.")

print("\n" + "=" * 80)
print("Анализ завершен!")
print("=" * 80)

