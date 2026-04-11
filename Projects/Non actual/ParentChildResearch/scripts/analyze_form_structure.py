"""
Скрипт для анализа DOM структуры Google Forms
Сохраняет HTML структуру каждой страницы и анализирует паттерны организации вопросов
"""
import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def analyze_form_structure(form_url, output_dir=None, manual_mode=False):
    """
    Анализирует структуру Google Form и сохраняет результаты
    
    Args:
        form_url: URL Google Form
        output_dir: Директория для сохранения результатов (по умолчанию: data/raw/form_analysis)
        manual_mode: Если True, пользователь вручную переходит между страницами
    """
    if output_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(base_dir, '..')
        output_dir = os.path.join(project_root, 'data', 'raw', 'form_analysis')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Настройка Chrome
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    analysis_results = {
        'form_url': form_url,
        'pages': []
    }
    
    try:
        print("=" * 60)
        print("АНАЛИЗ СТРУКТУРЫ GOOGLE FORM")
        print("=" * 60)
        print(f"URL формы: {form_url}")
        print(f"Директория для сохранения: {output_dir}")
        if manual_mode:
            print("РЕЖИМ: Ручной переход между страницами")
        else:
            print("РЕЖИМ: Автоматический переход")
        print("=" * 60)
        
        # Переходим на форму
        print("\nОткрытие формы в браузере...")
        driver.get(form_url)
        
        # Ждем загрузки формы
        print("Ожидание загрузки формы...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)
        
        # Страница 1: Основные данные
        print("\n[Страница 1] Анализ структуры...")
        page1_data = analyze_page(driver, 1, output_dir)
        analysis_results['pages'].append(page1_data)
        
        if not manual_mode:
            # Пытаемся заполнить первую страницу тестовыми данными для перехода
            print("\nПопытка заполнения первой страницы тестовыми данными...")
            try:
                # Ищем текстовые поля
                text_inputs = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='text']"))
                )
                
                if len(text_inputs) >= 3:
                    print("  Найдено текстовых полей:", len(text_inputs))
                    
                    # Заполняем тестовыми данными
                    text_inputs[0].clear()
                    text_inputs[0].send_keys("Тест Тестов")
                    time.sleep(0.5)
                    print("  ✓ Заполнено поле 1: Имя")
                    
                    text_inputs[1].clear()
                    text_inputs[1].send_keys("15")
                    time.sleep(0.5)
                    print("  ✓ Заполнено поле 2: Возраст")
                    
                    text_inputs[2].clear()
                    text_inputs[2].send_keys("9")
                    time.sleep(0.5)
                    print("  ✓ Заполнено поле 3: Класс")
                else:
                    print(f"  ⚠ Найдено только {len(text_inputs)} текстовых полей (ожидалось 3)")
            except Exception as e:
                print(f"  ⚠ Не удалось автоматически заполнить первую страницу: {e}")
                print("  Переключение в ручной режим...")
                manual_mode = True
        
        if manual_mode:
            print("\n" + "=" * 60)
            print("РУЧНОЙ РЕЖИМ")
            print("=" * 60)
            print("Пожалуйста, заполните первую страницу вручную и нажмите 'Далее'")
            print("После этого нажмите Enter здесь, чтобы продолжить анализ...")
            input("Нажмите Enter после перехода на страницу 2...")
        else:
            # Переходим на страницу 2 автоматически
            try:
                print("\nПопытка перехода на страницу 2...")
                # Пробуем разные селекторы для кнопки "Далее"
                next_selectors = [
                    "//span[contains(text(), 'Далее')]",
                    "//div[contains(text(), 'Далее')]",
                    "//button[contains(., 'Далее')]",
                    "//div[@role='button' and contains(., 'Далее')]",
                    "//span[@jsname and contains(text(), 'Далее')]"
                ]
                
                next_button = None
                for selector in next_selectors:
                    try:
                        next_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        print(f"  ✓ Кнопка 'Далее' найдена по селектору: {selector}")
                        break
                    except:
                        continue
                
                if next_button:
                    # Прокручиваем к кнопке
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
                    time.sleep(1)
                    next_button.click()
                    print("  ✓ Кнопка 'Далее' нажата")
                    time.sleep(3)  # Ждем загрузки следующей страницы
                else:
                    print("  ⚠ Кнопка 'Далее' не найдена автоматически")
                    print("  Переключение в ручной режим...")
                    manual_mode = True
                    input("  Нажмите Enter после перехода на страницу 2...")
            except Exception as e:
                print(f"  ⚠ Ошибка при автоматическом переходе: {e}")
                print("  Переключение в ручной режим...")
                manual_mode = True
                input("  Нажмите Enter после перехода на страницу 2...")
        
        # Обработка страниц 2-4
        try:
            print("\n[Страница 2] Анализ структуры (60 вопросов Q1-Q60)...")
            page2_data = analyze_page(driver, 2, output_dir)
            analysis_results['pages'].append(page2_data)
            
            # Переходим на страницу 3
            if manual_mode:
                print("\nПереход на страницу 3...")
                input("Нажмите Enter после перехода на страницу 3...")
            else:
                print("\nПопытка перехода на страницу 3...")
                next_selectors = [
                    "//span[contains(text(), 'Далее')]",
                    "//div[contains(text(), 'Далее')]",
                    "//button[contains(., 'Далее')]",
                    "//div[@role='button' and contains(., 'Далее')]"
                ]
                
                next_button = None
                for selector in next_selectors:
                    try:
                        next_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        break
                    except:
                        continue
                
                if next_button:
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
                    time.sleep(1)
                    next_button.click()
                    time.sleep(3)
                else:
                    print("  ⚠ Кнопка 'Далее' не найдена, переход вручную")
                    manual_mode = True
                    input("  Нажмите Enter после перехода на страницу 3...")
            
            print("\n[Страница 3] Анализ структуры (42 вопроса Choice1-Choice42)...")
            page3_data = analyze_page(driver, 3, output_dir)
            analysis_results['pages'].append(page3_data)
            
            # Переходим на страницу 4
            if manual_mode:
                print("\nПереход на страницу 4...")
                input("Нажмите Enter после перехода на страницу 4...")
            else:
                print("\nПопытка перехода на страницу 4...")
                next_selectors = [
                    "//span[contains(text(), 'Далее')]",
                    "//div[contains(text(), 'Далее')]",
                    "//button[contains(., 'Далее')]",
                    "//div[@role='button' and contains(., 'Далее')]"
                ]
                
                next_button = None
                for selector in next_selectors:
                    try:
                        next_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        break
                    except:
                        continue
                
                if next_button:
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
                    time.sleep(1)
                    next_button.click()
                    time.sleep(3)
                else:
                    print("  ⚠ Кнопка 'Далее' не найдена, переход вручную")
                    manual_mode = True
                    input("  Нажмите Enter после перехода на страницу 4...")
            
            print("\n[Страница 4] Анализ структуры (20 вопросов ProfQ1-ProfQ20)...")
            page4_data = analyze_page(driver, 4, output_dir)
            analysis_results['pages'].append(page4_data)
        
        except Exception as e:
            print(f"Ошибка при переходе между страницами: {e}")
            import traceback
            traceback.print_exc()
        
        # Сохраняем результаты анализа
        results_file = os.path.join(output_dir, 'analysis_results.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print("АНАЛИЗ ЗАВЕРШЕН")
        print("=" * 60)
        print(f"Результаты сохранены в: {results_file}")
        print(f"HTML файлы сохранены в: {output_dir}")
        
    except Exception as e:
        print(f"\nОшибка при анализе: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nЗакрытие браузера...")
        input("Нажмите Enter для закрытия браузера...")
        driver.quit()

def analyze_page(driver, page_num, output_dir):
    """
    Анализирует структуру одной страницы формы
    
    Returns:
        dict: Данные о структуре страницы
    """
    page_data = {
        'page_number': page_num,
        'html_file': None,
        'question_containers': [],
        'radio_buttons': [],
        'selectors_found': {}
    }
    
    # Сохраняем HTML страницы
    html_file = os.path.join(output_dir, f'page_{page_num}.html')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    page_data['html_file'] = html_file
    print(f"  HTML сохранен: {html_file}")
    
    # Ищем все возможные контейнеры вопросов
    question_selectors = [
        "div[role='listitem']",
        "div[data-params]",
        "div[jsname]",
        "div[data-item-id]",
        "div[aria-label]",
        "div[role='group']",
        "div.freebirdFormviewerViewItemsItemItem",
        "div[jscontroller]"
    ]
    
    print(f"  Поиск контейнеров вопросов...")
    for selector in question_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                page_data['selectors_found'][selector] = len(elements)
                print(f"    Найдено элементов по '{selector}': {len(elements)}")
        except:
            pass
    
    # Ищем все радиокнопки
    print(f"  Поиск радиокнопок...")
    radio_selectors = [
        "div[role='radio']",
        "div[data-value]",
        "div[aria-checked]",
        "div[jsname]",
        "div[jscontroller]"
    ]
    
    all_radios = []
    for selector in radio_selectors:
        try:
            radios = driver.find_elements(By.CSS_SELECTOR, selector)
            if radios:
                for radio in radios:
                    radio_info = {
                        'selector': selector,
                        'tag': radio.tag_name,
                        'attributes': {}
                    }
                    # Собираем все атрибуты
                    attrs = driver.execute_script("""
                        var items = {};
                        for (index = 0; index < arguments[0].attributes.length; ++index) {
                            items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value;
                        }
                        return items;
                    """, radio)
                    radio_info['attributes'] = attrs
                    
                    # Проверяем видимость
                    try:
                        radio_info['is_displayed'] = radio.is_displayed()
                        radio_info['location'] = {
                            'x': radio.location['x'],
                            'y': radio.location['y']
                        }
                    except:
                        radio_info['is_displayed'] = False
                    
                    all_radios.append(radio_info)
        except Exception as e:
            print(f"    Ошибка при поиске по '{selector}': {e}")
    
    page_data['radio_buttons'] = all_radios
    print(f"    Всего найдено радиокнопок: {len(all_radios)}")
    
    # Пытаемся найти структуру вопросов
    print(f"  Анализ структуры вопросов...")
    try:
        # Ищем контейнеры с вопросами через listitem
        listitems = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
        print(f"    Найдено listitem элементов: {len(listitems)}")
        
        for idx, item in enumerate(listitems[:5]):  # Анализируем первые 5 для примера
            try:
                # Ищем радиокнопки внутри этого контейнера
                radios_in_item = item.find_elements(By.CSS_SELECTOR, "div[role='radio']")
                
                question_info = {
                    'question_index': idx + 1,
                    'listitem_index': idx,
                    'radios_count': len(radios_in_item),
                    'radio_data_values': []
                }
                
                for radio in radios_in_item:
                    try:
                        data_value = radio.get_attribute('data-value')
                        if data_value:
                            question_info['radio_data_values'].append(data_value)
                    except:
                        pass
                
                if radios_in_item:
                    page_data['question_containers'].append(question_info)
                    print(f"      Вопрос {idx + 1}: найдено {len(radios_in_item)} радиокнопок, data-values: {question_info['radio_data_values']}")
            except Exception as e:
                print(f"      Ошибка при анализе вопроса {idx + 1}: {e}")
    except Exception as e:
        print(f"    Ошибка при анализе структуры: {e}")
    
    return page_data

if __name__ == "__main__":
    import sys
    
    form_url = 'https://forms.gle/jtdB9xU37NZUmH8o6'
    
    # Проверяем аргументы командной строки
    manual_mode = '--manual' in sys.argv or '-m' in sys.argv
    
    if manual_mode:
        print("\n" + "=" * 60)
        print("РЕЖИМ: Ручной переход между страницами")
        print("=" * 60)
        print("Скрипт будет ждать, пока вы вручную перейдете между страницами")
        print("Это полезно, если автоматическое заполнение не работает")
        print("=" * 60 + "\n")
    
    analyze_form_structure(form_url, manual_mode=manual_mode)

