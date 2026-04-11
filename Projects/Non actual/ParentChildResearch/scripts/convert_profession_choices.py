"""
Скрипт для преобразования текстовых ответов "Что тебе ближе?" в числовые значения (1 или 2)
"""
import pandas as pd
import os
import sys

# Добавляем путь к скриптам для импорта
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)

from profession_mapping import PROFESSION_MAPPING

try:
    from fuzzywuzzy import fuzz
except ImportError:
    # Если fuzzywuzzy не установлен, используем простое сравнение
    class SimpleFuzz:
        @staticmethod
        def ratio(a, b):
            if a == b:
                return 100
            # Простое сравнение по подстроке
            if a in b or b in a:
                return 80
            return 0
    fuzz = SimpleFuzz()

def normalize_text(text):
    """Нормализация текста для сравнения"""
    if pd.isna(text):
        return ""
    # Удаляем все невидимые символы и нормализуем пробелы
    text = str(text).strip().lower()
    # Удаляем мягкие переносы и другие невидимые символы
    text = text.replace('\u00ad', '')  # Мягкий перенос
    text = text.replace('\u200b', '')  # Zero-width space
    text = text.replace('\u200c', '')  # Zero-width non-joiner
    text = text.replace('\u200d', '')  # Zero-width joiner
    # Нормализуем пробелы
    text = ' '.join(text.split())
    return text

def find_choice(text, question_num):
    """
    Определяет, какой вариант выбран (1 или 2) на основе текста ответа
    """
    if pd.isna(text) or text == "":
        return None
    
    text_normalized = normalize_text(text)
    option1, option2 = PROFESSION_MAPPING[question_num]
    option1_normalized = normalize_text(option1)
    option2_normalized = normalize_text(option2)
    
    # Точное совпадение
    if text_normalized == option1_normalized:
        return 1
    if text_normalized == option2_normalized:
        return 2
    
    # Fuzzy matching для случаев с небольшими различиями
    ratio1 = fuzz.ratio(text_normalized, option1_normalized)
    ratio2 = fuzz.ratio(text_normalized, option2_normalized)
    
    if ratio1 > ratio2 and ratio1 > 80:
        return 1
    elif ratio2 > ratio1 and ratio2 > 80:
        return 2
    
    # Если не удалось определить, возвращаем None
    return None

def convert_profession_choices(input_file, output_file):
    """
    Преобразует текстовые ответы в числовые значения
    """
    print(f"Загрузка файла: {input_file}")
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    
    # Колонки с вопросами "Что тебе ближе?" начинаются с индекса 64 (колонка 65 в CSV)
    # Это колонки с 65 по 106 (42 вопроса)
    start_col_idx = 64  # Индекс первой колонки с вопросами "Что тебе ближе?"
    
    # Находим названия колонок
    columns = df.columns.tolist()
    
    # Преобразуем каждую колонку с вопросами "Что тебе ближе?"
    converted_count = 0
    failed_count = 0
    
    for i in range(1, 43):  # Вопросы с 1 по 42
        col_idx = start_col_idx + i - 1
        if col_idx < len(columns):
            col_name = columns[col_idx]
            print(f"Обработка вопроса {i} (колонка {col_name})...")
            
            # Преобразуем значения
            for idx in df.index:
                original_value = df.at[idx, col_name]
                choice = find_choice(original_value, i)
                
                if choice is not None:
                    df.at[idx, col_name] = choice
                    converted_count += 1
                else:
                    # Попробуем еще раз с улучшенной нормализацией
                    # Если это вопрос 26 и текст содержит "трейдер" и "биржевой", это вариант 2
                    if i == 26 and pd.notna(original_value):
                        text_lower = normalize_text(original_value)
                        if 'трейдер' in text_lower and 'биржевой' in text_lower:
                            df.at[idx, col_name] = 2
                            converted_count += 1
                            continue
                        elif 'преподаватель' in text_lower:
                            df.at[idx, col_name] = 1
                            converted_count += 1
                            continue
                    
                    failed_count += 1
                    print(f"  Предупреждение: не удалось определить выбор для строки {idx+2}, вопрос {i}")
                    print(f"    Текст: {original_value}")
    
    # Сохраняем результат
    print(f"\nСохранение результата в: {output_file}")
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\nПреобразование завершено:")
    print(f"  Успешно преобразовано: {converted_count}")
    print(f"  Не удалось преобразовать: {failed_count}")
    
    return df

if __name__ == "__main__":
    # base_dir уже определен выше
    project_root = os.path.join(base_dir, '..')
    
    # Пути к файлам
    input_file = os.path.join(project_root, 'data', 'raw', 'students_survey.csv')
    output_file = os.path.join(project_root, 'data', 'raw', 'students_survey_converted.csv')
    
    # Проверяем существование входного файла
    if not os.path.exists(input_file):
        print(f"Ошибка: файл {input_file} не найден")
        print("Сначала скопируйте исходные CSV файлы в data/raw/")
        exit(1)
    
    # Преобразуем
    convert_profession_choices(input_file, output_file)

