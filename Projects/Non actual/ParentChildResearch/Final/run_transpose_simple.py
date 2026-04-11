"""Упрощённый скрипт для транспонирования - использует относительные пути"""
import pandas as pd
import os

# Определяем пути относительно текущей директории скрипта
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print(f"Рабочая директория: {os.getcwd()}")

# Файлы
parents_input = "Опрос для родителей  (Ответы) - Ответы на форму (1).csv"
parents_output = "Родители трансп.csv"
teens_input = "Опрос ученика (Ответы) - Ответы на форму (1).csv"
teens_output = "Подростки трансп.csv"

# Транспонируем родителей
print("\n" + "="*60)
print("ТРАНСПОНИРОВАНИЕ ФАЙЛА РОДИТЕЛЕЙ")
print("="*60)

df = pd.read_csv(parents_input, encoding='utf-8')
print(f"Исходная форма: {df.shape[0]} строк, {df.shape[1]} столбцов")

if 'Отметка времени' in df.columns:
    df = df.drop(columns=['Отметка времени'])
    print("Удалён столбец 'Отметка времени'")

respondent_names = df['Фамилия, имя родителя '].astype(str) if 'Фамилия, имя родителя ' in df.columns else [f"Респондент_{i+1}" for i in range(len(df))]

df_t = df.T
df_t.columns = respondent_names
df_t = df_t.reset_index()
df_t.rename(columns={'index': 'Вопрос/Метаданные'}, inplace=True)

print(f"Транспонированная форма: {df_t.shape[0]} строк, {df_t.shape[1]} столбцов")
df_t.to_csv(parents_output, index=False, encoding='utf-8-sig')
print(f"Сохранено в: {parents_output}")

# Транспонируем подростков
print("\n" + "="*60)
print("ТРАНСПОНИРОВАНИЕ ФАЙЛА ПОДРОСТКОВ")
print("="*60)

df = pd.read_csv(teens_input, encoding='utf-8')
print(f"Исходная форма: {df.shape[0]} строк, {df.shape[1]} столбцов")

if 'Отметка времени' in df.columns:
    df = df.drop(columns=['Отметка времени'])
    print("Удалён столбец 'Отметка времени'")

respondent_names = df['Фамилия и имя '].astype(str) if 'Фамилия и имя ' in df.columns else [f"Респондент_{i+1}" for i in range(len(df))]

df_t = df.T
df_t.columns = respondent_names
df_t = df_t.reset_index()
df_t.rename(columns={'index': 'Вопрос/Метаданные'}, inplace=True)

print(f"Транспонированная форма: {df_t.shape[0]} строк, {df_t.shape[1]} столбцов")
df_t.to_csv(teens_output, index=False, encoding='utf-8-sig')
print(f"Сохранено в: {teens_output}")

print("\n" + "="*60)
print("ВСЕ ФАЙЛЫ УСПЕШНО ТРАНСПОНИРОВАНЫ!")
print("="*60)
