"""
Анализ и объяснение выбора вопросов 12 и 19 из опросника Овчаровой
Проверка, почему не использовались другие вопросы, особенно вопрос 2
"""
import os
import pandas as pd
import numpy as np
from scipy.stats import spearmanr

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
newtest_dir = os.path.join(parent_dir, "newtest")

print("=" * 80)
print("АНАЛИЗ ВЫБОРА ВОПРОСОВ 12 И 19 ИЗ ОПРОСНИКА ОВЧАРОВОЙ")
print("=" * 80)

# Загружаем данные
students_file = os.path.join(newtest_dir, "Опрос ученика (Ответы) Новый.csv")
students_df = pd.read_csv(students_file, encoding='utf-8-sig')

# Находим все вопросы Овчаровой
student_cols = students_df.columns.tolist()
ovcharova_questions = {}

for col in student_cols:
    col_str = str(col)
    # Вопросы Овчаровой
    for i in range(1, 21):
        if col_str.startswith(f"{i}. "):
            if 'Требует' in col_str or 'Нравится' in col_str or 'Предполагает' in col_str or \
               'Соответствует' in col_str or 'Позволяет' in col_str or 'Дает' in col_str or \
               'Является' in col_str or 'Близка' in col_str or 'Избрана' in col_str or \
               'Единственно' in col_str or 'Способствует' in col_str:
                ovcharova_questions[i] = {
                    'column': col,
                    'text': col_str
                }
                break

print(f"\nНайдено вопросов Овчаровой: {len(ovcharova_questions)}")
print("\nВсе вопросы опросника Овчаровой (мотивы выбора профессии):")
for i in sorted(ovcharova_questions.keys()):
    print(f"  {i}. {ovcharova_questions[i]['text'][:80]}...")

# Анализируем статистику по каждому вопросу
print("\n" + "=" * 80)
print("СТАТИСТИКА ПО ВСЕМ ВОПРОСАМ ОВЧАРОВОЙ")
print("=" * 80)

question_stats = []

for q_num, q_info in sorted(ovcharova_questions.items()):
    col = q_info['column']
    values = []
    
    for val in students_df[col]:
        try:
            num_val = float(val) if pd.notna(val) else None
            if num_val is not None:
                values.append(num_val)
        except:
            pass
    
    if len(values) > 0:
        question_stats.append({
            'question_num': q_num,
            'question_text': q_info['text'],
            'mean': np.mean(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'n': len(values),
            'variance': np.var(values)
        })

stats_df = pd.DataFrame(question_stats)

print("\nСтатистика по вопросам:")
print(f"{'№':<4} {'Среднее':<10} {'Ст.откл.':<10} {'Мин':<6} {'Макс':<6} {'Дисперсия':<10}")
print("-" * 60)
for _, row in stats_df.iterrows():
    print(f"{int(row['question_num']):<4} {row['mean']:<10.2f} {row['std']:<10.2f} {row['min']:<6.0f} {row['max']:<6.0f} {row['variance']:<10.2f}")

# Сравниваем вопросы 2, 12 и 19
print("\n" + "=" * 80)
print("СРАВНЕНИЕ ВОПРОСОВ 2, 12 И 19")
print("=" * 80)

q2_stats = stats_df[stats_df['question_num'] == 2].iloc[0] if len(stats_df[stats_df['question_num'] == 2]) > 0 else None
q12_stats = stats_df[stats_df['question_num'] == 12].iloc[0] if len(stats_df[stats_df['question_num'] == 12]) > 0 else None
q19_stats = stats_df[stats_df['question_num'] == 19].iloc[0] if len(stats_df[stats_df['question_num'] == 19]) > 0 else None

if q2_stats is not None:
    print(f"\nВопрос 2: {ovcharova_questions[2]['text'][:70]}...")
    print(f"  Среднее: {q2_stats['mean']:.2f}, Ст.отклонение: {q2_stats['std']:.2f}, Дисперсия: {q2_stats['variance']:.2f}")

if q12_stats is not None:
    print(f"\nВопрос 12: {ovcharova_questions[12]['text'][:70]}...")
    print(f"  Среднее: {q12_stats['mean']:.2f}, Ст.отклонение: {q12_stats['std']:.2f}, Дисперсия: {q12_stats['variance']:.2f}")

if q19_stats is not None:
    print(f"\nВопрос 19: {ovcharova_questions[19]['text'][:70]}...")
    print(f"  Среднее: {q19_stats['mean']:.2f}, Ст.отклонение: {q19_stats['std']:.2f}, Дисперсия: {q19_stats['variance']:.2f}")

# Анализируем теоретические основания выбора
print("\n" + "=" * 80)
print("ТЕОРЕТИЧЕСКИЙ АНАЛИЗ ВЫБОРА ВОПРОСОВ")
print("=" * 80)

analysis_text = """
ВОПРОС 12: "Дает возможности для роста профессионального мастерства"
- Связан с мотивом профессионального развития и карьерного роста
- Отражает стремление к самореализации через профессиональное совершенствование
- Может быть связан с установками родителей на развитие способностей ребенка

ВОПРОС 19: "Позволяет использовать профессиональные умения вне работы"
- Связан с мотивом интеграции профессии в личную жизнь
- Отражает желание применять профессиональные навыки в различных сферах
- Может быть связан с установками родителей на всестороннее развитие ребенка

ВОПРОС 2: "Нравится родителям"
- Связан с мотивом соответствия ожиданиям родителей
- Отражает зависимость выбора профессии от родительского одобрения
- Может иметь высокую корреляцию, но менее информативен для исследования
  самостоятельности выбора профессии
"""

print(analysis_text)

# Сохраняем анализ
output_file = os.path.join(script_dir, "анализ_выбора_вопросов.csv")
stats_df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\nСтатистика сохранена: {output_file}")

print("\n" + "=" * 80)
print("Анализ завершён!")
print("=" * 80)
