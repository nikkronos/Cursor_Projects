"""
Выводит компактный текстовый список всех значимых корреляций для вставки в работу.
Запуск: python list_significant_correlations.py
Результат печатается в консоль и сохраняется в Список_значимых_корреляций.txt
"""
import os
import runpy

def short(s, max_len=55):
    s = str(s).strip()
    return (s[:max_len] + "…") if len(s) > max_len else s

def main():
    defence_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(defence_dir)
    enhanced_path = os.path.join(project_root, "Final3", "enhanced_analysis.py")
    if not os.path.exists(enhanced_path):
        print("ОШИБКА: не найден enhanced_analysis.py")
        return
    globals_dict = runpy.run_path(enhanced_path)
    sig_om = sorted(globals_dict.get("significant_ovcharova_markovskaya", []), key=lambda x: abs(x["spearman_corr"]), reverse=True)
    sig_mh = sorted(globals_dict.get("significant_holland", []), key=lambda x: abs(x["spearman_corr"]), reverse=True)
    sig_oh = globals_dict.get("significant_ovcharova_holland", [])

    lines = []
    lines.append("Значимые корреляции (p < 0,05):")
    lines.append("")
    for c in sig_om:
        lines.append(f"• Установка родителя (ВРР) — мотив Овчаровой: «{short(c['parent_question'])}» ↔ «{short(c['ovcharova_question'], 50)}» (ρ = {c['spearman_corr']:.3f}).")
    for c in sig_mh:
        lines.append(f"• Установка родителя (ВРР) — тип Холланда: «{short(c['parent_question'])}» ↔ {c.get('holland_type_name', c.get('holland_type', '?'))} (ρ = {c['spearman_corr']:.3f}).")
    for c in sig_oh:
        lines.append(f"• Мотив Овчаровой — тип Холланда: «{short(c.get('ovcharova_question', '?'), 50)}» ↔ {c.get('holland_type_name', '?')} (ρ = {c['spearman_corr']:.3f}).")

    text = "\n".join(lines)
    print(text)
    out = os.path.join(defence_dir, "Список_значимых_корреляций.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\nСохранено: {out}")

if __name__ == "__main__":
    main()
