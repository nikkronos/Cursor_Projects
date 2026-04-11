# -*- coding: utf-8 -*-
"""
Единый скрипт для выполнения всех задач по порядку:
1. Задача В - добавление фамилий к подходам
2. Задачи Д, З, Н, О - цитирование
3. Работа со списком литературы
"""
import sys
from pathlib import Path

def main():
    print("=" * 70)
    print("ВЫПОЛНЕНИЕ ВСЕХ ЗАДАЧ ПО ПОРЯДКУ")
    print("=" * 70)
    print()
    
    v4 = Path(__file__).parent
    
    # 1. Задача В
    print("[1/3] Задача В: Добавление фамилий к подходам")
    print("-" * 70)
    try:
        from fix_task_V import fix_task_V
        if fix_task_V():
            print("✓ Задача В выполнена успешно")
        else:
            print("⚠ Задача В: проблемы при выполнении")
    except Exception as e:
        print(f"✗ Ошибка в задаче В: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # 2. Задачи Д, З, Н, О
    print("[2/3] Задачи Д, З, Н, О: Цитирование")
    print("-" * 70)
    try:
        from fix_citations_D_З_Н_О import fix_citations_in_document
        if fix_citations_in_document():
            print("✓ Задачи Д, З, Н, О выполнены успешно")
        else:
            print("⚠ Задачи Д, З, Н, О: проблемы при выполнении")
    except Exception as e:
        print(f"✗ Ошибка в задачах Д, З, Н, О: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # 3. Список литературы
    print("[3/3] Работа со списком литературы")
    print("-" * 70)
    try:
        from fix_literature_list import create_final_literature_list
        if create_final_literature_list():
            print("✓ Работа со списком литературы выполнена успешно")
        else:
            print("⚠ Работа со списком литературы: проблемы при выполнении")
    except Exception as e:
        print(f"✗ Ошибка в работе со списком литературы: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 70)
    print("ВЫПОЛНЕНИЕ ЗАВЕРШЕНО")
    print("=" * 70)

if __name__ == '__main__':
    main()





