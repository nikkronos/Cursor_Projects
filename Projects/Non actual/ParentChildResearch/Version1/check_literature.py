"""Скрипт для проверки использования источников в тексте Главы II"""
import re
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
chapter_file = os.path.join(script_dir, "ГЛАВА_II.md")
# Файл литературы находится на рабочем столе
desktop_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Рабочий стол")
literature_file = os.path.join(desktop_path, "1. Абульханова-Славская К.А. Страте.txt")

# Если файл не найден, пробуем альтернативный путь
if not os.path.exists(literature_file):
    # Альтернативный путь без OneDrive
    desktop_path_alt = os.path.join(os.path.expanduser("~"), "Desktop")
    literature_file_alt = os.path.join(desktop_path_alt, "1. Абульханова-Славская К.А. Страте.txt")
    if os.path.exists(literature_file_alt):
        literature_file = literature_file_alt

# Читаем текст Главы II
print("Чтение текста Главы II...")
with open(chapter_file, 'r', encoding='utf-8') as f:
    chapter_text = f.read()

# Читаем список литературы
print("Чтение списка литературы...")
if not os.path.exists(literature_file):
    print(f"ОШИБКА: Файл литературы не найден!")
    print(f"Искомый путь: {literature_file}")
    print("\nПожалуйста, убедитесь, что файл '1. Абульханова-Славская К.А. Страте.txt'")
    print("находится на рабочем столе (OneDrive\\Рабочий стол)")
    exit(1)

with open(literature_file, 'r', encoding='utf-8') as f:
    literature_text = f.read()
print(f"✓ Файл найден: {literature_file}")

# Парсим список литературы
# Файл содержит все источники в одной строке, разделенные номерами
literature_items = []
# Объединяем все строки в одну
full_text = ' '.join(literature_text.split('\n'))

# Находим все позиции "число. " в тексте
matches = list(re.finditer(r'(\d+)\.\s+', full_text))

for i, match in enumerate(matches):
    num = int(match.group(1))
    start_pos = match.end()  # Начало текста после "число. "
    
    # Конец текста - начало следующего "число. " или конец строки
    if i + 1 < len(matches):
        end_pos = matches[i + 1].start()
    else:
        end_pos = len(full_text)
    
    text = full_text[start_pos:end_pos].strip()
    
    # Убираем эмодзи 🚩 если есть
    text = text.replace('🚩', '').strip()
    
    if text:
        # Извлекаем фамилию автора (первое слово после номера)
        author_match = re.match(r'^([А-ЯЁA-Z][а-яёa-z]+(?:\s+[А-ЯЁA-Z]\.?[А-ЯЁA-Z]\.?)?)', text)
        if author_match:
            author_surname = author_match.group(1).split()[0]
        else:
            # Если не нашли, берем первое слово
            words = text.split()
            author_surname = words[0] if words else "Неизвестно"
        
        literature_items.append({
            'number': num,
            'full_text': f"{num}. {text}",
            'author_surname': author_surname,
            'author_text': text
        })

print(f"Найдено {len(literature_items)} источников в списке литературы")

# Ищем упоминания авторов в тексте
print("\nПоиск упоминаний авторов в тексте...")
used_authors = set()
used_numbers = set()

# Ищем ссылки в квадратных скобках [N] или [N; M]
bracket_refs = re.findall(r'\[(\d+(?:[;\s]+\d+)*)\]', chapter_text)
for ref in bracket_refs:
    numbers = re.findall(r'\d+', ref)
    for num in numbers:
        used_numbers.add(int(num))

# Ищем упоминания фамилий авторов в тексте
for item in literature_items:
    surname = item['author_surname']
    # Ищем фамилию в тексте (с учетом возможных вариантов написания)
    patterns = [
        surname,
        surname.replace('ё', 'е'),
        surname.replace('е', 'ё'),
    ]
    
    for pattern in patterns:
        if pattern.lower() in chapter_text.lower():
            used_authors.add(item['author_surname'])
            used_numbers.add(item['number'])
            break

print(f"\nНайдено использованных источников: {len(used_numbers)}")
print(f"Найдено упоминаний авторов: {len(used_authors)}")

# Определяем неиспользованные источники
all_numbers = {item['number'] for item in literature_items}
unused_numbers = all_numbers - used_numbers

print(f"\nНеиспользованных источников: {len(unused_numbers)}")

# Выводим использованные источники
print("\n" + "="*80)
print("ИСПОЛЬЗОВАННЫЕ ИСТОЧНИКИ:")
print("="*80)
used_items = [item for item in literature_items if item['number'] in used_numbers]
for item in sorted(used_items, key=lambda x: x['number']):
    print(f"{item['number']}. {item['full_text']}")

# Выводим неиспользованные источники
print("\n" + "="*80)
print("НЕИСПОЛЬЗОВАННЫЕ ИСТОЧНИКИ:")
print("="*80)
unused_items = [item for item in literature_items if item['number'] in unused_numbers]
for item in sorted(unused_items, key=lambda x: x['number']):
    print(f"{item['number']}. {item['full_text']}")

# Сохраняем очищенный список литературы
print("\n" + "="*80)
print("СОХРАНЕНИЕ ОЧИЩЕННОГО СПИСКА ЛИТЕРАТУРЫ...")
print("="*80)

cleaned_literature = []
for item in sorted(used_items, key=lambda x: x['number']):
    # Перенумеровываем
    new_num = len(cleaned_literature) + 1
    cleaned_text = item['full_text'].replace(f"{item['number']}.", f"{new_num}.", 1)
    cleaned_literature.append(cleaned_text)

output_file = os.path.join(script_dir, "Список_литературы_очищенный.txt")
with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(cleaned_literature))

print(f"✓ Очищенный список сохранен в: {output_file}")
print(f"  Всего источников: {len(cleaned_literature)} (было {len(literature_items)})")
print(f"  Удалено: {len(unused_numbers)} источников")

