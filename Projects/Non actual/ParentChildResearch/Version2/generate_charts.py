"""Генерация графиков и диаграмм для Главы II"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# Пытаемся импортировать seaborn, если нет - продолжаем без него
try:
    import seaborn as sns
    sns_available = True
except ImportError:
    sns_available = False
    print("Предупреждение: seaborn не установлен, тепловая карта не будет создана")

# Настройка для русского языка
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

# Определяем путь к скрипту
if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(sys.executable)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))

# Создаем папку для графиков
charts_dir = os.path.join(script_dir, 'charts')
os.makedirs(charts_dir, exist_ok=True)

# Загружаем данные
correlations_file = os.path.join(script_dir, '..', 'newtest', 'correlations_analysis.csv')
df = pd.read_csv(correlations_file, encoding='utf-8-sig')

# Фильтруем значимые корреляции
significant = df[df['spearman_p_value'] < 0.05].copy()

print("Генерация графиков...")

# 1. Гистограмма распределения корреляций
plt.figure(figsize=(10, 6))
plt.hist(df['spearman_correlation'], bins=30, edgecolor='black', alpha=0.7)
plt.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Нулевая корреляция')
plt.xlabel('Коэффициент корреляции Спирмена', fontsize=12)
plt.ylabel('Частота', fontsize=12)
plt.title('Распределение коэффициентов корреляции Спирмена', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(charts_dir, '1_histogram_correlations.png'), bbox_inches='tight')
plt.close()
print("✓ График 1: Гистограмма распределения корреляций")

# 2. Топ-10 самых сильных корреляций
# Создаем временную колонку с абсолютными значениями
df['abs_correlation'] = df['spearman_correlation'].abs()
top10 = df.nlargest(10, 'abs_correlation')
plt.figure(figsize=(12, 8))
colors = ['red' if p < 0.05 else 'blue' for p in top10['spearman_p_value']]
bars = plt.barh(range(len(top10)), top10['spearman_correlation'], color=colors, alpha=0.7)
plt.yticks(range(len(top10)), [f"{row['parent_question'][:50]}..." for _, row in top10.iterrows()], fontsize=8)
plt.xlabel('Коэффициент корреляции Спирмена', fontsize=12)
plt.title('Топ-10 самых сильных корреляций', fontsize=14, fontweight='bold')
plt.axvline(x=0, color='black', linestyle='-', linewidth=1)
plt.grid(True, alpha=0.3, axis='x')
plt.legend([plt.Rectangle((0,0),1,1, color='red', alpha=0.7), 
            plt.Rectangle((0,0),1,1, color='blue', alpha=0.7)], 
           ['Значимые (p<0.05)', 'Незначимые'], loc='lower right')
plt.tight_layout()
plt.savefig(os.path.join(charts_dir, '2_top10_correlations.png'), bbox_inches='tight')
plt.close()
print("✓ График 2: Топ-10 самых сильных корреляций")

# Удаляем временную колонку после использования
df = df.drop('abs_correlation', axis=1)

# 3. Статистически значимые корреляции
if len(significant) > 0:
    plt.figure(figsize=(12, 8))
    significant_sorted = significant.sort_values('spearman_correlation')
    colors_bar = ['green' if r > 0 else 'red' for r in significant_sorted['spearman_correlation']]
    bars = plt.barh(range(len(significant_sorted)), significant_sorted['spearman_correlation'], 
                    color=colors_bar, alpha=0.7)
    
    # Добавляем значения на столбцы
    for i, (idx, row) in enumerate(significant_sorted.iterrows()):
        plt.text(row['spearman_correlation'], i, f" {row['spearman_correlation']:.3f} (p={row['spearman_p_value']:.3f})", 
                va='center', fontsize=9)
    
    plt.yticks(range(len(significant_sorted)), 
               [f"{row['parent_question'][:60]}..." for _, row in significant_sorted.iterrows()], 
               fontsize=9)
    plt.xlabel('Коэффициент корреляции Спирмена', fontsize=12)
    plt.title('Статистически значимые корреляции (p < 0.05)', fontsize=14, fontweight='bold')
    plt.axvline(x=0, color='black', linestyle='-', linewidth=1)
    plt.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, '3_significant_correlations.png'), bbox_inches='tight')
    plt.close()
    print("✓ График 3: Статистически значимые корреляции")

# 4. Сравнение по двум вопросам о профессии
q12 = df[df['profession_question'].str.contains('12', na=False)]
q19 = df[df['profession_question'].str.contains('19', na=False)]

# Берем первые 20 для сравнения
q12_top20 = q12['spearman_correlation'].head(20).values
q19_top20 = q19['spearman_correlation'].head(20).values

plt.figure(figsize=(12, 6))
x = np.arange(len(q12_top20))  # Используем длину выбранных данных
width = 0.35

plt.bar(x - width/2, q12_top20, width, label='Вопрос 12 (рост мастерства)', alpha=0.7)
plt.bar(x + width/2, q19_top20, width, label='Вопрос 19 (умения вне работы)', alpha=0.7)

plt.xlabel('Порядковый номер корреляции', fontsize=12)
plt.ylabel('Коэффициент корреляции Спирмена', fontsize=12)
plt.title('Сравнение корреляций по двум вопросам о профессии (первые 20)', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(os.path.join(charts_dir, '4_comparison_prof_questions.png'), bbox_inches='tight')
plt.close()
print("✓ График 4: Сравнение по двум вопросам о профессии")

# 5. Тепловая карта значимых корреляций (если достаточно данных и seaborn доступен)
if len(significant) >= 3 and sns_available:
    try:
        # Создаем матрицу для тепловой карты
        pivot_data = significant.pivot_table(
            values='spearman_correlation',
            index='parent_question',
            columns='profession_question',
            aggfunc='first'
        )
        
        if pivot_data.shape[0] > 0 and pivot_data.shape[1] > 0:
            plt.figure(figsize=(10, max(8, pivot_data.shape[0] * 0.5)))
            sns.heatmap(pivot_data, annot=True, fmt='.3f', cmap='RdYlBu_r', center=0,
                       cbar_kws={'label': 'Коэффициент корреляции Спирмена'}, 
                       xticklabels=[col[:30] + '...' if len(str(col)) > 30 else col for col in pivot_data.columns],
                       yticklabels=[idx[:40] + '...' if len(str(idx)) > 40 else idx for idx in pivot_data.index],
                       annot_kws={'size': 8})  # Используем annot_kws вместо fontsize
            plt.title('Тепловая карта статистически значимых корреляций', fontsize=14, fontweight='bold')
            plt.tight_layout()
            plt.savefig(os.path.join(charts_dir, '5_heatmap_significant.png'), bbox_inches='tight')
            plt.close()
            print("✓ График 5: Тепловая карта значимых корреляций")
    except Exception as e:
        print(f"⚠ График 5: Не удалось создать тепловую карту: {e}")

# 6. Распределение по уровням значимости
df['significance_level'] = pd.cut(df['spearman_p_value'], 
                                  bins=[0, 0.001, 0.01, 0.05, 0.10, 1.0],
                                  labels=['***', '**', '*', 'тенденция', 'незначимо'])

plt.figure(figsize=(10, 6))
counts = df['significance_level'].value_counts().sort_index()
colors_map = {'***': 'darkgreen', '**': 'green', '*': 'lightgreen', 
              'тенденция': 'yellow', 'незначимо': 'lightgray'}
colors = [colors_map.get(label, 'gray') for label in counts.index]
bars = plt.bar(counts.index, counts.values, color=colors, alpha=0.7, edgecolor='black')
plt.xlabel('Уровень значимости', fontsize=12)
plt.ylabel('Количество корреляций', fontsize=12)
plt.title('Распределение корреляций по уровням статистической значимости', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3, axis='y')

# Добавляем значения на столбцы
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(charts_dir, '6_significance_levels.png'), bbox_inches='tight')
plt.close()
print("✓ График 6: Распределение по уровням значимости")

print(f"\n✓ Все графики сохранены в папку: {charts_dir}")

