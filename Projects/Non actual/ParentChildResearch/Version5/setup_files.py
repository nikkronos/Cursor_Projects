# -*- coding: utf-8 -*-
"""
Скрипт для копирования необходимых файлов в Version5
"""
import shutil
from pathlib import Path

def setup_version5():
    """Копирует необходимые файлы в Version5"""
    base = Path(__file__).parent.parent
    version4 = base / "Version4"
    version5 = base / "Version5"
    
    # Создаем Version5 если не существует
    version5.mkdir(exist_ok=True)
    
    # Копируем документ v7
    v7_source = version4 / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v7.docx"
    v7_dest = version5 / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v7.docx"
    
    if v7_source.exists():
        shutil.copy2(v7_source, v7_dest)
        print(f"✓ Скопирован: {v7_dest.name}")
    else:
        print(f"✗ Не найден: {v7_source}")
    
    # Копируем список литературы
    lit_source = version4 / "СПИСОК_ЛИТЕРАТУРЫ_ФИНАЛЬНЫЙ.md"
    lit_dest = version5 / "СПИСОК_ЛИТЕРАТУРЫ_ФИНАЛЬНЫЙ.md"
    
    if lit_source.exists():
        shutil.copy2(lit_source, lit_dest)
        print(f"✓ Скопирован: {lit_dest.name}")
    else:
        print(f"✗ Не найден: {lit_source}")
    
    print(f"\n✓ Настройка Version5 завершена")

if __name__ == '__main__':
    setup_version5()




