# -*- coding: utf-8 -*-
import shutil
import os
from pathlib import Path

# Получаем абсолютные пути
script_dir = Path(__file__).parent
parent_dir = script_dir.parent
version5 = parent_dir / "Version5"
version6 = script_dir

files = [
    "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v9.docx",
    "СПИСОК_ЛИТЕРАТУРЫ_ФИНАЛЬНЫЙ.md",
    "requirements.txt"
]

for f in files:
    src = version5 / f
    dst = version6 / f
    if src.exists():
        shutil.copy2(str(src), str(dst))
        print(f"Copied: {f}")
    else:
        print(f"Not found: {src}")

print("Done!")



