#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для настройки Version4 и анализа документа v6
"""
import os
import shutil
from pathlib import Path

# Определяем пути
base_dir = Path(__file__).parent.parent
version4_dir = base_dir / "Version4"
version3_dir = base_dir / "Version3"
version2_dir = base_dir / "Version2"

# Создаём Version4 если ещё не создана
version4_dir.mkdir(exist_ok=True)

# Копируем файлы
files_to_copy = [
    (version3_dir / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v6.docx", version4_dir / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v6.docx"),
    (version2_dir / "A1" / "ВКР Бакалавриат_Ворошилова.docx", version4_dir / "ВКР_ИСХОДНИК.docx"),
]

for src, dst in files_to_copy:
    if src.exists():
        shutil.copy2(src, dst)
        print(f"✓ Скопирован: {src.name} -> {dst.name}")
    else:
        print(f"✗ Не найден: {src}")

print("\n✓ Настройка Version4 завершена!")





