import pandas as pd
import os

os.makedirs('data/raw', exist_ok=True)

df1 = pd.read_csv(r'c:\Users\krono\OneDrive\Рабочий стол\Опрос для родителей .csv', encoding='utf-8-sig')
df1.to_csv('data/raw/parents_survey.csv', index=False, encoding='utf-8-sig')
print('Скопирован файл родителей')

df2 = pd.read_csv(r'c:\Users\krono\OneDrive\Рабочий стол\Опрос ученика.csv', encoding='utf-8-sig')
df2.to_csv('data/raw/students_survey.csv', index=False, encoding='utf-8-sig')
print('Скопирован файл учеников')

print('Готово')








