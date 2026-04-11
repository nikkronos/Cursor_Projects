# -*- coding: utf-8 -*-
"""Простой тест для проверки файлов"""
from pathlib import Path

v5 = Path(__file__).parent
v4 = v5.parent / "Version4"

print("Проверка файлов...")
print(f"Version5: {v5}")
print(f"Version4: {v4}")

# Проверяем документ v7
v7_v4 = v4 / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v7.docx"
v7_v5 = v5 / "ВКР_ПОЛНЫЙ_ДОКУМЕНТ_v7.docx"

print(f"\nДокумент v7:")
print(f"  В Version4: {v7_v4.exists()} - {v7_v4}")
if not v7_v5.exists() and v7_v4.exists():
    import shutil
    shutil.copy2(v7_v4, v7_v5)
    print(f"  ✓ Скопирован в Version5")
else:
    print(f"  В Version5: {v7_v5.exists()} - {v7_v5}")

# Проверяем список литературы
lit_v4 = v4 / "СПИСОК_ЛИТЕРАТУРЫ_ФИНАЛЬНЫЙ.md"
lit_v5 = v5 / "СПИСОК_ЛИТЕРАТУРЫ_ФИНАЛЬНЫЙ.md"

print(f"\nСписок литературы:")
print(f"  В Version4: {lit_v4.exists()} - {lit_v4}")
if not lit_v5.exists() and lit_v4.exists():
    import shutil
    shutil.copy2(lit_v4, lit_v5)
    print(f"  ✓ Скопирован в Version5")
else:
    print(f"  В Version5: {lit_v5.exists()} - {lit_v5}")

print("\n✓ Проверка завершена")




