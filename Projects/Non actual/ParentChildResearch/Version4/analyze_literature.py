# -*- coding: utf-8 -*-
"""
Анализ использования источников в тексте и формирование актуального списка литературы
"""
from pathlib import Path
import re

def extract_all_references(text):
    """Извлекает все ссылки на источники из текста"""
    # Паттерн для ссылок типа [1], [2, 3], [5; 64], [3; 31; 22]
    pattern = r'\[(\d+(?:[;\s,]*\d+)*)\]'
    matches = re.finditer(pattern, text)
    
    all_refs = set()
    for match in matches:
        ref_str = match.group(1)
        # Извлекаем все числа из ссылки
        numbers = re.findall(r'\d+', ref_str)
        all_refs.update([int(n) for n in numbers])
    
    return sorted(all_refs)

def load_literature_list():
    """Загружает список литературы"""
    v2 = Path(__file__).parent.parent / "Version2"
    lit_file = v2 / "СПИСОК_ЛИТЕРАТУРЫ_50_ИСТОЧНИКОВ_ГОСТ.md"
    
    if not lit_file.exists():
        return {}
    
    literature = {}
    with open(lit_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Парсим список литературы
    lines = content.split('\n')
    current_num = None
    current_text = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Проверяем, начинается ли строка с номера
        match = re.match(r'^(\d+)\.\s*(.+)', line)
        if match:
            # Сохраняем предыдущий источник
            if current_num is not None:
                literature[current_num] = ' '.join(current_text).strip()
            
            # Начинаем новый источник
            current_num = int(match.group(1))
            current_text = [match.group(2)]
        elif current_num is not None:
            current_text.append(line)
    
    # Сохраняем последний источник
    if current_num is not None:
        literature[current_num] = ' '.join(current_text).strip()
    
    return literature

def analyze_literature_usage():
    """Анализирует использование источников и формирует актуальный список"""
    v4 = Path(__file__).parent
    
    # Читаем текст документа
    text_file = v4 / "v6_text.txt"
    if not text_file.exists():
        print(f"ERROR: {text_file} not found")
        return False
    
    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("Анализ использования источников в тексте...")
    print("=" * 70)
    
    # Извлекаем все ссылки
    used_refs = extract_all_references(text)
    
    print(f"\nНайдено уникальных номеров источников в тексте: {len(used_refs)}")
    print(f"Диапазон: {min(used_refs) if used_refs else 0} - {max(used_refs) if used_refs else 0}")
    print(f"\nИспользуемые источники: {used_refs}")
    
    # Загружаем список литературы
    literature = load_literature_list()
    
    print(f"\nЗагружено источников из списка литературы: {len(literature)}")
    
    # Формируем актуальный список
    actual_literature = {}
    missing_refs = []
    
    for ref_num in used_refs:
        if ref_num in literature:
            actual_literature[ref_num] = literature[ref_num]
        else:
            missing_refs.append(ref_num)
    
    # Находим источники в списке, которые не используются
    unused_refs = [num for num in literature.keys() if num not in used_refs]
    
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ АНАЛИЗА")
    print("=" * 70)
    
    print(f"\n✓ Используется в тексте: {len(used_refs)} источников")
    print(f"✓ Найдено в списке литературы: {len(actual_literature)} источников")
    
    if missing_refs:
        print(f"\n⚠ Источники, используемые в тексте, но отсутствующие в списке: {missing_refs}")
    
    if unused_refs:
        print(f"\n⚠ Источники в списке литературы, но не используемые в тексте: {unused_refs}")
        print(f"   Количество: {len(unused_refs)}")
    
    # Сохраняем актуальный список литературы
    output_file = v4 / "СПИСОК_ЛИТЕРАТУРЫ_АКТУАЛЬНЫЙ.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# СПИСОК ЛИТЕРАТУРЫ (актуальный)\n\n")
        f.write(f"*Сформирован на основе реального использования в тексте*\n\n")
        f.write(f"*Всего источников в тексте: {len(used_refs)}*\n")
        f.write(f"*Найдено в списке: {len(actual_literature)}*\n\n")
        
        # Сортируем по номерам
        for ref_num in sorted(actual_literature.keys()):
            f.write(f"{ref_num}. {actual_literature[ref_num]}\n\n")
        
        if missing_refs:
            f.write("\n\n---\n\n")
            f.write("## ИСТОЧНИКИ, ИСПОЛЬЗУЕМЫЕ В ТЕКСТЕ, НО ОТСУТСТВУЮЩИЕ В СПИСКЕ:\n\n")
            for ref_num in missing_refs:
                f.write(f"[{ref_num}] - требуется добавить в список литературы\n")
    
    print(f"\n✓ Актуальный список литературы сохранён: {output_file.name}")
    
    # Проверяем, укладываемся ли в 50 источников
    total_actual = len(actual_literature) + len(missing_refs)
    print(f"\n{'=' * 70}")
    print(f"ИТОГО ИСТОЧНИКОВ: {total_actual}")
    if total_actual <= 50:
        print(f"✓ Укладываемся в 50 источников (осталось {50 - total_actual})")
    else:
        print(f"⚠ Превышено на {total_actual - 50} источников")
    print(f"{'=' * 70}")
    
    return True

if __name__ == '__main__':
    analyze_literature_usage()





