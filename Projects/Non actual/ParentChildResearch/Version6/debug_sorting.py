# -*- coding: utf-8 -*-
"""
Скрипт для диагностики сортировки
"""
from pathlib import Path
import re

# Правильный порядок русского алфавита для сортировки
russian_alphabet_order = {
    'А': 0, 'Б': 1, 'В': 2, 'Г': 3, 'Д': 4, 'Е': 5, 'Ё': 5.5,
    'Ж': 6, 'З': 7, 'И': 8, 'Й': 9, 'К': 10, 'Л': 11, 'М': 12,
    'Н': 13, 'О': 14, 'П': 15, 'Р': 16, 'С': 17, 'Т': 18, 'У': 19,
    'Ф': 20, 'Х': 21, 'Ц': 22, 'Ч': 23, 'Ш': 24, 'Щ': 25,
    'Ъ': 26, 'Ы': 27, 'Ь': 28, 'Э': 29, 'Ю': 30, 'Я': 31
}

def extract_author_surname(entry: str) -> str:
    """Извлекает фамилию первого автора"""
    entry = re.sub(r'^\d+\.\s*', '', entry.strip())
    
    match = re.match(r'^([А-ЯЁ][а-яё]+(?:\-[А-ЯЁ][а-яё]+)?)', entry)
    if match:
        surname = match.group(1)
        return surname.upper()
    
    match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z]\.?)*)', entry)
    if match:
        surname = match.group(1).split()[0]
        return surname.upper()
    
    match = re.search(r'([А-ЯЁA-Z])', entry)
    if match:
        return match.group(1)
    
    return 'Я'

def get_sort_key(surname):
    """Возвращает кортеж для правильной сортировки"""
    if not surname:
        return (3, 999, surname)
    
    first_char = surname[0].upper()
    
    if first_char in russian_alphabet_order:
        pos = russian_alphabet_order[first_char]
        return (0, pos, surname.upper())
    elif first_char.isalpha() and ord(first_char) < 128:
        return (1, ord(first_char), surname.upper())
    else:
        return (2, ord(first_char) if first_char else 999, surname.upper())

# Тестируем проблемные записи
test_entries = [
    "Осорина М.В. Секретный мир детей",
    "Петровский А.В. Психология развивающейся личности",
    "Поваренков Ю.П. Психологическое содержание",
    "Пряжников Н.С. Активизирующие опросники",
    "Резапкина Г.В. Методика",
    "Ремшмидт Х. Подростковый и юношеский возраст",
    "Роджерс К.Р. Взгляд на психотерапию",
    "Сидоренко Е.В. Методы математической обработки",
    "Слободчиков В.И., Исаев Е.И. Психология развития",
    "Сапогова Е.Е. Психология развития человека",
    "Фельдштейн Д.И. Психология взросления",
    "Фонарев А.Р. Формы становления личности",
    "Франкл В. Человек в поисках смысла",
    "Фромм А. Азбука для родителей",
    "Эйдемиллер Э.Г., Юстицкис В.В. Психология и психотерапия семьи",
    "Ядов В.А. Социологическое исследование"
]

print("Проверка сортировки проблемных записей:\n")
items = []
for entry in test_entries:
    surname = extract_author_surname(entry)
    sort_key = get_sort_key(surname)
    items.append((sort_key, surname, entry))

items.sort(key=lambda x: x[0])

print("Результат сортировки:")
for idx, (sort_key, surname, entry) in enumerate(items, 1):
    print(f"{idx:2}. {surname:15} | {entry[:50]}")
