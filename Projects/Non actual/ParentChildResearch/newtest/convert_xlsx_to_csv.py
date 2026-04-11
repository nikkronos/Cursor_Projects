"""Скрипт для конвертации XLSX файлов в CSV"""
import os
import pandas as pd

# Определяем путь к папке со скриптом
script_dir = os.path.dirname(os.path.abspath(__file__))

# Файлы для конвертации
files = [
    {
        'xlsx': os.path.join(script_dir, "Опрос для родителей  (Ответы).xlsx"),
        'csv': os.path.join(script_dir, "Опрос для родителей  (Ответы).csv")
    },
    {
        'xlsx': os.path.join(script_dir, "Опрос ученика (Ответы) Новый.xlsx"),
        'csv': os.path.join(script_dir, "Опрос ученика (Ответы) Новый.csv")
    }
]

print("Начало конвертации XLSX файлов в CSV...")
print(f"Рабочая директория: {script_dir}\n")

for file_info in files:
    xlsx_path = file_info['xlsx']
    csv_path = file_info['csv']
    
    xlsx_name = os.path.basename(xlsx_path)
    csv_name = os.path.basename(csv_path)
    
    if not os.path.exists(xlsx_path):
        print(f"  ✗ Файл не найден: {xlsx_name}")
        continue
    
    try:
        print(f"Обработка файла: {xlsx_name}")
        
        # Читаем XLSX файл
        df = pd.read_excel(xlsx_path, engine='openpyxl')
        
        print(f"  Загружено строк: {len(df)}")
        print(f"  Загружено столбцов: {len(df.columns)}")
        
        # Сохраняем в CSV с кодировкой utf-8-sig (для корректного отображения в Excel)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        print(f"  ✓ Файл сохранен: {csv_name}")
        
    except Exception as e:
        print(f"  ✗ Ошибка при обработке {xlsx_name}: {e}")
        import traceback
        traceback.print_exc()

print("\nКонвертация завершена!")





























