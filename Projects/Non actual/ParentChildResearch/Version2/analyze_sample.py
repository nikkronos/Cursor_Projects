"""Анализ данных выборки для получения статистики по полу и возрасту"""
import pandas as pd
import os

# Пути к файлам
script_dir = os.path.dirname(os.path.abspath(__file__))
parents_file = os.path.join(script_dir, '..', 'newtest', 'Опрос для родителей  (Ответы).csv')
students_file = os.path.join(script_dir, '..', 'newtest', 'Опрос ученика (Ответы) Новый.csv')

print("Анализ данных выборки...")

# Загружаем данные родителей
parents_df = pd.read_csv(parents_file, encoding='utf-8-sig')
print(f"\nДанные родителей: {len(parents_df)} записей")
print("Колонки:", list(parents_df.columns[:10]))

# Загружаем данные учеников
students_df = pd.read_csv(students_file, encoding='utf-8-sig')
print(f"\nДанные учеников: {len(students_df)} записей")
print("Колонки:", list(students_df.columns[:10]))

# Анализ возраста подростков
if 'Возраст ребенка' in parents_df.columns:
    ages = parents_df['Возраст ребенка'].dropna()
    print(f"\n=== ВОЗРАСТ ПОДРОСТКОВ ===")
    print(f"Количество: {len(ages)}")
    print(f"Минимальный возраст: {ages.min()}")
    print(f"Максимальный возраст: {ages.max()}")
    print(f"Средний возраст: {ages.mean():.1f}")
    print(f"Медианный возраст: {ages.median():.1f}")
    print(f"\nРаспределение по возрастам:")
    print(ages.value_counts().sort_index())
elif 'Возраст' in students_df.columns:
    ages = students_df['Возраст'].dropna()
    print(f"\n=== ВОЗРАСТ ПОДРОСТКОВ ===")
    print(f"Количество: {len(ages)}")
    print(f"Минимальный возраст: {ages.min()}")
    print(f"Максимальный возраст: {ages.max()}")
    print(f"Средний возраст: {ages.mean():.1f}")
    print(f"Медианный возраст: {ages.median():.1f}")
    print(f"\nРаспределение по возрастам:")
    print(ages.value_counts().sort_index())

# Анализ пола подростков (по именам или другим признакам)
print(f"\n=== ПОЛ ПОДРОСТКОВ ===")
# Пытаемся определить пол по именам
if 'Фамилия и имя ребенка' in parents_df.columns:
    names = parents_df['Фамилия и имя ребенка'].dropna()
elif 'Фамилия и имя' in students_df.columns:
    names = students_df['Фамилия и имя'].dropna()
else:
    names = pd.Series([])

# Простой анализ по окончаниям имен (не очень точный, но лучше чем ничего)
if len(names) > 0:
    # Типичные окончания женских имен в русском языке
    female_endings = ['а', 'я', 'ия', 'ья']
    male_count = 0
    female_count = 0
    unknown_count = 0
    
    for name in names:
        name_str = str(name).strip()
        if name_str:
            # Берем последнее слово (имя)
            name_parts = name_str.split()
            if name_parts:
                first_name = name_parts[-1].lower()
                if any(first_name.endswith(ending) for ending in female_endings):
                    female_count += 1
                elif first_name:
                    male_count += 1
                else:
                    unknown_count += 1
    
    print(f"Юноши (предположительно): {male_count}")
    print(f"Девушки (предположительно): {female_count}")
    print(f"Не определено: {unknown_count}")
    print(f"Всего: {len(names)}")

# Анализ класса
if 'Класс' in students_df.columns:
    classes = students_df['Класс'].dropna()
    print(f"\n=== КЛАССЫ ===")
    print(f"Распределение по классам:")
    print(classes.value_counts().sort_index())

# Сохраняем результаты
results = {
    'total_pairs': len(parents_df),
    'ages': ages.tolist() if 'ages' in locals() else [],
    'male_count': male_count if 'male_count' in locals() else 0,
    'female_count': female_count if 'female_count' in locals() else 0,
}

output_file = os.path.join(script_dir, 'sample_statistics.txt')
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("СТАТИСТИКА ВЫБОРКИ\n")
    f.write("="*50 + "\n\n")
    f.write(f"Общее количество пар: {results['total_pairs']}\n\n")
    if results['ages']:
        f.write(f"Возраст подростков: {min(results['ages'])}-{max(results['ages'])} лет\n")
        f.write(f"Средний возраст: {sum(results['ages'])/len(results['ages']):.1f} лет\n\n")
    f.write(f"Юноши: {results['male_count']}\n")
    f.write(f"Девушки: {results['female_count']}\n")

print(f"\n✓ Результаты сохранены в: {output_file}")














