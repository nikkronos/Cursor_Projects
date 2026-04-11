# -*- coding: utf-8 -*-
"""
Тест паттернов для проверки, что они правильно находят проблемные места
"""
import re

# Тестовые строки из документа
test_cases = [
    "системный семейный подход (Андреева 5)",
    "системный семейный подход (Эдельмин, Юскис 64)",
    "подход (Андреева 5), (Эдельмин, Юскис 64)",
    "Корреляция между установкой «Я не считаю его (ее) таким умным и способным, как мне хотелось бы» и ориентацией на профессиональный рост (вопрос 12)",
    "Адлер [2] подчеркивал роль",
    "Гинзбург [16], Климов [25], Прихожан [41], Толстых [41]",
    "Возрастной и культурно-исторический подход [16; 57]",
    "Ценностно-смысловой подход [36; 40; 60]",
]

# Паттерн для фамилий в скобках
pattern1 = r'\(([А-ЯЁ][а-яё]+(?:\-[А-ЯЁ][а-яё]+)?(?:\s*,\s*[А-ЯЁ][а-яё]+(?:\-[А-ЯЁ][а-яё]+)?)?)\s+(\d+)\)'

print("=" * 70)
print("ТЕСТ ПАТТЕРНОВ")
print("=" * 70)

for i, test_text in enumerate(test_cases, 1):
    print(f"\n{i}. Исходный текст: {test_text}")
    
    matches = list(re.finditer(pattern1, test_text))
    if matches:
        print(f"   Найдено совпадений: {len(matches)}")
        for match in matches:
            print(f"     - {match.group(0)} -> группа 1: '{match.group(1)}', группа 2: '{match.group(2)}'")
            
            # Проверяем, что это не "вопрос"
            names_str = match.group(1).strip()
            exclude_words = ['вопрос', 'его', 'нее', 'него', 'ней']
            if any(word in names_str.lower() for word in exclude_words):
                print(f"       -> ИСКЛЮЧЕНО (содержит исключаемое слово)")
            else:
                num = match.group(2)
                names = [n.strip() for n in names_str.split(',')]
                if len(names) == 1:
                    result = f"{names[0]} [{num}]"
                else:
                    result = f"{', '.join(names)} [{num}]"
                print(f"       -> РЕЗУЛЬТАТ: {result}")
    else:
        print(f"   Совпадений не найдено")

print("\n" + "=" * 70)
print("ТЕСТ ПАТТЕРНА ДЛЯ НЕВЕРНЫХ НОМЕРОВ")
print("=" * 70)

# Тест для неверных номеров
test_numbers = [
    "[16; 57]",
    "[36; 40; 60]",
    "[1; 2; 3]",
    "[54]",
    "[64]",
]

pattern2 = r'\[(\d+(?:[,\s;]\s*\d+)*)\]'
max_source = 53
min_source = 1

for test_text in test_numbers:
    print(f"\nИсходный текст: {test_text}")
    match = re.search(pattern2, test_text)
    if match:
        numbers_str = match.group(1)
        valid_numbers = []
        for num_str in re.split(r'[,\s;]+', numbers_str):
            num_str = num_str.strip()
            try:
                num = int(num_str)
                if min_source <= num <= max_source:
                    valid_numbers.append(num)
                    print(f"  {num} - OK")
                else:
                    print(f"  {num} - НЕВЕРНЫЙ (вне диапазона {min_source}-{max_source})")
            except ValueError:
                pass
        
        if valid_numbers:
            result = f"[{', '.join(map(str, sorted(set(valid_numbers))))}]"
            print(f"  РЕЗУЛЬТАТ: {result}")
        else:
            print(f"  РЕЗУЛЬТАТ: (удалено)")




