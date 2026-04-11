# -*- coding: utf-8 -*-
"""Извлекает текст из исходника для поиска фамилий"""
from pathlib import Path
from docx import Document

v4 = Path(__file__).parent
source_file = v4 / "ВКР_ИСХОДНИК.docx"

if source_file.exists():
    doc = Document(str(source_file))
    text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    with open(v4 / "source_text.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print(f"✓ Извлечён текст из исходника ({len(text)} символов)")
else:
    print(f"✗ Файл не найден: {source_file}")





