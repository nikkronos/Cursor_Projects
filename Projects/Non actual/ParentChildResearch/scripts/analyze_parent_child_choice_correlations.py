"""
Скрипт для анализа корреляций между ответами родителей и выбором детей в вопросах "Что тебе ближе?"
"""
import pandas as pd
import os
import numpy as np
from scipy.stats import pearsonr

def load_data(parents_file, students_file, pairs_file):
    """Загрузка данных"""
    print(f"Загрузка данных родителей из: {parents_file}")
    parents_df = pd.read_csv(parents_file, encoding='utf-8-sig')
    print(f"  Загружено строк: {len(parents_df)}")
    
    print(f"Загрузка данных учеников из: {students_file}")
    students_df = pd.read_csv(students_file, encoding='utf-8-sig')
    print(f"  Загружено строк: {len(students_df)}")
    
    print(f"Загрузка сопоставления пар из: {pairs_file}")
    pairs_df = pd.read_csv(pairs_file, encoding='utf-8-sig')
    print(f"  Загружено пар: {len(pairs_df)}")
    
    return parents_df, students_df, pairs_df

def analyze_choice_correlations(parents_df, students_df, pairs_df):
    """
    Анализ корреляций между ответами родителей (60 вопросов) 
    и выбором детей в вопросах "Что тебе ближе?" (42 вопроса)
    """
    print("\nАнализ корреляций между ответами родителей и выбором детей...")
    
    # Колонки с ответами родителей (вопросы 1-60)
    parent_start_col = 5  # Первый вопрос у родителей
    parent_end_col = 65   # После последнего вопроса
    
    # Колонки с вопросами "Что тебе ближе?" у детей (вопросы 1-42)
    # Это колонки с индексами 64-105 (в CSV это колонки 65-106)
    choice_start_col = 64  # Первый вопрос "Что тебе ближе?"
    choice_end_col = 106   # После последнего вопроса
    
    # Создаем матрицу корреляций
    # Строки: вопросы родителей (1-60)
    # Колонки: вопросы "Что тебе ближе?" (1-42)
    correlation_matrix = []
    
    for pair_idx, pair in pairs_df.iterrows():
        parent_idx = pair['parent_index']
        student_idx = pair['student_index']
        
        # Получаем ответы родителей
        parent_answers = parents_df.iloc[parent_idx, parent_start_col:parent_end_col].values
        parent_answers = pd.to_numeric(parent_answers, errors='coerce')
        
        # Получаем выборы детей
        child_choices = students_df.iloc[student_idx, choice_start_col:choice_end_col].values
        child_choices = pd.to_numeric(child_choices, errors='coerce')
        
        # Для каждой пары (вопрос родителя, вопрос выбора ребенка) рассчитываем корреляцию
        # Но сначала нужно собрать данные по всем парам
        # Поэтому создадим список всех значений для каждой комбинации
        
        pair_correlations = []
        for parent_q in range(60):  # Вопросы родителей 1-60
            parent_value = parent_answers[parent_q]
            
            if pd.isna(parent_value):
                continue
            
            for choice_q in range(42):  # Вопросы выбора 1-42
                choice_value = child_choices[choice_q]
                
                if pd.isna(choice_value):
                    continue
                
                pair_correlations.append({
                    'pair_id': pair_idx,
                    'parent_question': parent_q + 1,
                    'choice_question': choice_q + 1,
                    'parent_answer': parent_value,
                    'child_choice': choice_value
                })
        
        if pair_idx == 0:
            all_data = pair_correlations
        else:
            all_data.extend(pair_correlations)
    
    # Преобразуем в DataFrame для удобства
    data_df = pd.DataFrame(all_data)
    
    # Теперь рассчитываем корреляции для каждой комбинации вопросов
    print("Расчет корреляций для каждой комбинации вопросов...")
    
    correlations_list = []
    
    for parent_q in range(1, 61):
        for choice_q in range(1, 43):
            # Фильтруем данные для этой комбинации
            subset = data_df[
                (data_df['parent_question'] == parent_q) & 
                (data_df['choice_question'] == choice_q)
            ]
            
            if len(subset) > 1:
                parent_vals = subset['parent_answer'].values
                choice_vals = subset['child_choice'].values
                
                # Удаляем NaN
                mask = ~(np.isnan(parent_vals) | np.isnan(choice_vals))
                parent_clean = parent_vals[mask]
                choice_clean = choice_vals[mask]
                
                if len(parent_clean) > 1:
                    try:
                        correlation, p_value = pearsonr(parent_clean, choice_clean)
                        
                        correlations_list.append({
                            'parent_question': parent_q,
                            'choice_question': choice_q,
                            'correlation': correlation,
                            'p_value': p_value,
                            'n_pairs': len(parent_clean)
                        })
                    except Exception as e:
                        pass  # Игнорируем ошибки
    
    correlations_df = pd.DataFrame(correlations_list)
    
    print(f"  Рассчитано корреляций: {len(correlations_df)}")
    
    return correlations_df

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(base_dir, '..')
    
    # Пути к файлам
    parents_file = os.path.join(project_root, 'data', 'raw', 'parents_survey.csv')
    students_file = os.path.join(project_root, 'data', 'raw', 'students_survey_converted.csv')
    pairs_file = os.path.join(project_root, 'data', 'raw', 'pairs_mapping.csv')
    
    # Проверяем существование файлов
    if not os.path.exists(parents_file):
        print(f"Ошибка: файл {parents_file} не найден")
        exit(1)
    
    if not os.path.exists(students_file):
        print(f"Ошибка: файл {students_file} не найден. Сначала запустите convert_profession_choices.py")
        exit(1)
    
    if not os.path.exists(pairs_file):
        print(f"Ошибка: файл {pairs_file} не найден. Сначала запустите analyze_data.py")
        exit(1)
    
    # Загружаем данные
    parents_df, students_df, pairs_df = load_data(parents_file, students_file, pairs_file)
    
    # Анализируем корреляции
    correlations_df = analyze_choice_correlations(parents_df, students_df, pairs_df)
    
    # Сохраняем результаты
    output_file = os.path.join(project_root, 'data', 'raw', 'parent_child_choice_correlations.csv')
    correlations_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nСохранены корреляции в: {output_file}")
    
    # Выводим статистику
    if len(correlations_df) > 0:
        print(f"\nСтатистика корреляций:")
        print(f"  Средняя корреляция: {correlations_df['correlation'].mean():.4f}")
        print(f"  Медианная корреляция: {correlations_df['correlation'].median():.4f}")
        print(f"  Минимальная корреляция: {correlations_df['correlation'].min():.4f}")
        print(f"  Максимальная корреляция: {correlations_df['correlation'].max():.4f}")
        
        # Топ-10 самых сильных корреляций
        top_correlations = correlations_df.nlargest(10, 'correlation')
        print(f"\nТоп-10 самых сильных корреляций:")
        for idx, row in top_correlations.iterrows():
            print(f"  Вопрос родителя {row['parent_question']} <-> Выбор ребенка {row['choice_question']}: {row['correlation']:.4f} (p={row['p_value']:.4f})")








