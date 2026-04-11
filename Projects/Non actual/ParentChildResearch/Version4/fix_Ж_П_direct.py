# -*- coding: utf-8 -*-
"""
Прямое исправление проблем Ж и П - более надёжная версия
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

def fix_Ж_П_direct():
    """Прямое исправление проблем Ж и П"""
    v4 = Path(__file__).parent
    v7_file = v4 / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v7.docx"
    
    if not v7_file.exists():
        print(f"ERROR: {v7_file} not found")
        return False
    
    print("=" * 70)
    print("ПРЯМОЕ ИСПРАВЛЕНИЕ ПРОБЛЕМ Ж И П")
    print("=" * 70)
    
    doc = Document(str(v7_file))
    changes = []
    
    # Проходим по всем параграфам
    for para_idx, para in enumerate(doc.paragraphs):
        text = para.text
        original_text = text
        
        # Ж. Ищем [22; 35]
        if "[22; 35]" in text or "[22;35]" in text:
            # Проверяем, не исправлено ли уже
            if "Дружинин, 22" not in text and "Леонтьев А.Н., 35" not in text:
                # Заменяем все варианты
                text = text.replace("[22; 35]", format_citation([22, 35]))
                text = text.replace("[22;35]", format_citation([22, 35]))
                if text != original_text:
                    para.text = text
                    changes.append(f"Ж: Параграф {para_idx+1} - исправлено [22; 35]")
                    print(f"  ✓ {changes[-1]}")
                    original_text = text
        
        # Ж. Ищем [63; 64]
        if "[63; 64]" in text or "[63;64]" in text:
            if "Шнейдер, 63" not in text and "Эйдемиллер, Юстицкис, 64" not in text:
                text = text.replace("[63; 64]", format_citation([63, 64]))
                text = text.replace("[63;64]", format_citation([63, 64]))
                if text != original_text:
                    para.text = text
                    changes.append(f"Ж: Параграф {para_idx+1} - исправлено [63; 64]")
                    print(f"  ✓ {changes[-1]}")
                    original_text = text
        
        # П. Ищем [1; 2; 7; 9; 34; 41; 54]
        if "[1; 2; 7; 9; 34; 41; 54]" in text or "[1;2;7;9;34;41;54]" in text:
            if "Абульханова-Славская, 1" not in text:
                text = text.replace("[1; 2; 7; 9; 34; 41; 54]", format_citation([1, 2, 7, 9, 34, 41, 54]))
                text = text.replace("[1;2;7;9;34;41;54]", format_citation([1, 2, 7, 9, 34, 41, 54]))
                if text != original_text:
                    para.text = text
                    changes.append(f"П: Параграф {para_idx+1} - исправлено [1; 2; 7; 9; 34; 41; 54]")
                    print(f"  ✓ {changes[-1]}")
                    original_text = text
        
        # П. Ищем [18; 27; 30; 48]
        if "[18; 27; 30; 48]" in text or "[18;27;30;48]" in text:
            if "Гинзбург, 18" not in text:
                text = text.replace("[18; 27; 30; 48]", format_citation([18, 27, 30, 48]))
                text = text.replace("[18;27;30;48]", format_citation([18, 27, 30, 48]))
                if text != original_text:
                    para.text = text
                    changes.append(f"П: Параграф {para_idx+1} - исправлено [18; 27; 30; 48]")
                    print(f"  ✓ {changes[-1]}")
    
    print(f"\nВнесено изменений: {len(changes)}")
    
    if len(changes) == 0:
        print("\n⚠ Изменения не найдены. Возможные причины:")
        print("  1. Уже исправлено ранее")
        print("  2. Формат ссылок отличается от ожидаемого")
        print("  3. Текст находится в таблице, а не в параграфе")
        
        # Показываем примеры того, что ищем
        print("\nИщем следующие паттерны:")
        print("  - [22; 35] или [22;35]")
        print("  - [63; 64] или [63;64]")
        print("  - [1; 2; 7; 9; 34; 41; 54]")
        print("  - [18; 27; 30; 48]")
    
    # Сохраняем
    doc.save(str(v7_file))
    print(f"\n✓ Документ сохранён: {v7_file.name}")
    
    return True

if __name__ == '__main__':
    fix_Ж_П_direct()





