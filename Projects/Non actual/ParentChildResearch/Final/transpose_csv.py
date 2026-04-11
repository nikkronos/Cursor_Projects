"""
Скрипт для транспонирования CSV файлов с опросами родителей и подростков.
Транспонирует таблицы: строки становятся столбцами, столбцы - строками.
Удаляет столбец "Отметка времени", сохраняет остальные метаданные.
"""
import pandas as pd
import os

def transpose_parents_csv(input_file, output_file):
    """Транспонирует CSV файл с ответами родителей."""
    print(f"Читаю файл: {input_file}")
    
    # Читаем CSV файл
    df = pd.read_csv(input_file, encoding='utf-8')
    
    print(f"Исходная форма: {df.shape[0]} строк, {df.shape[1]} столбцов")
    
    # Удаляем столбец "Отметка времени"
    if 'Отметка времени' in df.columns:
        df = df.drop(columns=['Отметка времени'])
        print("Удалён столбец 'Отметка времени'")
    
    # Получаем имена респондентов для заголовков столбцов
    if 'Фамилия, имя родителя ' in df.columns:
        respondent_names = df['Фамилия, имя родителя '].astype(str)
    elif 'Фамилия, имя родителя' in df.columns:
        respondent_names = df['Фамилия, имя родителя'].astype(str)
    else:
        # Если столбца с именем нет, используем номера
        respondent_names = [f"Респондент_{i+1}" for i in range(len(df))]
    
    # Транспонируем DataFrame
    df_transposed = df.T
    
    # Устанавливаем заголовки столбцов (имена респондентов)
    df_transposed.columns = respondent_names
    
    # Первый столбец теперь содержит названия вопросов/метаданных
    # Преобразуем индекс в первый столбец
    df_transposed = df_transposed.reset_index()
    df_transposed.rename(columns={'index': 'Вопрос/Метаданные'}, inplace=True)
    
    print(f"Транспонированная форма: {df_transposed.shape[0]} строк, {df_transposed.shape[1]} столбцов")
    print(f"Сохранение в файл: {output_file}")
    
    # Сохраняем в CSV
    df_transposed.to_csv(output_file, index=False, encoding='utf-8-sig')
    print("Готово!\n")
    
    return df_transposed

def transpose_teens_csv(input_file, output_file):
    """Транспонирует CSV файл с ответами подростков."""
    print(f"Читаю файл: {input_file}")
    
    # Читаем CSV файл
    df = pd.read_csv(input_file, encoding='utf-8')
    
    print(f"Исходная форма: {df.shape[0]} строк, {df.shape[1]} столбцов")
    
    # Удаляем столбец "Отметка времени"
    if 'Отметка времени' in df.columns:
        df = df.drop(columns=['Отметка времени'])
        print("Удалён столбец 'Отметка времени'")
    
    # Получаем имена респондентов для заголовков столбцов
    if 'Фамилия и имя ' in df.columns:
        respondent_names = df['Фамилия и имя '].astype(str)
    elif 'Фамилия и имя' in df.columns:
        respondent_names = df['Фамилия и имя'].astype(str)
    else:
        # Если столбца с именем нет, используем номера
        respondent_names = [f"Респондент_{i+1}" for i in range(len(df))]
    
    # Транспонируем DataFrame
    df_transposed = df.T
    
    # Устанавливаем заголовки столбцов (имена респондентов)
    df_transposed.columns = respondent_names
    
    # Первый столбец теперь содержит названия вопросов/метаданных
    # Преобразуем индекс в первый столбец
    df_transposed = df_transposed.reset_index()
    df_transposed.rename(columns={'index': 'Вопрос/Метаданные'}, inplace=True)
    
    print(f"Транспонированная форма: {df_transposed.shape[0]} строк, {df_transposed.shape[1]} столбцов")
    print(f"Сохранение в файл: {output_file}")
    
    # Сохраняем в CSV
    df_transposed.to_csv(output_file, index=False, encoding='utf-8-sig')
    print("Готово!\n")
    
    return df_transposed

def main():
    # Определяем пути к файлам
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    parents_input = os.path.join(script_dir, "Опрос для родителей  (Ответы) - Ответы на форму (1).csv")
    parents_output = os.path.join(script_dir, "Родители трансп.csv")
    
    teens_input = os.path.join(script_dir, "Опрос ученика (Ответы) - Ответы на форму (1).csv")
    teens_output = os.path.join(script_dir, "Подростки трансп.csv")
    
    # Проверяем наличие входных файлов
    if not os.path.exists(parents_input):
        print(f"ОШИБКА: Файл не найден: {parents_input}")
        return
    
    if not os.path.exists(teens_input):
        print(f"ОШИБКА: Файл не найден: {teens_input}")
        return
    
    # Транспонируем файл родителей
    print("=" * 60)
    print("ТРАНСПОНИРОВАНИЕ ФАЙЛА РОДИТЕЛЕЙ")
    print("=" * 60)
    transpose_parents_csv(parents_input, parents_output)
    
    # Транспонируем файл подростков
    print("=" * 60)
    print("ТРАНСПОНИРОВАНИЕ ФАЙЛА ПОДРОСТКОВ")
    print("=" * 60)
    transpose_teens_csv(teens_input, teens_output)
    
    print("=" * 60)
    print("ВСЕ ФАЙЛЫ УСПЕШНО ТРАНСПОНИРОВАНЫ!")
    print("=" * 60)

if __name__ == "__main__":
    main()
