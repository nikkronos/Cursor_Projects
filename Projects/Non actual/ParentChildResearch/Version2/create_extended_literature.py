"""Создание расширенного списка литературы (50 источников)"""
import os
import re

script_dir = os.path.dirname(os.path.abspath(__file__))

# Известные ссылки из Главы II
chapter2_refs = {5, 12, 18, 22, 30, 35, 52, 60}

# Читаем полный список литературы
lit_file = os.path.join(script_dir, 'A1', '1. Абульханова-Славская К.А. Страте.txt')
with open(lit_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Разбиваем на источники
sources = []
for line in content.split('\n'):
    line = line.strip()
    if line:
        # Ищем номер источника в начале строки
        match = re.match(r'^(\d+)\.\s+(.+)', line)
        if match:
            num = int(match.group(1))
            text = match.group(2).strip()
            sources.append((num, text))

print(f"Всего источников в списке: {len(sources)}")
print(f"Использовано в Главе II: {sorted(chapter2_refs)}")

# Создаем расширенный список с добавлением источников на методики и статистику
extended_sources = []

# 1. Источники из Главы II (уже используются)
for num in sorted(chapter2_refs):
    if num <= len(sources):
        extended_sources.append((num, sources[num-1][1]))

# 2. Добавляем источники на методики (66-68)
extended_sources.append((66, "Марковская И.М. Опросник взаимодействия родитель-ребенок (ВРР)"))
extended_sources.append((67, "Holland J.L. Making vocational choices: A theory of vocational personalities and work environments"))
extended_sources.append((68, "Резапкина Г.В. Методика «Мотивы выбора профессии»"))

# 3. Добавляем источники на статистические методы (69-71)
extended_sources.append((69, "Спирмен Ч. Корреляция между признаками, измеренными в порядковой шкале"))
extended_sources.append((70, "Пирсон К. Математический вклад в теорию эволюции"))
extended_sources.append((71, "Сидоренко Е.В. Методы математической обработки в психологии"))

# 4. Добавляем дополнительные релевантные источники из списка
# Выбираем источники, которые логично добавить в текст
additional_refs = [1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 53, 54, 55, 56, 57, 58, 59, 61, 62, 63, 64, 65]

# Берем первые 42 источника из дополнительных, чтобы вместе с 8 из Главы II и 6 новых = 50
needed = 50 - len(extended_sources)  # Нужно еще источников
for num in additional_refs[:needed]:
    if num <= len(sources):
        extended_sources.append((num, sources[num-1][1]))

# Сортируем по номерам
extended_sources.sort(key=lambda x: x[0])

print(f"\nРасширенный список: {len(extended_sources)} источников")

# Сохраняем
output_file = os.path.join(script_dir, 'СПИСОК_ЛИТЕРАТУРЫ_50_ИСТОЧНИКОВ.txt')
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("СПИСОК ЛИТЕРАТУРЫ (50 источников)\n")
    f.write("=" * 60 + "\n\n")
    for i, (num, text) in enumerate(extended_sources, 1):
        f.write(f"{i}. {text}\n")

print(f"✓ Расширенный список сохранен в: {output_file}")

# Создаем маппинг старых номеров на новые
mapping = {}
for i, (old_num, text) in enumerate(extended_sources, 1):
    mapping[old_num] = i

print(f"\nМаппинг номеров:")
for old, new in sorted(mapping.items())[:10]:
    print(f"  Старый номер {old} -> Новый номер {new}")
print("  ...")

# Сохраняем маппинг
mapping_file = os.path.join(script_dir, 'МАППИНГ_НОМЕРОВ.txt')
with open(mapping_file, 'w', encoding='utf-8') as f:
    f.write("МАППИНГ СТАРЫХ НОМЕРОВ НА НОВЫЕ\n")
    f.write("=" * 60 + "\n\n")
    for old, new in sorted(mapping.items()):
        f.write(f"Старый {old:3d} -> Новый {new:3d}\n")

print(f"✓ Маппинг сохранен в: {mapping_file}")












