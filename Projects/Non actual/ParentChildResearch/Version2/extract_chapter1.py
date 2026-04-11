"""Извлечение текста и ссылок из Главы I"""
import os
import sys
import re

# Добавляем текущую директорию в путь
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    from docx import Document
except ImportError:
    print("Ошибка: библиотека python-docx не установлена")
    print("Установите: pip install python-docx")
    sys.exit(1)

# Путь к файлу Главы I
chapter1_file = os.path.join(script_dir, 'A1', 'ВКР Бакалавриат_Ворошилова.docx')

print("Извлечение текста из Главы I...")

try:
    doc = Document(chapter1_file)
    
    # Извлекаем весь текст
    full_text = []
    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text)
    
    # Объединяем в один текст
    chapter1_text = '\n'.join(full_text)
    
    # Сохраняем в файл
    output_file = os.path.join(os.path.dirname(__file__), 'ГЛАВА_I.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(chapter1_text)
    
    print(f"✓ Текст сохранен в: {output_file}")
    print(f"  Количество символов: {len(chapter1_text)}")
    
    # Ищем все ссылки вида [N] или [N; M]
    references = re.findall(r'\[(\d+(?:;\s*\d+)*)\]', chapter1_text)
    
    # Собираем уникальные номера источников
    all_refs = set()
    for ref in references:
        numbers = [int(n.strip()) for n in ref.split(';')]
        all_refs.update(numbers)
    
    print(f"\nНайдено ссылок в тексте: {len(references)}")
    print(f"Уникальных номеров источников: {len(all_refs)}")
    print(f"Номера источников: {sorted(all_refs)}")
    
    # Сохраняем список ссылок
    refs_file = os.path.join(os.path.dirname(__file__), 'ССЫЛКИ_ГЛАВА_I.txt')
    with open(refs_file, 'w', encoding='utf-8') as f:
        f.write("Ссылки из Главы I:\n")
        f.write("=" * 50 + "\n\n")
        for ref in sorted(all_refs):
            f.write(f"{ref}\n")
    
    print(f"✓ Список ссылок сохранен в: {refs_file}")
    
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()

