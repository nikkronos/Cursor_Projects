# -*- coding: utf-8 -*-
"""
Тест обработки фамилий в квадратных скобках
"""
import re

test_cases = [
    "[Андреева, 5; Эйдемиллер, Юстицкис, 64]",
    "[Адлер; 2]",
    "[Гинзбург, 18; Климов, 30; Прихожан, Толстых, 49]",
    "[30, 40]",  # Только номера - не должно обрабатываться
    "[Андреева, 5]",  # Один автор
]

pattern = r'\[([А-ЯЁ][а-яё]+(?:\-[А-ЯЁ][а-яё]+)?(?:\s*,\s*\d+)?(?:\s*;\s*[А-ЯЁ][а-яё]+(?:\-[А-ЯЁ][а-яё]+)?(?:\s*,\s*\d+)?)*)\]'

print("=" * 70)
print("ТЕСТ ПАТТЕРНА ДЛЯ ФАМИЛИЙ В КВАДРАТНЫХ СКОБКАХ")
print("=" * 70)

for test_text in test_cases:
    print(f"\nИсходный текст: {test_text}")
    match = re.search(pattern, test_text)
    
    if match:
        print(f"  ✓ Найдено совпадение")
        content = match.group(1)
        print(f"  Содержимое: {content}")
        
        # Парсим
        parts = [p.strip() for p in content.split(';')]
        print(f"  Части (разделены по ;): {parts}")
        
        authors_with_numbers = []
        for part in parts:
            number_match = re.search(r'(\d+)\s*$', part)
            if number_match:
                number = int(number_match.group(1))
                authors_part = part[:number_match.start()].strip().rstrip(',')
                authors = [a.strip() for a in authors_part.split(',')]
                authors = [a for a in authors if a and re.match(r'^[А-ЯЁ][а-яё]+', a)]
                
                if authors:
                    print(f"    - Авторы: {authors}, Номер: {number}")
                    authors_with_numbers.append({
                        'authors': authors,
                        'number': number
                    })
        
        if authors_with_numbers:
            # Формируем результат для страницы 4
            result_parts = []
            for item in authors_with_numbers:
                if len(item['authors']) == 1:
                    result_parts.append(f"{item['authors'][0]} [{item['number']}]")
                else:
                    authors_str = ', '.join(item['authors'][:-1]) + f" и {item['authors'][-1]}"
                    result_parts.append(f"{authors_str} [{item['number']}]")
            
            result = ', '.join(result_parts)
            print(f"  РЕЗУЛЬТАТ: {result}")
        else:
            print(f"  ✗ Авторы не найдены")
    else:
        print(f"  ✗ Совпадений не найдено")




