# -*- coding: utf-8 -*-
"""Скрипт для копирования необходимых файлов в Version6"""
import shutil
from pathlib import Path

def setup_files():
    """Копирует необходимые файлы из Version5 в Version6"""
    base = Path(__file__).parent.parent
    version5 = base / "Version5"
    version6 = base / "Version6"
    
    version6.mkdir(exist_ok=True)
    
    files_to_copy = [
        "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v9.docx",
        "СПИСОК_ЛИТЕРАТУРЫ_ФИНАЛЬНЫЙ.md",
        "requirements.txt"
    ]
    
    for filename in files_to_copy:
        source = version5 / filename
        dest = version6 / filename
        
        if source.exists():
            shutil.copy2(source, dest)
            print(f"✓ Скопирован: {filename}")
        else:
            print(f"✗ Не найден: {source}")
    
    print("\n✓ Файлы скопированы в Version6")

if __name__ == '__main__':
    setup_files()



