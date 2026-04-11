# -*- coding: utf-8 -*-
"""
Скрипт для замены перечислений источников на цитирование с указанием авторов
"""
from pathlib import Path
from docx import Document
import re

# Словарь соответствия номеров источников и авторов
AUTHORS_MAP = {
    1: "Абульханова-Славская",
    2: "Адлер",
    3: "Ананьев",
    4: "Ананьев",
    5: "Андреева",
    6: "Асмолов",
    7: "Байярд",
    8: "Бендас",
    9: "Марковская",
    10: "Голланд",
    11: "Резапкина",
    12: "Божович",
    13: "Сидоренко",
    14: "Наследов",
    15: "Гласс, Стенли",
    16: "Выготский",
    17: "Гаврилова",
    18: "Гинзбург",
    19: "Головаха",
    20: "Деркач, Зазыкин",
    21: "Дружилов",
    22: "Дружинин",
    23: "Дубровина",
    24: "Журавлев, Купрейченко",
    25: "Зеер",
    26: "Иванников",
    27: "Кабардова",
    28: "Карпова, Артемьева",
    29: "Кле",
    30: "Климов",
    31: "Кон",
    32: "Кривцова",
    33: "Кулагина, Колюцкий",
    34: "Леви",
    35: "Леонтьев А.Н.",
    36: "Леонтьев Д.А.",
    37: "Лисина",
    38: "Ломов",
    39: "Маркова",
    40: "Маслоу",
    41: "Матейчек",
    42: "Мерлин",
    43: "Митина",
    44: "Мухина",
    45: "Носкова",
    46: "Осорина",
    47: "Петровский",
    48: "Поваренков",
    49: "Прихожан, Толстых",
    50: "Пряжников",
    51: "Ремшмидт",
    52: "Роджерс",
    53: "Сапогова",
    54: "Сатир",
    55: "Слободчиков, Исаев",
    56: "Толочек",
    57: "Фельдштейн",
    58: "Фельдштейн",
    59: "Фонарев",
    60: "Франкл",
    61: "Фромм",
    62: "Цукерман, Мастеров",
    63: "Шнейдер",
    64: "Эйдемиллер, Юстицкис",
    65: "Ядов"
}

def format_citation(ref_numbers):
    """Форматирует цитату с указанием авторов"""
    authors_list = []
    for num in ref_numbers:
        if num in AUTHORS_MAP:
            authors_list.append(f"{AUTHORS_MAP[num]}, {num}")
        else:
            authors_list.append(str(num))
    return "[" + "; ".join(authors_list) + "]"

def replace_simple_citations(text):
    """Заменяет простые перечисления на цитирование с авторами"""
    # Паттерн для ссылок типа [3; 31; 22] или [22; 35]
    pattern = r'\[(\d+(?:\s*;\s*\d+)+)\]'
    
    def replace_match(match):
        ref_str = match.group(1)
        ref_numbers = [int(x.strip()) for x in ref_str.split(';')]
        return format_citation(ref_numbers)
    
    return re.sub(pattern, replace_match, text)

def fix_citations_in_document():
    """Исправляет цитирование в документе"""
    v4 = Path(__file__).parent
    v6_file = v4 / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v6.docx"
    
    if not v6_file.exists():
        print(f"ERROR: {v6_file} not found")
        return False
    
    print("Читаю документ для исправления цитирования...")
    doc = Document(str(v6_file))
    
    changes = []
    
    # Список мест, где нужно заменить перечисления на цитирование
    # (из задач Д, Ж, З, Н, О, П)
    
    for para in doc.paragraphs:
        original_text = para.text
        
        # Заменяем простые перечисления
        new_text = replace_simple_citations(original_text)
        
        if new_text != original_text:
            para.text = new_text
            changes.append(f"Исправлено цитирование: {original_text[:50]}...")
    
    print(f"Внесено изменений в цитирование: {len(changes)}")
    
    # Сохраняем
    output_file = v4 / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v7_citations.docx"
    doc.save(str(output_file))
    print(f"Сохранено: {output_file.name}")
    
    return True

if __name__ == '__main__':
    fix_citations_in_document()





