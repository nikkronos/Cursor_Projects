"""Скрипт для копирования исходных CSV файлов в проект с использованием pandas"""
import pandas as pd
import os

# Определяем пути
base_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(base_dir, '..')
raw_data_dir = os.path.join(project_root, 'data', 'raw')

# Создаем директорию, если её нет
os.makedirs(raw_data_dir, exist_ok=True)

# Пути к исходным файлам
source_parents = r'c:\Users\krono\OneDrive\Рабочий стол\Опрос для родителей .csv'
source_students = r'c:\Users\krono\OneDrive\Рабочий стол\Опрос ученика.csv'

# Пути назначения
dest_parents = os.path.join(raw_data_dir, 'parents_survey.csv')
dest_students = os.path.join(raw_data_dir, 'students_survey.csv')

# Копируем файлы через pandas для корректной обработки кодировки
try:
    df_parents = pd.read_csv(source_parents, encoding='utf-8-sig')
    df_parents.to_csv(dest_parents, index=False, encoding='utf-8-sig')
    print(f"Скопирован файл родителей: {dest_parents}")
    print(f"  Строк: {len(df_parents)}")
except Exception as e:
    print(f"Ошибка при копировании файла родителей: {e}")

try:
    df_students = pd.read_csv(source_students, encoding='utf-8-sig')
    df_students.to_csv(dest_students, index=False, encoding='utf-8-sig')
    print(f"Скопирован файл учеников: {dest_students}")
    print(f"  Строк: {len(df_students)}")
except Exception as e:
    print(f"Ошибка при копировании файла учеников: {e}")

print("Копирование завершено")








