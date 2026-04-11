"""
Скрипт для генерации новых пар родитель-ребенок на основе существующих данных
"""
import pandas as pd
import numpy as np
import os
from faker import Faker
from scipy.stats import pearsonr

# Инициализация Faker для генерации дат (имена теперь генерируем вручную)
fake = Faker('ru_RU')

# Популярные имена в РФ 2015-2025 (только самые распространенные)
POPULAR_FIRST_NAMES_MALE = ['Александр', 'Максим', 'Артем', 'Михаил', 'Даниил', 'Иван', 'Дмитрий', 
                           'Кирилл', 'Андрей', 'Егор', 'Матвей', 'Тимофей', 'Роман', 'Владимир',
                           'Илья', 'Алексей', 'Никита', 'Сергей', 'Павел', 'Арсений', 'Марк',
                           'Лев', 'Федор', 'Глеб', 'Лука', 'Степан', 'Ярослав', 'Богдан']
POPULAR_FIRST_NAMES_FEMALE = ['София', 'Мария', 'Анна', 'Анастасия', 'Виктория', 'Елизавета', 'Полина',
                             'Алиса', 'Дарья', 'Александра', 'Ева', 'Варвара', 'Милана', 'Вероника',
                             'Маргарита', 'Ксения', 'Валерия', 'Елена', 'Ольга', 'Татьяна', 'Екатерина',
                             'Арина', 'Ульяна', 'Юлия', 'Ирина', 'Светлана', 'Наталья', 'Марина']
POPULAR_LAST_NAMES = ['Иванов', 'Петров', 'Смирнов', 'Кузнецов', 'Попов', 'Соколов', 'Лебедев', 
                     'Козлов', 'Новиков', 'Морозов', 'Волков', 'Соловьев', 'Васильев', 'Зайцев',
                     'Павлов', 'Семенов', 'Голубев', 'Виноградов', 'Богданов', 'Воробьев']

def generate_russian_name(gender='random'):
    """Генерация русского имени на основе популярных имен 2015-2025"""
    if gender == 'random':
        gender = np.random.choice(['male', 'female'])
    
    if gender == 'male':
        first_name = np.random.choice(POPULAR_FIRST_NAMES_MALE)
    else:
        first_name = np.random.choice(POPULAR_FIRST_NAMES_FEMALE)
    
    last_name = np.random.choice(POPULAR_LAST_NAMES)
    if gender == 'female':
        # Склоняем фамилию для женского пола
        if last_name.endswith('ов') or last_name.endswith('ев'):
            last_name = last_name[:-2] + 'а'
        elif last_name.endswith('ин'):
            last_name = last_name[:-2] + 'ина'
        elif last_name.endswith('ский'):
            last_name = last_name[:-4] + 'ская'
    
    return f"{last_name} {first_name}"

def generate_first_name(gender='random'):
    """Генерация только имени"""
    if gender == 'random':
        gender = np.random.choice(['male', 'female'])
    
    if gender == 'male':
        return np.random.choice(POPULAR_FIRST_NAMES_MALE)
    else:
        return np.random.choice(POPULAR_FIRST_NAMES_FEMALE)

def load_existing_data(parents_file, students_file, pairs_file, correlations_file, choice_correlations_file):
    """Загрузка существующих данных"""
    print("Загрузка существующих данных...")
    
    parents_df = pd.read_csv(parents_file, encoding='utf-8-sig')
    students_df = pd.read_csv(students_file, encoding='utf-8-sig')
    pairs_df = pd.read_csv(pairs_file, encoding='utf-8-sig')
    correlations_df = pd.read_csv(correlations_file, encoding='utf-8-sig')
    
    choice_correlations_df = None
    if os.path.exists(choice_correlations_file):
        choice_correlations_df = pd.read_csv(choice_correlations_file, encoding='utf-8-sig')
        print(f"  Загружены корреляции выбора: {len(choice_correlations_df)} записей")
    
    print(f"  Загружено пар: {len(pairs_df)}")
    print(f"  Загружено корреляций: {len(correlations_df)}")
    
    return parents_df, students_df, pairs_df, correlations_df, choice_correlations_df

def generate_parent_responses(parents_template, num_new):
    """Генерация ответов родителей на основе существующих данных"""
    print(f"\nГенерация ответов для {num_new} родителей...")
    
    # Колонки с ответами (вопросы 1-60)
    answer_start_col = 5
    answer_end_col = 65
    
    new_parents = []
    
    for i in range(num_new):
        # Выбираем случайный шаблон
        template_idx = np.random.randint(0, len(parents_template))
        template_row = parents_template.iloc[template_idx]
        
        # Определяем пол ребенка случайно
        child_gender = np.random.choice(['male', 'female'])
        child_name = generate_first_name(child_gender)
        
        # Генерируем имя родителя (обычно противоположного пола для разнообразия)
        parent_gender = 'female' if child_gender == 'male' else 'male'
        parent_name = generate_russian_name(parent_gender)
        
        # Копируем метаданные
        new_parent = {
            'Отметка времени': fake.date_time_between(start_date='-1y', end_date='now').strftime('%Y/%m/%d %I:%M:%S %p GMT+3'),
            'Фамилия, имя родителя ': parent_name,
            '  Фамилия и имя ребенка  ': child_name,
            '  Возраст ребенка ': np.random.choice([14, 15, 16]),
            'Я даю согласие на обработку персональных данных моих и моего ребенка в исследовательских целях. Мне известно, что данные будут использованы только в обобщенном виде. ': 'Подтверждаю'
        }
        
        # Генерируем ответы на основе шаблона с небольшими вариациями
        # Используем реальные названия колонок из CSV
        for j in range(60):
            col_idx = answer_start_col + j
            if col_idx < len(parents_template.columns):
                col_name = parents_template.columns[col_idx]
                answer = template_row[col_name]
                answer = pd.to_numeric(answer, errors='coerce')
                
                if pd.notna(answer):
                    # Добавляем случайное отклонение (-1, 0, или +1)
                    variation = np.random.choice([-1, 0, 1], p=[0.2, 0.6, 0.2])
                    new_answer = max(1, min(5, int(answer) + variation))
                    new_parent[col_name] = new_answer
                else:
                    new_parent[col_name] = np.random.randint(1, 6)
            else:
                # Если колонка не существует, создаем новую
                col_name = parents_template.columns[answer_start_col] if answer_start_col < len(parents_template.columns) else f'Q{j+1}'
                new_parent[col_name] = np.random.randint(1, 6)
        
        new_parents.append(new_parent)
    
    new_parents_df = pd.DataFrame(new_parents)
    print(f"  Сгенерировано родителей: {len(new_parents_df)}")
    
    return new_parents_df

def generate_child_choice(parent_answer, parent_question, choice_question, choice_correlations_df):
    """
    Генерация выбора ребенка (1 или 2) на основе ответа родителя и корреляций
    """
    if choice_correlations_df is None:
        # Если нет корреляций, выбираем случайно
        return np.random.choice([1, 2])
    
    # Находим корреляцию для этой комбинации вопросов
    correlation_row = choice_correlations_df[
        (choice_correlations_df['parent_question'] == parent_question) &
        (choice_correlations_df['choice_question'] == choice_question)
    ]
    
    if len(correlation_row) == 0:
        # Если нет корреляции, выбираем случайно
        return np.random.choice([1, 2])
    
    correlation = correlation_row.iloc[0]['correlation']
    
    # Используем корреляцию для определения вероятности выбора
    # Если корреляция положительная и ответ родителя высокий, увеличиваем вероятность выбора 1
    # Если корреляция отрицательная, инвертируем логику
    
    base_prob = 0.5
    if correlation > 0:
        # Положительная корреляция: высокий ответ родителя -> выше вероятность выбора 1
        prob_adjustment = (parent_answer - 3) / 10 * abs(correlation)
    else:
        # Отрицательная корреляция: высокий ответ родителя -> выше вероятность выбора 2
        prob_adjustment = -(parent_answer - 3) / 10 * abs(correlation)
    
    prob_choice_1 = base_prob + prob_adjustment
    prob_choice_1 = max(0.1, min(0.9, prob_choice_1))  # Ограничиваем диапазон
    
    return np.random.choice([1, 2], p=[prob_choice_1, 1 - prob_choice_1])

def generate_student_responses(students_template, parents_template, new_parents_df, pairs_df, 
                               choice_correlations_df, num_new):
    """Генерация ответов учеников на основе существующих данных и корреляций"""
    print(f"\nГенерация ответов для {num_new} учеников...")
    
    # Колонки с ответами (вопросы 1-60)
    answer_start_col = 4
    answer_end_col = 64
    
    # Колонки с вопросами "Что тебе ближе?" (вопросы 1-42)
    choice_start_col = 64
    choice_end_col = 106
    
    new_students = []
    
    for i in range(num_new):
        # Выбираем случайный шаблон
        template_idx = np.random.randint(0, len(students_template))
        template_row = students_template.iloc[template_idx]
        
        # Получаем соответствующие ответы родителя
        parent_row = new_parents_df.iloc[i]
        parent_answers = [parent_row.get(f'Q{j+1}', np.random.randint(1, 6)) for j in range(60)]
        
        # Копируем метаданные
        new_student = {
            'Отметка времени': fake.date_time_between(start_date='-1y', end_date='now').strftime('%Y/%m/%d %I:%M:%S %p GMT+3'),
            'Фамилия и имя ': parent_row['  Фамилия и имя ребенка  '],
            'Возраст ': parent_row['  Возраст ребенка '],
            'Класс ': np.random.choice(['9', '9е', '9Е', '10', 'Студент'])
        }
        
        # Генерируем ответы на вопросы 1-60 на основе шаблона
        # Используем реальные названия колонок из CSV
        for j in range(60):
            col_idx = answer_start_col + j
            if col_idx < len(students_template.columns):
                col_name = students_template.columns[col_idx]
                answer = template_row[col_name]
                answer = pd.to_numeric(answer, errors='coerce')
                
                if pd.notna(answer):
                    variation = np.random.choice([-1, 0, 1], p=[0.2, 0.6, 0.2])
                    new_answer = max(1, min(5, int(answer) + variation))
                    new_student[col_name] = new_answer
                else:
                    new_student[col_name] = np.random.randint(1, 6)
            else:
                col_name = students_template.columns[answer_start_col] if answer_start_col < len(students_template.columns) else f'Q{j+1}'
                new_student[col_name] = np.random.randint(1, 6)
        
        # Генерируем выборы в вопросах "Что тебе ближе?" на основе корреляций
        for choice_q in range(1, 43):
            col_idx = choice_start_col + choice_q - 1
            if col_idx < len(students_template.columns):
                col_name = students_template.columns[col_idx]
            else:
                col_name = f'Choice{choice_q}'
            
            # Используем средний ответ родителя или конкретный вопрос
            avg_parent_answer = np.mean([a for a in parent_answers if pd.notna(a)])
            
            choice = generate_child_choice(
                avg_parent_answer, 
                np.random.randint(1, 61),  # Случайный вопрос родителя
                choice_q,
                choice_correlations_df
            )
            new_student[col_name] = choice
        
        # Генерируем ответы на вопросы о профессиях (20 вопросов)
        for j in range(20):
            col_idx = choice_end_col + j
            if col_idx < len(students_template.columns):
                col_name = students_template.columns[col_idx]
            else:
                col_name = f'ProfQ{j+1}'
            new_student[col_name] = np.random.randint(1, 6)
        
        new_students.append(new_student)
    
    new_students_df = pd.DataFrame(new_students)
    print(f"  Сгенерировано учеников: {len(new_students_df)}")
    
    return new_students_df

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(base_dir, '..')
    
    # Пути к файлам
    parents_file = os.path.join(project_root, 'data', 'raw', 'parents_survey.csv')
    students_file = os.path.join(project_root, 'data', 'raw', 'students_survey_converted.csv')
    pairs_file = os.path.join(project_root, 'data', 'raw', 'pairs_mapping.csv')
    correlations_file = os.path.join(project_root, 'data', 'raw', 'correlations.csv')
    choice_correlations_file = os.path.join(project_root, 'data', 'raw', 'parent_child_choice_correlations.csv')
    
    # Загружаем существующие данные
    parents_df, students_df, pairs_df, correlations_df, choice_correlations_df = load_existing_data(
        parents_file, students_file, pairs_file, correlations_file, choice_correlations_file
    )
    
    # Определяем количество новых пар для генерации
    num_existing = len(pairs_df)
    num_new = 50 - num_existing
    
    print(f"\nСуществующих пар: {num_existing}")
    print(f"Нужно сгенерировать: {num_new}")
    
    if num_new <= 0:
        print("Уже есть 50 или больше пар. Генерация не требуется.")
        exit(0)
    
    # Генерируем новые данные
    new_parents_df = generate_parent_responses(parents_df, num_new)
    new_students_df = generate_student_responses(
        students_df, parents_df, new_parents_df, pairs_df, 
        choice_correlations_df, num_new
    )
    
    # Сохраняем результаты
    output_dir = os.path.join(project_root, 'data', 'generated')
    os.makedirs(output_dir, exist_ok=True)
    
    new_parents_output = os.path.join(output_dir, 'new_parents.csv')
    new_students_output = os.path.join(output_dir, 'new_students.csv')
    
    new_parents_df.to_csv(new_parents_output, index=False, encoding='utf-8-sig')
    new_students_df.to_csv(new_students_output, index=False, encoding='utf-8-sig')
    
    print(f"\nСохранены новые данные:")
    print(f"  Родители: {new_parents_output}")
    print(f"  Ученики: {new_students_output}")

