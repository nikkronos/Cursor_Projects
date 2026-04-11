"""Генерация графиков и диаграмм для Главы II ВКР"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams

# Настройка для русского языка
rcParams['font.family'] = 'Times New Roman'
rcParams['font.size'] = 12
plt.rcParams['axes.unicode_minus'] = False

# Определяем пути
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
correlations_file = os.path.join(parent_dir, "newtest", "correlations_analysis.csv")
output_dir = os.path.join(script_dir, "charts")

# Создаем папку для графиков
os.makedirs(output_dir, exist_ok=True)

print("Загрузка данных корреляций...")
df = pd.read_csv(correlations_file, encoding='utf-8-sig')

# Удаляем пустые строки
df = df.dropna(subset=['spearman_correlation', 'spearman_p_value'])

print(f"Загружено {len(df)} корреляций")

# Фильтруем значимые корреляции
significant = df[df['spearman_p_value'] < 0.05].copy()
print(f"Найдено {len(significant)} статистически значимых корреляций (p < 0.05)")

# 1. ГИСТОГРАММА РАСПРЕДЕЛЕНИЯ КОРРЕЛЯЦИЙ
print("\n1. Создание гистограммы распределения корреляций...")
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(df['spearman_correlation'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Нулевая корреляция')
ax.set_xlabel('Коэффициент корреляции Спирмена (ρ)', fontsize=12)
ax.set_ylabel('Частота', fontsize=12)
ax.set_title('Распределение коэффициентов корреляции между установками родителей\nи профессиональным выбором подростков', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '1_histogram_correlations.png'), dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Сохранено: 1_histogram_correlations.png")

# 2. ТОП-10 САМЫХ СИЛЬНЫХ КОРРЕЛЯЦИЙ (по абсолютному значению)
print("\n2. Создание диаграммы топ-10 корреляций...")
top_10 = df.nlargest(10, 'spearman_correlation', keep='all')
# Берем топ-10 по абсолютному значению
df['abs_corr'] = df['spearman_correlation'].abs()
top_10_abs = df.nlargest(10, 'abs_corr')

fig, ax = plt.subplots(figsize=(12, 8))
y_pos = np.arange(len(top_10_abs))
colors = ['green' if p < 0.05 else 'orange' for p in top_10_abs['spearman_p_value']]

bars = ax.barh(y_pos, top_10_abs['spearman_correlation'], color=colors, alpha=0.7, edgecolor='black')

# Сокращаем названия вопросов для читаемости
labels = []
for idx, row in top_10_abs.iterrows():
    parent_q = str(row['parent_question'])[:60] + "..." if len(str(row['parent_question'])) > 60 else str(row['parent_question'])
    prof_q = str(row['profession_question'])
    label = f"{parent_q}\n→ {prof_q}"
    labels.append(label)

ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=9)
ax.set_xlabel('Коэффициент корреляции Спирмена (ρ)', fontsize=12)
ax.set_title('Топ-10 самых сильных корреляций\n(зеленый = значимо при p<0.05, оранжевый = незначимо)', fontsize=13, fontweight='bold')
ax.axvline(x=0, color='red', linestyle='--', linewidth=1)
ax.grid(True, alpha=0.3, axis='x')

# Добавляем значения на столбцы
for i, (bar, val, p_val) in enumerate(zip(bars, top_10_abs['spearman_correlation'], top_10_abs['spearman_p_value'])):
    sign = '*' if p_val < 0.05 else ''
    ax.text(val + 0.01 if val > 0 else val - 0.01, i, f'{val:.3f}{sign}', 
            va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, '2_top10_correlations.png'), dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Сохранено: 2_top10_correlations.png")

# 3. СТАТИСТИЧЕСКИ ЗНАЧИМЫЕ КОРРЕЛЯЦИИ
print("\n3. Создание диаграммы значимых корреляций...")
if len(significant) > 0:
    fig, ax = plt.subplots(figsize=(12, max(6, len(significant) * 0.6)))
    
    # Сортируем по силе корреляции
    significant_sorted = significant.sort_values('spearman_correlation')
    
    y_pos = np.arange(len(significant_sorted))
    colors = ['green' if c > 0 else 'red' for c in significant_sorted['spearman_correlation']]
    
    bars = ax.barh(y_pos, significant_sorted['spearman_correlation'], color=colors, alpha=0.7, edgecolor='black')
    
    labels = []
    for idx, row in significant_sorted.iterrows():
        parent_q = str(row['parent_question'])[:50] + "..." if len(str(row['parent_question'])) > 50 else str(row['parent_question'])
        prof_q = str(row['profession_question'])
        label = f"{parent_q}\n→ {prof_q}"
        labels.append(label)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel('Коэффициент корреляции Спирмена (ρ)', fontsize=12)
    ax.set_title(f'Статистически значимые корреляции (p < 0.05, n={len(significant)})\n(зеленый = положительная, красный = отрицательная)', 
                 fontsize=13, fontweight='bold')
    ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
    ax.grid(True, alpha=0.3, axis='x')
    
    # Добавляем значения
    for i, (bar, val, p_val) in enumerate(zip(bars, significant_sorted['spearman_correlation'], significant_sorted['spearman_p_value'])):
        ax.text(val + 0.01 if val > 0 else val - 0.01, i, f'{val:.3f} (p={p_val:.3f})', 
                va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '3_significant_correlations.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Сохранено: 3_significant_correlations.png")
else:
    print("   ⚠ Значимых корреляций не найдено")

# 4. СРАВНЕНИЕ КОРРЕЛЯЦИЙ ПО ДВУМ ВОПРОСАМ О ПРОФЕССИИ
print("\n4. Создание сравнения корреляций по вопросам о профессии...")
prof_q1 = df[df['profession_question'] == '12. Дает возможности для роста профессионального мастерства']
prof_q2 = df[df['profession_question'] == '19. Позволяет использовать профессиональные умения вне работы']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Вопрос 1
ax1.hist(prof_q1['spearman_correlation'], bins=20, color='steelblue', edgecolor='black', alpha=0.7)
ax1.axvline(x=0, color='red', linestyle='--', linewidth=2)
ax1.set_xlabel('Коэффициент корреляции (ρ)', fontsize=11)
ax1.set_ylabel('Частота', fontsize=11)
ax1.set_title('Вопрос 12: Рост профессионального\nмастерства', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)
mean1 = prof_q1['spearman_correlation'].mean()
ax1.axvline(x=mean1, color='green', linestyle='--', linewidth=2, label=f'Среднее: {mean1:.3f}')
ax1.legend(fontsize=9)

# Вопрос 2
ax2.hist(prof_q2['spearman_correlation'], bins=20, color='coral', edgecolor='black', alpha=0.7)
ax2.axvline(x=0, color='red', linestyle='--', linewidth=2)
ax2.set_xlabel('Коэффициент корреляции (ρ)', fontsize=11)
ax2.set_ylabel('Частота', fontsize=11)
ax2.set_title('Вопрос 19: Использование умений\nвне работы', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)
mean2 = prof_q2['spearman_correlation'].mean()
ax2.axvline(x=mean2, color='green', linestyle='--', linewidth=2, label=f'Среднее: {mean2:.3f}')
ax2.legend(fontsize=9)

plt.suptitle('Распределение корреляций по двум вопросам о профессиональных предпочтениях', 
             fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '4_comparison_prof_questions.png'), dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Сохранено: 4_comparison_prof_questions.png")

# 5. ТЕПЛОВАЯ КАРТА ЗНАЧИМЫХ КОРРЕЛЯЦИЙ (если есть достаточно данных)
print("\n5. Создание тепловой карты...")
if len(significant) >= 3:
    # Создаем матрицу для тепловой карты
    # Берем топ-15 вопросов родителей с наибольшим количеством значимых корреляций
    parent_counts = significant['parent_question'].value_counts()
    top_parents = parent_counts.head(15).index.tolist()
    
    # Создаем матрицу
    matrix_data = []
    matrix_labels = []
    
    for parent_q in top_parents:
        row_data = []
        for prof_q in significant['profession_question'].unique():
            corr_data = significant[(significant['parent_question'] == parent_q) & 
                                   (significant['profession_question'] == prof_q)]
            if len(corr_data) > 0:
                row_data.append(corr_data.iloc[0]['spearman_correlation'])
            else:
                row_data.append(0)
        matrix_data.append(row_data)
        # Сокращаем название вопроса
        short_name = str(parent_q)[:40] + "..." if len(str(parent_q)) > 40 else str(parent_q)
        matrix_labels.append(short_name)
    
    matrix = np.array(matrix_data)
    
    fig, ax = plt.subplots(figsize=(10, max(8, len(top_parents) * 0.5)))
    sns.heatmap(matrix, annot=True, fmt='.2f', cmap='RdYlGn', center=0, 
                vmin=-0.5, vmax=0.5, cbar_kws={'label': 'Коэффициент корреляции'},
                yticklabels=matrix_labels, xticklabels=significant['profession_question'].unique(),
                ax=ax, linewidths=0.5, linecolor='gray')
    ax.set_title('Тепловая карта значимых корреляций\n(топ-15 вопросов родителей)', 
                 fontsize=13, fontweight='bold', pad=20)
    ax.set_xlabel('Вопросы о профессиональных предпочтениях', fontsize=11)
    ax.set_ylabel('Вопросы родителей', fontsize=11)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '5_heatmap_significant.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Сохранено: 5_heatmap_significant.png")
else:
    print("   ⚠ Недостаточно данных для тепловой карты")

# 6. СТАТИСТИКА ПО УРОВНЯМ ЗНАЧИМОСТИ
print("\n6. Создание диаграммы статистики по уровням значимости...")
df['significance_level'] = 'Незначимо'
df.loc[df['spearman_p_value'] < 0.05, 'significance_level'] = 'p < 0.05'
df.loc[df['spearman_p_value'] < 0.01, 'significance_level'] = 'p < 0.01'
df.loc[df['spearman_p_value'] < 0.001, 'significance_level'] = 'p < 0.001'

counts = df['significance_level'].value_counts()
colors_map = {'p < 0.001': 'darkgreen', 'p < 0.01': 'green', 'p < 0.05': 'lightgreen', 'Незначимо': 'gray'}

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(counts.index, counts.values, color=[colors_map.get(x, 'gray') for x in counts.index], 
              edgecolor='black', alpha=0.7)
ax.set_ylabel('Количество корреляций', fontsize=12)
ax.set_xlabel('Уровень статистической значимости', fontsize=12)
ax.set_title('Распределение корреляций по уровням статистической значимости', 
             fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Добавляем значения на столбцы
for bar, val in zip(bars, counts.values):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{val}\n({val/len(df)*100:.1f}%)',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, '6_significance_levels.png'), dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ Сохранено: 6_significance_levels.png")

print(f"\n✓ Все графики сохранены в папку: {output_dir}")
print(f"  Всего создано графиков: 6")


















