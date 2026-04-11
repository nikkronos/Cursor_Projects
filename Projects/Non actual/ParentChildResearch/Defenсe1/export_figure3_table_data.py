"""
Извлекает данные для таблицы координат точек Рисунка 3 (scatter plot Овчарова-Холланд).
Создаёт текстовый файл с данными для вставки в таблицу Word.
"""
import os
import runpy

def main():
    defence_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(defence_dir)
    enhanced_path = os.path.join(project_root, "Final3", "enhanced_analysis.py")
    
    if not os.path.exists(enhanced_path):
        print("ОШИБКА: не найден enhanced_analysis.py")
        return
    
    globals_dict = runpy.run_path(enhanced_path)
    significant_ovcharova_holland = globals_dict.get("significant_ovcharova_holland", [])
    
    if len(significant_ovcharova_holland) == 0:
        print("Нет значимых корреляций Овчарова-Холланд для Рисунка 3")
        return
    
    # Берём первую значимую корреляцию
    corr = significant_ovcharova_holland[0]
    ovcharova_values = corr.get('ovcharova_values', [])
    holland_values = corr.get('holland_values', [])
    ovcharova_q = corr.get('ovcharova_question', '?')
    holland_name = corr.get('holland_type_name', corr.get('holland_type', '?'))
    rho = corr.get('spearman_corr', 0)
    p_val = corr.get('spearman_p', 1)
    n = len(ovcharova_values)
    
    # Формируем данные для таблицы
    lines = []
    lines.append("ДАННЫЕ ДЛЯ ТАБЛИЦЫ К РИСУНКУ 3")
    lines.append("=" * 60)
    lines.append(f"Корреляция: {ovcharova_q} ↔ {holland_name}")
    lines.append(f"ρ (Спирмен) = {rho:.4f}, p = {p_val:.4f}")
    lines.append(f"Количество наблюдений: {n}")
    lines.append("")
    lines.append("Таблица координат точек (X, Y):")
    lines.append("")
    lines.append("№\tБалл по мотиву (X)\tБалл по типу Холланда (Y)")
    lines.append("-" * 60)
    
    for i in range(n):
        lines.append(f"{i+1}\t{ovcharova_values[i]}\t{holland_values[i]}")
    
    text = "\n".join(lines)
    print(text)
    
    out_path = os.path.join(defence_dir, "Данные_для_таблицы_Рисунок3.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\nСохранено: {out_path}")

if __name__ == "__main__":
    main()
