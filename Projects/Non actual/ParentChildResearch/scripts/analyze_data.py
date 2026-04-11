"""
Скрипт для анализа данных: сопоставление пар родитель-ребенок и расчет корреляций
"""
import pandas as pd
import os
from scipy.stats import pearsonr
import numpy as np

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

def normalize_name(name):
    """Нормализация имени для сравнения"""
    if pd.isna(name):
        return ""
    return str(name).strip().lower()

def match_names(name1, name2):
    """Сопоставление имен с использованием fuzzy matching"""
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    
    if n1 == n2:
        return 2  # Точное совпадение
    
    # Проверяем частичное совпадение (фамилия)
    parts1 = n1.split()
    parts2 = n2.split()
    
    if len(parts1) > 0 and len(parts2) > 0:
        if parts1[0] == parts2[0]:  # Фамилия совпадает
            return 1
    
    # Fuzzy matching
    ratio = fuzz.ratio(n1, n2)
    if ratio > 80:
        return 1
    
    return 0

def load_data(parents_file, students_file):
    """Загрузка данных из CSV файлов"""
    print(f"Загрузка данных родителей из: {parents_file}")
    parents_df = pd.read_csv(parents_file, encoding='utf-8-sig')
    print(f"  Загружено строк: {len(parents_df)}")
    
    print(f"Загрузка данных учеников из: {students_file}")
    students_df = pd.read_csv(students_file, encoding='utf-8-sig')
    print(f"  Загружено строк: {len(students_df)}")
    
    return parents_df, students_df

def match_pairs(parents_df, students_df):
    """Сопоставление пар родитель-ребенок"""
    print("\nСопоставление пар родитель-ребенок...")
    
    pairs = []
    
    # Колонки с именами
    parent_name_col = "Фамилия, имя родителя "
    child_name_col_parent = "  Фамилия и имя ребенка  "
    student_name_col = "Фамилия и имя "
    
    for p_idx, parent_row in parents_df.iterrows():
        parent_name = parent_row[parent_name_col]
        child_name_from_parent = parent_row[child_name_col_parent]
        
        best_match = None
        best_score = 0
        
        for s_idx, student_row in students_df.iterrows():
            student_name = student_row[student_name_col]
            
            # Сравниваем имя ребенка из опроса родителей с именем ученика
            score = match_names(child_name_from_parent, student_name)
            
            if score > best_score:
                best_score = score
                best_match = (s_idx, student_name, score)
        
        if best_match and best_score > 0:
            pairs.append({
                'parent_index': p_idx,
                'student_index': best_match[0],
                'parent_name': parent_name,
                'child_name': child_name_from_parent,
                'student_name': best_match[1],
                'match_score': best_match[2]
            })
            print(f"  Найдена пара: {parent_name} / {best_match[1]} (score: {best_match[2]})")
    
    pairs_df = pd.DataFrame(pairs)
    print(f"\nВсего найдено пар: {len(pairs_df)}")
    
    return pairs_df

def calculate_correlations(parents_df, students_df, pairs_df):
    """Расчет корреляций между ответами родителей и детей"""
    print("\nРасчет корреляций...")
    
    # Колонки с ответами (вопросы 1-60)
    # У родителей: колонки с индексами 5-64 (вопросы 1-60)
    # У детей: колонки с индексами 4-63 (вопросы 1-60)
    
    parent_start_col = 5  # Первый вопрос у родителей
    parent_end_col = 65   # После последнего вопроса
    student_start_col = 4  # Первый вопрос у учеников
    student_end_col = 64   # После последнего вопроса
    
    correlations = []
    
    for pair_idx, pair in pairs_df.iterrows():
        parent_idx = pair['parent_index']
        student_idx = pair['student_index']
        
        # Получаем ответы родителей и детей
        parent_answers = parents_df.iloc[parent_idx, parent_start_col:parent_end_col].values
        student_answers = students_df.iloc[student_idx, student_start_col:student_end_col].values
        
        # Преобразуем в числовые значения
        parent_answers = pd.to_numeric(parent_answers, errors='coerce')
        student_answers = pd.to_numeric(student_answers, errors='coerce')
        
        # Удаляем NaN значения
        mask = ~(np.isnan(parent_answers) | np.isnan(student_answers))
        parent_clean = parent_answers[mask]
        student_clean = student_answers[mask]
        
        if len(parent_clean) > 1:
            try:
                correlation, p_value = pearsonr(parent_clean, student_clean)
                valid_answers = len(parent_clean)
                
                correlations.append({
                    'pair_id': pair_idx,
                    'parent_name': pair['parent_name'],
                    'child_name': pair['child_name'],
                    'correlation': correlation,
                    'p_value': p_value,
                    'valid_answers': valid_answers
                })
            except Exception as e:
                print(f"  Ошибка при расчете корреляции для пары {pair['parent_name']}: {e}")
    
    correlations_df = pd.DataFrame(correlations)
    print(f"  Рассчитано корреляций: {len(correlations_df)}")
    
    return correlations_df

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(base_dir, '..')
    
    # Пути к файлам
    parents_file = os.path.join(project_root, 'data', 'raw', 'parents_survey.csv')
    
    # Используем преобразованный файл, если он существует, иначе исходный
    students_converted = os.path.join(project_root, 'data', 'raw', 'students_survey_converted.csv')
    students_original = os.path.join(project_root, 'data', 'raw', 'students_survey.csv')
    
    if os.path.exists(students_converted):
        students_file = students_converted
        print("Используется преобразованный файл students_survey_converted.csv")
    else:
        students_file = students_original
        print("Используется исходный файл students_survey.csv")
    
    # Проверяем существование файлов
    if not os.path.exists(parents_file):
        print(f"Ошибка: файл {parents_file} не найден")
        exit(1)
    
    if not os.path.exists(students_file):
        print(f"Ошибка: файл {students_file} не найден")
        exit(1)
    
    # Загружаем данные
    parents_df, students_df = load_data(parents_file, students_file)
    
    # Сопоставляем пары
    pairs_df = match_pairs(parents_df, students_df)
    
    # Рассчитываем корреляции
    correlations_df = calculate_correlations(parents_df, students_df, pairs_df)
    
    # Сохраняем результаты
    output_dir = os.path.join(project_root, 'data', 'raw')
    os.makedirs(output_dir, exist_ok=True)
    
    pairs_output = os.path.join(output_dir, 'pairs_mapping.csv')
    correlations_output = os.path.join(output_dir, 'correlations.csv')
    
    pairs_df.to_csv(pairs_output, index=False, encoding='utf-8-sig')
    print(f"\nСохранено сопоставление пар в: {pairs_output}")
    
    correlations_df.to_csv(correlations_output, index=False, encoding='utf-8-sig')
    print(f"Сохранены корреляции в: {correlations_output}")
    
    # Выводим статистику
    if len(correlations_df) > 0:
        print(f"\nСтатистика корреляций:")
        print(f"  Средняя корреляция: {correlations_df['correlation'].mean():.4f}")
        print(f"  Медианная корреляция: {correlations_df['correlation'].median():.4f}")
        print(f"  Минимальная корреляция: {correlations_df['correlation'].min():.4f}")
        print(f"  Максимальная корреляция: {correlations_df['correlation'].max():.4f}")

