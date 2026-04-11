"""Проверка и очистка списка литературы"""
import re
import os

# Читаем список литературы
literature_file = os.path.join(os.path.dirname(__file__), '..', '..', '1. Абульханова-Славская К.А. Страте.txt')
if not os.path.exists(literature_file):
    # Пробуем альтернативный путь
    desktop_path = os.path.expanduser(r"~\OneDrive\Рабочий стол")
    literature_file = os.path.join(desktop_path, "1. Абульханова-Славская К.А. Страте.txt")

# Читаем текст Главы II
chapter_file = os.path.join(os.path.dirname(__file__), 'ГЛАВА_II.md')

print("Проверка списка литературы...")

# Читаем список литературы
with open(literature_file, 'r', encoding='utf-8') as f:
    literature_text = f.read()

# Читаем Главу II
with open(chapter_file, 'r', encoding='utf-8') as f:
    chapter_text = f.read()

# Парсим список литературы (формат: номер. Автор Название)
literature_items = []
for line in literature_text.split('\n'):
    line = line.strip()
    if line and re.match(r'^\d+\.', line):
        # Извлекаем номер и текст
        match = re.match(r'^(\d+)\.\s*(.+)', line)
        if match:
            num = int(match.group(1))
            text = match.group(2).strip()
            # Убираем эмодзи и лишние символы
            text = re.sub(r'🚩', '', text).strip()
            literature_items.append((num, text))

print(f"Найдено {len(literature_items)} источников в списке литературы")

# Ищем ссылки в тексте (формат [номер] или [номер; номер])
used_numbers = set()
citations = re.findall(r'\[(\d+(?:[;\s]*\d+)*)\]', chapter_text)
for citation in citations:
    # Разбираем ссылки вида "12" или "12; 18; 30"
    numbers = re.findall(r'\d+', citation)
    for num_str in numbers:
        used_numbers.add(int(num_str))

print(f"Найдено {len(used_numbers)} использованных источников: {sorted(used_numbers)}")

# Фильтруем использованные источники
used_literature = []
for num, text in literature_items:
    if num in used_numbers:
        used_literature.append((num, text))

# Сортируем по номеру
used_literature.sort(key=lambda x: x[0])

# Сохраняем очищенный список
output_file = os.path.join(os.path.dirname(__file__), 'СПИСОК_ЛИТЕРАТУРЫ_ОЧИЩЕННЫЙ.txt')
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("СПИСОК ЛИТЕРАТУРЫ\n\n")
    for i, (num, text) in enumerate(used_literature, 1):
        f.write(f"{i}. {text}\n")

print(f"\n✓ Очищенный список литературы сохранен в: {output_file}")
print(f"  Использовано источников: {len(used_literature)}")
print(f"  Удалено источников: {len(literature_items) - len(used_literature)}")

# Выводим список использованных источников
print("\nИспользованные источники:")
for i, (num, text) in enumerate(used_literature, 1):
    print(f"  {i}. {text}")














