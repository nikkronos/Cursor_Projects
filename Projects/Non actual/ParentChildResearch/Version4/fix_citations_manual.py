# -*- coding: utf-8 -*-
"""
Скрипт для замены перечислений источников на цитирование с указанием авторов
Задачи Д, Ж, З, Н, О, П
"""
from pathlib import Path
from docx import Document

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

def format_citation_with_authors(ref_numbers):
    """Форматирует цитату с указанием авторов и номеров"""
    authors_list = []
    for num in ref_numbers:
        if num in AUTHORS_MAP:
            authors_list.append(f"{AUTHORS_MAP[num]}, {num}")
        else:
            authors_list.append(str(num))
    return "[" + "; ".join(authors_list) + "]"

def extract_ref_numbers(ref_str):
    """Извлекает номера источников из строки типа '[3; 31; 22]'"""
    import re
    numbers = re.findall(r'\d+', ref_str)
    return [int(n) for n in numbers]

def fix_citations_in_document():
    """Исправляет цитирование в документе"""
    v4 = Path(__file__).parent
    v7_file = v4 / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v7.docx"
    
    if not v7_file.exists():
        print(f"ERROR: {v7_file} not found")
        return False
    
    print("=" * 70)
    print("ЗАДАЧИ Д, Ж, З, Н, О, П: Замена перечислений на цитирование")
    print("=" * 70)
    
    doc = Document(str(v7_file))
    changes = []
    
    # Список мест, где нужно заменить перечисления на цитирование
    # На основе анализа текста
    
    replacements = [
        # Строка 66: [3; 31; 22]
        {
            "search": "[3; 31; 22]",
            "replace": format_citation_with_authors([3, 31, 22]),
            "desc": "Д: Строка 66 - добавлено цитирование"
        },
        # Строка 168: [22; 35] и [63; 64]
        {
            "search": "[22; 35]",
            "replace": format_citation_with_authors([22, 35]),
            "desc": "Ж: Строка 168 - добавлено цитирование [22; 35]"
        },
        {
            "search": "[63; 64]",
            "replace": format_citation_with_authors([63, 64]),
            "desc": "Ж: Строка 168 - добавлено цитирование [63; 64]"
        },
        # Строка 174: [20; 21] и [26; 42]
        {
            "search": "[20; 21]",
            "replace": format_citation_with_authors([20, 21]),
            "desc": "З: Строка 174 - добавлено цитирование [20; 21]"
        },
        {
            "search": "[26; 42]",
            "replace": format_citation_with_authors([26, 42]),
            "desc": "З: Строка 174 - добавлено цитирование [26; 42]"
        },
        # Строка 214: [3; 4] и [38]
        {
            "search": "[3; 4]",
            "replace": format_citation_with_authors([3, 4]),
            "desc": "Н: Строка 214 - добавлено цитирование [3; 4]"
        },
        {
            "search": "[38]",
            "replace": format_citation_with_authors([38]),
            "desc": "Н: Строка 214 - добавлено цитирование [38]"
        },
        # Строка 215: [20; 21; 26]
        {
            "search": "[20; 21; 26]",
            "replace": format_citation_with_authors([20, 21, 26]),
            "desc": "О: Строка 215 - добавлено цитирование [20; 21; 26]"
        },
        # Строка 218: [1; 2; 7; 9; 34; 41; 54] и [18; 27; 30; 48]
        {
            "search": "[1; 2; 7; 9; 34; 41; 54]",
            "replace": format_citation_with_authors([1, 2, 7, 9, 34, 41, 54]),
            "desc": "П: Строка 218 - добавлено цитирование [1; 2; 7; 9; 34; 41; 54]"
        },
        {
            "search": "[18; 27; 30; 48]",
            "replace": format_citation_with_authors([18, 27, 30, 48]),
            "desc": "П: Строка 218 - добавлено цитирование [18; 27; 30; 48]"
        },
        # Строка 216: [52; 60]
        {
            "search": "[52; 60]",
            "replace": format_citation_with_authors([52, 60]),
            "desc": "П: Строка 216 - добавлено цитирование [52; 60]"
        },
    ]
    
    for para in doc.paragraphs:
        text = para.text
        original_text = text
        for repl in replacements:
            # Проверяем, что исходная ссылка есть в тексте
            if repl["search"] in text:
                # Проверяем, что замена ещё не выполнена
                # Ищем по части фамилии первого автора из замены
                first_author = repl["replace"].split(",")[0].replace("[", "").strip()
                if first_author not in text:
                    para.text = text.replace(repl["search"], repl["replace"])
                    changes.append(repl["desc"])
                    print(f"  ✓ {repl['desc']}")
                    text = para.text  # Обновляем текст для следующей замены
                else:
                    print(f"  ⚠ Пропущено (уже исправлено): {repl['desc']}")
    
    print(f"\nВнесено изменений: {len(changes)}")
    
    # Сохраняем
    doc.save(str(v7_file))
    print(f"\n✓ Документ обновлён: {v7_file.name}")
    
    return True

if __name__ == '__main__':
    fix_citations_in_document()

