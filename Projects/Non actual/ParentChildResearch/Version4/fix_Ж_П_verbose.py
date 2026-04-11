# -*- coding: utf-8 -*-
"""
Исправление Ж и П с подробным выводом того, что найдено
"""
from pathlib import Path
from docx import Document

AUTHORS_MAP = {
    1: "Абульханова-Славская",
    2: "Адлер",
    7: "Байярд",
    9: "Марковская",
    18: "Гинзбург",
    22: "Дружинин",
    27: "Кабардова",
    30: "Климов",
    34: "Леви",
    35: "Леонтьев А.Н.",
    41: "Матейчек",
    48: "Поваренков",
    54: "Сатир",
    63: "Шнейдер",
    64: "Эйдемиллер, Юстицкис"
}

def format_citation(ref_numbers):
    """Форматирует цитату с указанием авторов и номеров"""
    authors_list = []
    for num in ref_numbers:
        if num in AUTHORS_MAP:
            authors_list.append(f"{AUTHORS_MAP[num]}, {num}")
        else:
            authors_list.append(str(num))
    return "[" + "; ".join(authors_list) + "]"

def fix_Ж_П_verbose():
    """Исправление с подробным выводом"""
    v4 = Path(__file__).parent
    v7_file = v4 / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v7.docx"
    
    if not v7_file.exists():
        print(f"ERROR: {v7_file} not found")
        return False
    
    print("=" * 70)
    print("ИСПРАВЛЕНИЕ Ж И П (подробный режим)")
    print("=" * 70)
    
    doc = Document(str(v7_file))
    changes = []
    
    # Ищем все параграфы с проблемными паттернами
    print("\nШАГ 1: Поиск проблемных мест...")
    
    for para_idx, para in enumerate(doc.paragraphs):
        text = para.text
        
        # Ж. [22; 35]
        if "[22; 35]" in text:
            print(f"\n  Найдено [22; 35] в параграфе {para_idx+1}:")
            print(f"    Текст: {text[:150]}...")
            if "Дружинин, 22" in text or "Леонтьев А.Н., 35" in text:
                print("    ✓ Уже исправлено")
            else:
                print("    ✗ Требует исправления")
                new_citation = format_citation([22, 35])
                print(f"    Заменяем на: {new_citation}")
                para.text = text.replace("[22; 35]", new_citation)
                changes.append(f"Ж: Параграф {para_idx+1} - [22; 35]")
        
        # Ж. [63; 64]
        if "[63; 64]" in text:
            print(f"\n  Найдено [63; 64] в параграфе {para_idx+1}:")
            print(f"    Текст: {text[:150]}...")
            if "Шнейдер, 63" in text or "Эйдемиллер, Юстицкис, 64" in text:
                print("    ✓ Уже исправлено")
            else:
                print("    ✗ Требует исправления")
                new_citation = format_citation([63, 64])
                print(f"    Заменяем на: {new_citation}")
                para.text = text.replace("[63; 64]", new_citation)
                changes.append(f"Ж: Параграф {para_idx+1} - [63; 64]")
        
        # П. [1; 2; 7; 9; 34; 41; 54]
        if "[1; 2; 7; 9; 34; 41; 54]" in text:
            print(f"\n  Найдено [1; 2; 7; 9; 34; 41; 54] в параграфе {para_idx+1}:")
            print(f"    Текст: {text[:150]}...")
            if "Абульханова-Славская, 1" in text:
                print("    ✓ Уже исправлено")
            else:
                print("    ✗ Требует исправления")
                new_citation = format_citation([1, 2, 7, 9, 34, 41, 54])
                print(f"    Заменяем на: {new_citation}")
                para.text = text.replace("[1; 2; 7; 9; 34; 41; 54]", new_citation)
                changes.append(f"П: Параграф {para_idx+1} - [1; 2; 7; 9; 34; 41; 54]")
        
        # П. [18; 27; 30; 48]
        if "[18; 27; 30; 48]" in text:
            print(f"\n  Найдено [18; 27; 30; 48] в параграфе {para_idx+1}:")
            print(f"    Текст: {text[:150]}...")
            if "Гинзбург, 18" in text:
                print("    ✓ Уже исправлено")
            else:
                print("    ✗ Требует исправления")
                new_citation = format_citation([18, 27, 30, 48])
                print(f"    Заменяем на: {new_citation}")
                para.text = text.replace("[18; 27; 30; 48]", new_citation)
                changes.append(f"П: Параграф {para_idx+1} - [18; 27; 30; 48]")
    
    print("\n" + "=" * 70)
    print(f"ИТОГО ВНЕСЕНО ИЗМЕНЕНИЙ: {len(changes)}")
    print("=" * 70)
    
    if changes:
        for change in changes:
            print(f"  ✓ {change}")
    else:
        print("\n⚠ Изменения не внесены.")
        print("Возможно, паттерны не найдены или уже исправлены.")
    
    # Сохраняем
    doc.save(str(v7_file))
    print(f"\n✓ Документ сохранён: {v7_file.name}")
    
    return True

if __name__ == '__main__':
    fix_Ж_П_verbose()





