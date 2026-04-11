# -*- coding: utf-8 -*-
from pathlib import Path
import shutil

base = Path(__file__).parent.parent
v4 = Path(__file__).parent

# Копируем файлы
v6_src = base / "Version3" / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v6.docx"
src_doc = base / "Version2" / "A1" / "ВКР Бакалавриат_Ворошилова.docx"

if v6_src.exists():
    shutil.copy2(v6_src, v4 / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v6.docx")
    print("OK: v6 copied")

if src_doc.exists():
    shutil.copy2(src_doc, v4 / "ВКР_ИСХОДНИК.docx")
    print("OK: source copied")

# Извлекаем текст
try:
    from docx import Document
    
    if (v4 / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v6.docx").exists():
        doc = Document(str(v4 / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v6.docx"))
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        with open(v4 / "v6_text.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print(f"OK: extracted {len(text)} chars")
        
except ImportError:
    print("Need: pip install python-docx")





