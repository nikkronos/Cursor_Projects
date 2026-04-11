# -*- coding: utf-8 -*-
"""
Скрипт для извлечения списка литературы из документа v20
"""
from pathlib import Path
from docx import Document
import re

def extract_literature_from_doc(doc_path: Path):
    """
    Извлекает список литературы из документа Word.
    """
    print(f"📖 Открываю документ: {doc_path.name}")
    doc = Document(str(doc_path))
    
    # Ищем начало списка литературы
    literature_start_idx = -1
    literature_items = []
    
    print("\n🔍 Ищу раздел 'Список литературы'...")
    
    for idx, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        text_lower = text.lower()
        
        # Ищем начало списка литературы
        if literature_start_idx == -1:
            if any(keyword in text_lower for keyword in ['список литературы', 'литература', 'библиографический список']):
                literature_start_idx = idx
                print(f"  ✓ Найдено начало списка литературы на параграфе {idx + 1}: '{text[:50]}...'")
                continue
        else:
            # После нахождения начала, собираем элементы списка
            # Элементы списка начинаются с номера: "1. ", "10. " и т.д.
            match = re.match(r'^(\d+)\.\s+(.+)', text)
            if match:
                number = int(match.group(1))
                entry = match.group(2).strip()
                literature_items.append({
                    'number': number,
                    'entry': entry,
                    'para_idx': idx
                })
            elif text and not re.match(r'^\d+\.', text):
                # Если встретили текст, который не является элементом списка,
                # и он не пустой, возможно это конец списка
                # Но сначала проверим, не является ли это продолжением предыдущего элемента
                if literature_items and not text.startswith(('—', '/', '//', 'М.:', 'СПб.:', 'Ростов')):
                    # Возможно, это новый раздел
                    print(f"  ⚠ Возможно, конец списка на параграфе {idx + 1}: '{text[:50]}...'")
                    break
    
    print(f"\n📚 Найдено источников в списке литературы: {len(literature_items)}")
    
    if literature_items:
        print("\n  Первые 5 источников:")
        for item in literature_items[:5]:
            print(f"    {item['number']}. {item['entry'][:60]}...")
        
        if len(literature_items) > 5:
            print(f"    ... и ещё {len(literature_items) - 5} источников")
    
    return literature_items, literature_start_idx

def save_literature_to_md(literature_items, output_path: Path):
    """
    Сохраняет список литературы в .md файл для дальнейшей работы.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# СПИСОК ЛИТЕРАТУРЫ\n\n")
        f.write("*Извлечено из документа v20*\n\n")
        f.write(f"*Всего источников: {len(literature_items)}*\n\n")
        
        for item in literature_items:
            f.write(f"{item['number']}. {item['entry']}\n\n")
    
    print(f"\n💾 Список литературы сохранён в: {output_path.name}")

if __name__ == '__main__':
    version10 = Path(__file__).parent
    version6 = version10.parent / "Version6"
    
    # Путь к документу v20
    v20_path = version6 / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v20.docx"
    
    if not v20_path.exists():
        print(f"❌ ОШИБКА: Документ не найден: {v20_path}")
        print(f"   Проверьте путь: {v20_path.absolute()}")
    else:
        literature_items, start_idx = extract_literature_from_doc(v20_path)
        
        if literature_items:
            # Сохраняем в .md файл для дальнейшей работы
            output_path = version10 / "СПИСОК_ЛИТЕРАТУРЫ_v20_extracted.md"
            save_literature_to_md(literature_items, output_path)
        else:
            print("\n❌ Список литературы не найден в документе!")
            print("   Проверьте, есть ли раздел 'Список литературы' в конце документа.")
