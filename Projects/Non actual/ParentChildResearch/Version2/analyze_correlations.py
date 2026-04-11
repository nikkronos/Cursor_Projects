"""Анализ корреляций из файла correlations_analysis.csv"""
import pandas as pd
import os

# Путь к файлу с корреляциями
correlations_file = os.path.join(os.path.dirname(__file__), '..', 'newtest', 'correlations_analysis.csv')

# Загружаем данные
df = pd.read_csv(correlations_file, encoding='utf-8-sig')

# Фильтруем статистически значимые корреляции (p < 0.05)
significant = df[df['spearman_p_value'] < 0.05].copy()

print("="*80)
print("СТАТИСТИЧЕСКИ ЗНАЧИМЫЕ КОРРЕЛЯЦИИ (p < 0.05)")
print("="*80)
print(f"\nВсего значимых корреляций: {len(significant)}")
print(f"Всего корреляций: {len(df)}")
print(f"Процент значимых: {len(significant)/len(df)*100:.1f}%\n")

# Сортируем по абсолютному значению корреляции
significant['abs_correlation'] = significant['spearman_correlation'].abs()
significant = significant.sort_values('abs_correlation', ascending=False)

print("\nДетальная информация о значимых корреляциях:\n")
for idx, row in significant.iterrows():
    print(f"{'='*80}")
    print(f"Корреляция #{idx}")
    print(f"Вопрос родителя: {row['parent_question']}")
    print(f"Вопрос о профессии: {row['profession_question']}")
    print(f"Коэффициент Спирмена: ρ = {row['spearman_correlation']:.4f}")
    print(f"Уровень значимости: p = {row['spearman_p_value']:.4f}")
    print(f"Количество пар: n = {int(row['n_pairs'])}")
    
    # Интерпретация силы связи
    abs_rho = abs(row['spearman_correlation'])
    if abs_rho < 0.2:
        strength = "очень слабая"
    elif abs_rho < 0.4:
        strength = "слабая"
    elif abs_rho < 0.6:
        strength = "умеренная"
    elif abs_rho < 0.8:
        strength = "сильная"
    else:
        strength = "очень сильная"
    
    direction = "положительная" if row['spearman_correlation'] > 0 else "отрицательная"
    print(f"Характер связи: {direction} {strength} связь")
    print()

# Общая статистика
print("\n" + "="*80)
print("ОБЩАЯ СТАТИСТИКА")
print("="*80)
print(f"Средняя корреляция: {df['spearman_correlation'].mean():.4f}")
print(f"Медианная корреляция: {df['spearman_correlation'].median():.4f}")
print(f"Минимальная корреляция: {df['spearman_correlation'].min():.4f}")
print(f"Максимальная корреляция: {df['spearman_correlation'].max():.4f}")
print(f"Стандартное отклонение: {df['spearman_correlation'].std():.4f}")

# Сохраняем значимые корреляции
output_file = os.path.join(os.path.dirname(__file__), 'significant_correlations.csv')
significant[['parent_question', 'profession_question', 'spearman_correlation', 'spearman_p_value', 'n_pairs']].to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\nЗначимые корреляции сохранены в: {output_file}")














