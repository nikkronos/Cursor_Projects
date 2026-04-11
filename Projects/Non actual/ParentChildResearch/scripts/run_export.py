"""Запуск экспорта в XLSX"""
import sys
import os

# Добавляем путь к скриптам
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем и запускаем экспорт
from export_to_xlsx import *

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
        print(f"Ошибка: файл {students_file} не найден")
        exit(1)
    
    if not os.path.exists(pairs_file):
        print(f"Ошибка: файл {pairs_file} не найден")
        exit(1)
    
    # Загружаем данные
    parents_df, students_df, pairs_df = load_data(parents_file, students_file, pairs_file)
    
    # Экспортируем существующие пары
    output_dir = os.path.join(project_root, 'data', 'generated')
    os.makedirs(output_dir, exist_ok=True)
    
    existing_output = os.path.join(output_dir, 'existing_pairs.xlsx')
    export_to_xlsx(parents_df, students_df, pairs_df, existing_output, "Existing Pairs")
    
    # Если есть сгенерированные данные, экспортируем все 50 пар
    new_parents_file = os.path.join(project_root, 'data', 'generated', 'new_parents.csv')
    new_students_file = os.path.join(project_root, 'data', 'generated', 'new_students.csv')
    
    if os.path.exists(new_parents_file) and os.path.exists(new_students_file):
        print("\nЗагрузка сгенерированных данных...")
        new_parents_df = pd.read_csv(new_parents_file, encoding='utf-8-sig')
        new_students_df = pd.read_csv(new_students_file, encoding='utf-8-sig')
        
        # Объединяем существующие и новые данные
        all_parents_df = pd.concat([parents_df, new_parents_df], ignore_index=True)
        all_students_df = pd.concat([students_df, new_students_df], ignore_index=True)
        
        # Создаем пары для всех данных
        all_pairs = []
        for i in range(len(pairs_df)):
            all_pairs.append(pairs_df.iloc[i].to_dict())
        
        # Добавляем пары для новых данных
        for i in range(len(new_parents_df)):
            all_pairs.append({
                'parent_index': len(parents_df) + i,
                'student_index': len(students_df) + i,
                'parent_name': new_parents_df.iloc[i].get('Фамилия, имя родителя ', ''),
                'child_name': new_parents_df.iloc[i].get('  Фамилия и имя ребенка  ', ''),
                'student_name': new_students_df.iloc[i].get('Фамилия и имя ', ''),
                'match_score': 0
            })
        
        all_pairs_df = pd.DataFrame(all_pairs)
        
        # Экспортируем все 50 пар
        all_output = os.path.join(output_dir, 'all_50_pairs.xlsx')
        export_to_xlsx(all_parents_df, all_students_df, all_pairs_df, all_output, "All 50 Pairs")
    
    print("\nЭкспорт завершен!")





