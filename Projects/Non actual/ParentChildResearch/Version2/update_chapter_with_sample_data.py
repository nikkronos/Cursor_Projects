"""Обновление Главы II с данными о выборке"""
import pandas as pd
import os
import re

# Пути
script_dir = os.path.dirname(os.path.abspath(__file__))
parents_file = os.path.join(script_dir, '..', 'newtest', 'Опрос для родителей  (Ответы).csv')
students_file = os.path.join(script_dir, '..', 'newtest', 'Опрос ученика (Ответы) Новый.csv')
chapter_file = os.path.join(script_dir, 'ГЛАВА_II.md')

print("Анализ данных выборки...")

# Загружаем данные
parents_df = pd.read_csv(parents_file, encoding='utf-8-sig')
students_df = pd.read_csv(students_file, encoding='utf-8-sig')

# Анализ возраста подростков
if 'Возраст ребенка' in parents_df.columns:
    ages = parents_df['Возраст ребенка'].dropna().astype(int)
    age_min = int(ages.min())
    age_max = int(ages.max())
    age_mean = ages.mean()
    age_median = ages.median()
elif 'Возраст' in students_df.columns:
    ages = students_df['Возраст'].dropna().astype(int)
    age_min = int(ages.min())
    age_max = int(ages.max())
    age_mean = ages.mean()
    age_median = ages.median()
else:
    age_min = age_max = age_mean = age_median = None

# Анализ пола по именам
if 'Фамилия и имя ребенка' in parents_df.columns:
    names = parents_df['Фамилия и имя ребенка'].dropna()
elif 'Фамилия и имя' in students_df.columns:
    names = students_df['Фамилия и имя'].dropna()
else:
    names = pd.Series([])

female_endings = ['а', 'я', 'ия', 'ья', 'на', 'ва', 'ва', 'ова', 'ева']
male_count = 0
female_count = 0

for name in names:
    name_str = str(name).strip()
    if name_str:
        name_parts = name_str.split()
        if name_parts:
            first_name = name_parts[-1].lower()
            if any(first_name.endswith(ending) for ending in female_endings):
                female_count += 1
            else:
                male_count += 1

# Анализ классов
if 'Класс' in students_df.columns:
    classes = students_df['Класс'].dropna()
    class_distribution = classes.value_counts().sort_index()
else:
    class_distribution = None

print(f"\nРезультаты анализа:")
print(f"Возраст: {age_min}-{age_max} лет (средний: {age_mean:.1f})")
print(f"Юноши: {male_count}, Девушки: {female_count}")

# Читаем Главу II
with open(chapter_file, 'r', encoding='utf-8') as f:
    chapter_text = f.read()

# Обновляем раздел 2.1.1
old_sample_text = r'\*\*Характеристика выборки подростков:\*\*\s*- Возраст: учащиеся 9–11-х классов \(подростковый возраст, 14–17 лет\)\s*- Общее количество: 50 человек\s*- Пол: \(требуется уточнение данных о распределении по полу\)'

new_sample_text = f"""**Характеристика выборки подростков:**
- Возраст: учащиеся 9–11-х классов (подростковый возраст, {age_min}–{age_max} лет)
- Средний возраст: {age_mean:.1f} лет
- Общее количество: 50 человек
- Пол: юноши — {male_count} человек ({male_count/50*100:.0f}%), девушки — {female_count} человек ({female_count/50*100:.0f}%)"""

# Заменяем текст
chapter_text = re.sub(
    r'\*\*Характеристика выборки подростков:\*\*.*?Пол: \(требуется уточнение данных о распределении по полу\)',
    new_sample_text,
    chapter_text,
    flags=re.DOTALL
)

# Обновляем раздел о родителях
old_parents_text = r'\*\*Характеристика выборки родителей:\*\*\s*- Общее количество: 50 человек\s*- Пол: \(требуется уточнение данных о распределении по полу\)\s*- Возраст: \(требуется уточнение данных\)'

new_parents_text = """**Характеристика выборки родителей:**
- Общее количество: 50 человек
- Пол: (данные не собирались)
- Возраст: (данные не собирались)"""

chapter_text = re.sub(
    r'\*\*Характеристика выборки родителей:\*\*.*?Возраст: \(требуется уточнение данных\)',
    new_parents_text,
    chapter_text,
    flags=re.DOTALL
)

# Сохраняем обновленный текст
with open(chapter_file, 'w', encoding='utf-8') as f:
    f.write(chapter_text)

print(f"\n✓ Глава II обновлена с данными о выборке")
print(f"  Сохранено в: {chapter_file}")














