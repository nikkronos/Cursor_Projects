# -*- coding: utf-8 -*-
"""
Скрипт для копирования документа v20 из Version6 в Version10
"""
from pathlib import Path
import shutil

def copy_document():
    version10 = Path(__file__).parent
    version6 = version10.parent / "Version6"
    
    source = version6 / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v20.docx"
    destination = version10 / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v20.docx"
    
    if not source.exists():
        print(f"ERROR: Исходный документ не найден: {source}")
        return False
    
    if destination.exists():
        print(f"INFO: Документ уже существует: {destination}")
        response = input("Перезаписать? (y/n): ")
        if response.lower() != 'y':
            print("Отменено")
            return False
    
    shutil.copy2(source, destination)
    print(f"✓ Документ скопирован: {destination}")
    return True

if __name__ == '__main__':
    copy_document()
