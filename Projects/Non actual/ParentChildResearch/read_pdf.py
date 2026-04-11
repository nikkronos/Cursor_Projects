"""Скрипт для чтения PDF файлов"""
import sys
import os

# Добавляем путь к рабочему столу
desktop_path = os.path.expanduser(r"~\OneDrive\Рабочий стол")
if not os.path.exists(desktop_path):
    desktop_path = r"C:\Users\krono\OneDrive\Рабочий стол"

try:
    import PyPDF2
    
    # Читаем методичку
    metodichka_path = os.path.join(desktop_path, "Методические рекомендации по написанию ВКР бакалавриат 2024.pdf")
    
    with open(metodichka_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        print(f"Всего страниц в методичке: {len(reader.pages)}")
        print("\n" + "="*80)
        print("СТРАНИЦА 21 (индекс 20):")
        print("="*80)
        page_21 = reader.pages[20].extract_text()
        print(page_21)
        
        # Также проверим приложение 2
        print("\n" + "="*80)
        print("ПОИСК ПРИЛОЖЕНИЯ 2:")
        print("="*80)
        for i in range(len(reader.pages)):
            text = reader.pages[i].extract_text()
            if "ПРИЛОЖЕНИЕ 2" in text or "Приложение 2" in text or "Приложение 2" in text:
                print(f"\nНайдено на странице {i+1}:")
                print(text[:2000])
                break
        
        # Поиск структуры Главы II
        print("\n" + "="*80)
        print("ПОИСК СТРУКТУРЫ ГЛАВЫ II:")
        print("="*80)
        for i in range(len(reader.pages)):
            text = reader.pages[i].extract_text()
            if "ГЛАВА II" in text or "Глава II" in text or "Глава 2" in text:
                print(f"\nНайдено на странице {i+1}:")
                print(text[:3000])
                
except ImportError:
    print("PyPDF2 не установлен. Устанавливаю...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
    # Повторяем попытку
    import PyPDF2
    metodichka_path = os.path.join(desktop_path, "Методические рекомендации по написанию ВКР бакалавриат 2024.pdf")
    with open(metodichka_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        print(f"Всего страниц: {len(reader.pages)}")
        print("\nСТРАНИЦА 21:")
        print(reader.pages[20].extract_text())

except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()

