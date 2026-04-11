"""Анализ значимых корреляций для подготовки текста Главы II"""
import pandas as pd
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
correlations_file = os.path.join(parent_dir, "newtest", "correlations_analysis.csv")

df = pd.read_csv(correlations_file, encoding='utf-8-sig')
df = df.dropna(subset=['spearman_correlation', 'spearman_p_value'])

# Значимые корреляции
significant = df[df['spearman_p_value'] < 0.05].copy()

print("=" * 80)
print("АНАЛИЗ ЗНАЧИМЫХ КОРРЕЛЯЦИЙ")
print("=" * 80)
print(f"\nВсего корреляций: {len(df)}")
print(f"Статистически значимых (p < 0.05): {len(significant)}")
print(f"Процент значимых: {len(significant)/len(df)*100:.1f}%")

if len(significant) > 0:
    print("\n" + "=" * 80)
    print("СТАТИСТИЧЕСКИ ЗНАЧИМЫЕ КОРРЕЛЯЦИИ:")
    print("=" * 80)
    
    # Сортируем по силе корреляции
    significant_sorted = significant.sort_values('spearman_correlation', ascending=False)
    
    for idx, row in significant_sorted.iterrows():
        print(f"\n{idx+1}. ρ = {row['spearman_correlation']:.4f}, p = {row['spearman_p_value']:.4f}")
        print(f"   Вопрос родителя: {row['parent_question']}")
        print(f"   Вопрос о профессии: {row['profession_question']}")
        
        # Интерпретация
        rho_abs = abs(row['spearman_correlation'])
        if rho_abs < 0.2:
            strength = "очень слабая"
        elif rho_abs < 0.4:
            strength = "слабая"
        elif rho_abs < 0.6:
            strength = "умеренная"
        elif rho_abs < 0.8:
            strength = "сильная"
        else:
            strength = "очень сильная"
        
        direction = "положительная" if row['spearman_correlation'] > 0 else "отрицательная"
        print(f"   Характер связи: {direction}, {strength}")

print("\n" + "=" * 80)
print("СТАТИСТИКА:")
print("=" * 80)
print(f"Средняя корреляция (все): {df['spearman_correlation'].mean():.4f}")
print(f"Медианная корреляция (все): {df['spearman_correlation'].median():.4f}")
print(f"Средняя корреляция (значимые): {significant['spearman_correlation'].mean():.4f}")
print(f"Максимальная корреляция: {df['spearman_correlation'].max():.4f}")
print(f"Минимальная корреляция: {df['spearman_correlation'].min():.4f}")

# Анализ по вопросам о профессии
print("\n" + "=" * 80)
print("АНАЛИЗ ПО ВОПРОСАМ О ПРОФЕССИИ:")
print("=" * 80)

prof_questions = df['profession_question'].unique()
for prof_q in prof_questions:
    prof_data = df[df['profession_question'] == prof_q]
    prof_significant = prof_data[prof_data['spearman_p_value'] < 0.05]
    
    print(f"\n{prof_q}:")
    print(f"  Всего корреляций: {len(prof_data)}")
    print(f"  Значимых: {len(prof_significant)}")
    print(f"  Средняя корреляция: {prof_data['spearman_correlation'].mean():.4f}")
    if len(prof_significant) > 0:
        print(f"  Средняя значимая корреляция: {prof_significant['spearman_correlation'].mean():.4f}")


















