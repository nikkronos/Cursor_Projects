# -*- coding: utf-8 -*-
"""
Скрипт для отладки - проверяем, что именно нужно исправить
"""
import re
from pathlib import Path
from docx import Document

def load_literature_list(literature_file):
    """Загружает список литературы из файла"""
    literature = {}
    with open(literature_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'^(\d+)\.\s+([^\n]+)'
    matches = re.finditer(pattern, content, re.MULTILINE)
    
    for match in matches:
        num = int(match.group(1))
        entry = match.group(2).strip()
        author_match = re.match(r'^([А-ЯЁ][а-яё]+(?:\-[А-ЯЁ][а-яё]+)?)', entry)
        if author_match:
            author = author_match.group(1)
        else:
            author_match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', entry)
            if author_match:
                author = author_match.group(1)
            else:
                author = None
        literature[num] = {
            'number': num,
            'entry': entry,
            'author': author
        }
    
    return literature

def find_all_citations(text):
    """Находит все ссылки на источники в тексте"""
    citations = []
    
    # Квадратные скобки с номерами
    pattern1 = r'\[(\d+(?:[,\s;]\s*\d+)*)\]'
    matches1 = re.finditer(pattern1, text)
    for match in matches1:
        numbers_str = match.group(1)
        numbers = []
        for num_str in re.split(r'[,\s;]+', numbers_str):
            if '-' in num_str:
                start, end = map(int, num_str.split('-'))
                numbers.extend(range(start, end + 1))
            else:
                numbers.append(int(num_str.strip()))
        citations.append({
            'type': 'square_brackets',
            'full_match': match.group(0),
            'numbers': numbers,
            'position': match.span()
        })
    
    # Круглые скобки с номерами
    pattern2 = r'\((\d+(?:[,\s;]\s*\d+)*)\)'
    matches2 = re.finditer(pattern2, text)
    for match in matches2:
        numbers_str = match.group(1)
        numbers = []
        for num_str in re.split(r'[,\s;]+', numbers_str):
            if '-' in num_str:
                start, end = map(int, num_str.split('-'))
                numbers.extend(range(start, end + 1))
            else:
                numbers.append(int(num_str.strip()))
        citations.append({
            'type': 'round_brackets_numbers',
            'full_match': match.group(0),
            'numbers': numbers,
            'position': match.span()
        })
    
    # Круглые скобки с фамилиями и номерами
    pattern3 = r'\(([А-ЯЁа-яё\s,\-]+?)\s+(\d+)\)'
    matches3 = re.finditer(pattern3, text)
    for match in matches3:
        names_str = match.group(1).strip()
        if 'вопрос' not in names_str.lower():  # Исключаем "(вопрос 12)"
            citations.append({
                'type': 'round_brackets_name_number',
                'full_match': match.group(0),
                'names': [n.strip() for n in names_str.split(',')],
                'number': int(match.group(2)),
                'position': match.span()
            })
    
    return citations

def main():
    version5 = Path(__file__).parent
    v7_path = version5 / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v7.docx"
    literature_path = version5 / "СПИСОК_ЛИТЕРАТУРЫ_ФИНАЛЬНЫЙ.md"
    
    if not v7_path.exists():
        print(f"ERROR: {v7_path} не найден")
        return
    
    # Загружаем документ
    doc = Document(str(v7_path))
    print("=" * 70)
    print("ПОИСК ПРОБЛЕМНЫХ МЕСТ В ДОКУМЕНТЕ v7")
    print("=" * 70)
    
    # Загружаем список литературы
    literature = load_literature_list(literature_path)
    max_source = max(literature.keys())
    min_source = min(literature.keys())
    
    print(f"Диапазон источников: {min_source}-{max_source}\n")
    
    problems_found = []
    page_4_paragraphs = []
    
    # Ищем проблемные места
    keywords = ['системный семейный подход', 'андреева', 'эдельмин', 'юскис', 'адлер', 
                'гинзбург', 'климов', 'прихожан', 'толстых']
    
    for para_idx, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if not text:
            continue
        
        text_lower = text.lower()
        is_page_4 = any(keyword in text_lower for keyword in keywords)
        
        # Ищем все ссылки
        citations = find_all_citations(text)
        
        for citation in citations:
            # Проверяем фамилии в скобках
            if citation['type'] == 'round_brackets_name_number':
                problems_found.append({
                    'para_idx': para_idx,
                    'type': 'name_in_brackets',
                    'text': text,
                    'citation': citation,
                    'is_page_4': is_page_4
                })
            
            # Проверяем неверные номера
            if 'numbers' in citation:
                for num in citation['numbers']:
                    if num < min_source or num > max_source:
                        problems_found.append({
                            'para_idx': para_idx,
                            'type': 'source_not_found',
                            'text': text,
                            'citation': citation,
                            'bad_number': num,
                            'is_page_4': is_page_4
                        })
            elif 'number' in citation:
                num = citation['number']
                if num < min_source or num > max_source:
                    problems_found.append({
                        'para_idx': para_idx,
                        'type': 'source_not_found',
                        'text': text,
                        'citation': citation,
                        'bad_number': num,
                        'is_page_4': is_page_4
                    })
        
        if is_page_4:
            page_4_paragraphs.append({
                'para_idx': para_idx,
                'text': text,
                'citations': citations
            })
    
    print(f"Найдено проблем: {len(problems_found)}")
    print(f"Найдено параграфов на странице 4: {len(page_4_paragraphs)}\n")
    
    # Показываем проблемы с фамилиями в скобках
    name_problems = [p for p in problems_found if p['type'] == 'name_in_brackets']
    print(f"{'='*70}")
    print(f"ПРОБЛЕМЫ С ФАМИЛИЯМИ В СКОБКАХ: {len(name_problems)}")
    print(f"{'='*70}")
    for i, problem in enumerate(name_problems[:10], 1):
        print(f"\n{i}. Параграф {problem['para_idx'] + 1} (страница 4: {problem['is_page_4']})")
        print(f"   Найдено: {problem['citation']['full_match']}")
        print(f"   Текст: {problem['text'][:200]}...")
    
    # Показываем проблемы с неверными номерами
    number_problems = [p for p in problems_found if p['type'] == 'source_not_found']
    print(f"\n{'='*70}")
    print(f"ПРОБЛЕМЫ С НЕВЕРНЫМИ НОМЕРАМИ: {len(number_problems)}")
    print(f"{'='*70}")
    for i, problem in enumerate(number_problems[:10], 1):
        print(f"\n{i}. Параграф {problem['para_idx'] + 1}")
        print(f"   Неверный номер: {problem.get('bad_number', 'N/A')}")
        print(f"   Найдено: {problem['citation']['full_match']}")
        print(f"   Текст: {problem['text'][:200]}...")
    
    # Показываем страницу 4
    print(f"\n{'='*70}")
    print(f"СТРАНИЦА 4 - ПАРАГРАФЫ С КЛЮЧЕВЫМИ СЛОВАМИ")
    print(f"{'='*70}")
    for i, para_data in enumerate(page_4_paragraphs[:5], 1):
        print(f"\n{i}. Параграф {para_data['para_idx'] + 1}:")
        print(f"   {para_data['text'][:300]}...")
        if para_data['citations']:
            print(f"   Найдено ссылок: {len(para_data['citations'])}")
            for cit in para_data['citations']:
                print(f"     - {cit['full_match']} ({cit['type']})")

if __name__ == '__main__':
    main()




