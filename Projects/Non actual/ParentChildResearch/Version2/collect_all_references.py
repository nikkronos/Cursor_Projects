"""Сбор всех ссылок из обеих глав и создание расширенного списка литературы"""
import os
import re
import sys

# Добавляем текущую директорию в путь
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

print("=" * 60)
print("СБОР ВСЕХ ССЫЛОК И СОЗДАНИЕ РАСШИРЕННОГО СПИСКА ЛИТЕРАТУРЫ")
print("=" * 60)

# 1. Извлекаем ссылки из Главы II
print("\n1. Анализ Главы II...")
chapter2_file = os.path.join(script_dir, 'ГЛАВА_II.md')
chapter2_refs = set()

if os.path.exists(chapter2_file):
    with open(chapter2_file, 'r', encoding='utf-8') as f:
        chapter2_text = f.read()
    
    # Ищем ссылки вида [N] или [N; M]
    refs = re.findall(r'\[(\d+(?:;\s*\d+)*)\]', chapter2_text)
    for ref in refs:
        numbers = [int(n.strip()) for n in ref.split(';')]
        chapter2_refs.update(numbers)
    
    print(f"   Найдено ссылок в Главе II: {len(refs)}")
    print(f"   Уникальных номеров: {len(chapter2_refs)}")
    print(f"   Номера: {sorted(chapter2_refs)}")
else:
    print("   ⚠ Файл Главы II не найден")

# 2. Пытаемся извлечь ссылки из Word документа Главы I
print("\n2. Анализ Главы I (Word документ)...")
chapter1_docx = os.path.join(script_dir, 'A1', 'ВКР Бакалавриат_Ворошилова.docx')
chapter1_refs = set()

try:
    from docx import Document
    
    if os.path.exists(chapter1_docx):
        doc = Document(chapter1_docx)
        chapter1_text = '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
        
        # Ищем ссылки
        refs = re.findall(r'\[(\d+(?:;\s*\d+)*)\]', chapter1_text)
        for ref in refs:
            numbers = [int(n.strip()) for n in ref.split(';')]
            chapter1_refs.update(numbers)
        
        print(f"   Найдено ссылок в Главе I: {len(refs)}")
        print(f"   Уникальных номеров: {len(chapter1_refs)}")
        print(f"   Номера: {sorted(chapter1_refs)}")
        
        # Сохраняем текст Главы I
        chapter1_txt = os.path.join(script_dir, 'ГЛАВА_I_ИЗВЛЕЧЕННЫЙ.txt')
        with open(chapter1_txt, 'w', encoding='utf-8') as f:
            f.write(chapter1_text)
        print(f"   ✓ Текст сохранен в: {chapter1_txt}")
    else:
        print("   ⚠ Файл Главы I не найден")
        
except ImportError:
    print("   ⚠ Библиотека python-docx не установлена")
    print("   Установите: pip install python-docx")
except Exception as e:
    print(f"   ⚠ Ошибка при чтении Word документа: {e}")

# 3. Объединяем все ссылки
all_refs = chapter1_refs.union(chapter2_refs)
print(f"\n3. Объединенные ссылки из обеих глав:")
print(f"   Всего уникальных номеров: {len(all_refs)}")
print(f"   Номера: {sorted(all_refs)}")

# 4. Читаем полный список литературы
print("\n4. Чтение полного списка литературы...")
lit_file = os.path.join(script_dir, 'A1', '1. Абульханова-Славская К.А. Страте.txt')
all_literature = []

if os.path.exists(lit_file):
    with open(lit_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Разбиваем на строки и нумеруем
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    for i, line in enumerate(lines, 1):
        all_literature.append((i, line))
    
    print(f"   Всего источников в списке: {len(all_literature)}")
else:
    print("   ⚠ Файл со списком литературы не найден")

# 5. Создаем список использованных источников
print("\n5. Формирование списка использованных источников...")
used_sources = []
for num, text in all_literature:
    if num in all_refs:
        used_sources.append((num, text))

print(f"   Использовано источников из списка: {len(used_sources)}")

# 6. Сохраняем результаты
output_file = os.path.join(script_dir, 'ИСПОЛЬЗОВАННЫЕ_ИСТОЧНИКИ.txt')
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("ИСПОЛЬЗОВАННЫЕ ИСТОЧНИКИ ИЗ ОБЕИХ ГЛАВ\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Глава I: {sorted(chapter1_refs)}\n")
    f.write(f"Глава II: {sorted(chapter2_refs)}\n")
    f.write(f"Всего уникальных: {len(all_refs)}\n\n")
    f.write("Список источников:\n")
    f.write("-" * 60 + "\n")
    for num, text in sorted(used_sources, key=lambda x: x[0]):
        f.write(f"{num}. {text}\n")

print(f"   ✓ Результаты сохранены в: {output_file}")

# 7. Показываем, какие источники нужно добавить
print("\n6. Анализ недостающих источников...")
print(f"   Использовано: {len(all_refs)}")
print(f"   Нужно: 50")
print(f"   Не хватает: {max(0, 50 - len(all_refs))}")

print("\n" + "=" * 60)
print("АНАЛИЗ ЗАВЕРШЕН")
print("=" * 60)












