"""
Скрипт для автоматической отправки данных из CSV в Google Form
Использует Selenium для автоматизации браузера с контекстным поиском радиокнопок
"""
import pandas as pd
import os
import time
import json
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

# Настройка логирования
def setup_logging(log_dir=None):
    """Настройка логирования"""
    if log_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(base_dir, '..')
        log_dir = os.path.join(project_root, 'logs')
    
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'form_submission_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__), log_file

def find_radio_in_question_context(driver, question_index, answer_value, question_type='scale', logger=None):
    """
    Находит радиокнопку в контексте конкретного вопроса
    
    Args:
        driver: WebDriver instance
        question_index: Индекс вопроса (0-based)
        answer_value: Значение ответа (1-5 для scale, 1-2 для choice)
        question_type: Тип вопроса ('scale' для 1-5, 'choice' для 1-2)
        logger: Logger instance
    
    Returns:
        WebElement или None
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    # Стратегия 1: Поиск контейнера вопроса через listitem и радиокнопки внутри
    try:
        listitems = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
        
        # Фильтруем listitems: ищем только те, которые содержат радиокнопки (это вопросы)
        question_listitems = []
        for item in listitems:
            radios_in_item = item.find_elements(By.CSS_SELECTOR, "div[role='radio']")
            if radios_in_item:  # Если есть радиокнопки, это вопрос
                question_listitems.append(item)
        
        # Если нашли вопросы через фильтрацию, используем их
        if question_listitems and question_index < len(question_listitems):
            question_container = question_listitems[question_index]
        elif question_index < len(listitems):
            # Fallback: используем все listitems (может быть заголовок в начале)
            # Пропускаем первый listitem, если он не содержит радиокнопок
            start_idx = 0
            if len(listitems) > 0:
                first_radios = listitems[0].find_elements(By.CSS_SELECTOR, "div[role='radio']")
                if not first_radios:  # Первый listitem не содержит радиокнопок - это заголовок
                    start_idx = 1
            
            if question_index + start_idx < len(listitems):
                question_container = listitems[question_index + start_idx]
            else:
                raise IndexError("Question index out of range")
        else:
            raise IndexError("Question index out of range")
            
            # Ищем радиокнопки внутри этого контейнера
            radios = question_container.find_elements(By.CSS_SELECTOR, "div[role='radio']")
            
            if radios:
                # Для scale вопросов (1-5) выбираем по индексу
                if question_type == 'scale' and 1 <= answer_value <= 5:
                    if len(radios) >= answer_value:
                        target_radio = radios[answer_value - 1]
                        logger.info(f"  Стратегия 1 (listitem): найдена радиокнопка для вопроса {question_index + 1}, ответ {answer_value}")
                        return target_radio
                
                # Для choice вопросов (1-2) выбираем по индексу
                elif question_type == 'choice' and 1 <= answer_value <= 2:
                    if len(radios) >= answer_value:
                        target_radio = radios[answer_value - 1]
                        logger.info(f"  Стратегия 1 (listitem): найдена радиокнопка для вопроса {question_index + 1}, ответ {answer_value}")
                        return target_radio
                
                # Альтернативно: поиск по data-value внутри контейнера
                for radio in radios:
                    try:
                        data_value = radio.get_attribute('data-value')
                        if data_value and str(data_value) == str(answer_value):
                            logger.info(f"  Стратегия 1 (listitem + data-value): найдена радиокнопка для вопроса {question_index + 1}, ответ {answer_value}")
                            return radio
                    except:
                        continue
    except Exception as e:
        logger.debug(f"  Стратегия 1 не сработала: {e}")
    
    # Стратегия 2: Группировка радиокнопок по вопросам через listitem
    try:
        # Находим все listitems с вопросами (которые содержат радиокнопки)
        listitems = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
        question_listitems = []
        
        for item in listitems:
            radios_in_item = item.find_elements(By.CSS_SELECTOR, "div[role='radio']")
            if radios_in_item:  # Если есть радиокнопки, это вопрос
                question_listitems.append(item)
        
        if question_index < len(question_listitems):
            question_container = question_listitems[question_index]
            radios = question_container.find_elements(By.CSS_SELECTOR, "div[role='radio']")
            
            if radios:
                if question_type == 'scale' and 1 <= answer_value <= 5:
                    if len(radios) >= answer_value:
                        target_radio = radios[answer_value - 1]
                        logger.info(f"  Стратегия 2 (listitem группировка): найдена радиокнопка для вопроса {question_index + 1}, ответ {answer_value}")
                        return target_radio
                elif question_type == 'choice' and 1 <= answer_value <= 2:
                    if len(radios) >= answer_value:
                        target_radio = radios[answer_value - 1]
                        logger.info(f"  Стратегия 2 (listitem группировка): найдена радиокнопка для вопроса {question_index + 1}, ответ {answer_value}")
                        return target_radio
    except Exception as e:
        logger.debug(f"  Стратегия 2 не сработала: {e}")
    
    # Стратегия 3: Поиск по data-value с фильтрацией по видимости
    try:
        # Находим все радиокнопки с нужным data-value
        radios_with_value = driver.find_elements(By.CSS_SELECTOR, f"div[data-value='{answer_value}']")
        
        # Фильтруем по видимости
        visible_radios = [r for r in radios_with_value if r.is_displayed()]
        
        if visible_radios:
            # Пытаемся определить, какая радиокнопка относится к нужному вопросу
            # Используем позицию на странице
            listitems = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
            if question_index < len(listitems):
                question_container = listitems[question_index]
                question_y = question_container.location['y']
                
                # Находим радиокнопку, которая находится ближе всего к контейнеру вопроса
                best_radio = None
                min_distance = float('inf')
                
                for radio in visible_radios:
                    radio_y = radio.location['y']
                    distance = abs(radio_y - question_y)
                    if distance < min_distance:
                        min_distance = distance
                        best_radio = radio
                
                if best_radio:
                    logger.info(f"  Стратегия 3 (data-value + позиция): найдена радиокнопка для вопроса {question_index + 1}, ответ {answer_value}")
                    return best_radio
    except Exception as e:
        logger.debug(f"  Стратегия 3 не сработала: {e}")
    
    # Стратегия 4: Поиск через XPath по структуре
    try:
        listitems = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
        if question_index < len(listitems):
            question_container = listitems[question_index]
            # Ищем радиокнопку с нужным data-value внутри контейнера
            xpath = f".//div[@role='radio' and @data-value='{answer_value}']"
            radio = question_container.find_element(By.XPATH, xpath)
            logger.info(f"  Стратегия 4 (XPath): найдена радиокнопка для вопроса {question_index + 1}, ответ {answer_value}")
            return radio
    except Exception as e:
        logger.debug(f"  Стратегия 4 не сработала: {e}")
    
    logger.warning(f"  Не удалось найти радиокнопку для вопроса {question_index + 1}, ответ {answer_value}")
    return None

def scroll_to_element(driver, element):
    """Прокручивает страницу к элементу"""
    try:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.3)
    except:
        pass

def fill_question_page(driver, questions_data, question_type, page_name, logger, delay=0.2):
    """
    Заполняет страницу с вопросами
    
    Args:
        driver: WebDriver instance
        questions_data: Список кортежей (question_index, answer_value)
        question_type: Тип вопроса ('scale' или 'choice')
        page_name: Название страницы для логирования
        logger: Logger instance
        delay: Задержка между вопросами
    """
    logger.info(f"{page_name}: Начало заполнения {len(questions_data)} вопросов")
    
    for q_idx, answer_value in questions_data:
        try:
            logger.info(f"  Обработка вопроса {q_idx + 1}/{len(questions_data)}: ответ {answer_value}")
            
            # Находим радиокнопку в контексте вопроса
            radio = find_radio_in_question_context(driver, q_idx, answer_value, question_type, logger)
            
            if radio:
                # Прокручиваем к элементу
                scroll_to_element(driver, radio)
                
                # Ждем, пока элемент станет кликабельным
                try:
                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(radio))
                except:
                    pass
                
                # Кликаем на радиокнопку
                clicked = False
                try:
                    # Пробуем обычный клик
                    radio.click()
                    clicked = True
                    logger.debug(f"    Клик выполнен обычным способом")
                except Exception as e:
                    logger.debug(f"    Обычный клик не сработал: {e}, пробуем JavaScript")
                    try:
                        # Если обычный клик не работает, используем JavaScript
                        driver.execute_script("arguments[0].click();", radio)
                        clicked = True
                        logger.debug(f"    Клик выполнен через JavaScript")
                    except Exception as e2:
                        logger.error(f"    JavaScript клик тоже не сработал: {e2}")
                
                # Проверяем, что радиокнопка действительно выбрана
                if clicked:
                    time.sleep(0.3)  # Даем время на обновление состояния
                    try:
                        # Проверяем атрибут aria-checked или checked
                        is_checked = radio.get_attribute('aria-checked')
                        if is_checked == 'true' or radio.get_attribute('checked'):
                            logger.info(f"    ✓ Вопрос {q_idx + 1} заполнен (подтверждено)")
                        else:
                            logger.warning(f"    ⚠ Вопрос {q_idx + 1}: клик выполнен, но состояние не изменилось")
                    except:
                        logger.info(f"    ✓ Вопрос {q_idx + 1} заполнен (клик выполнен)")
                
                time.sleep(delay)
            else:
                logger.error(f"    ✗ Не удалось найти радиокнопку для вопроса {q_idx + 1}")
                # Продолжаем работу, но логируем ошибку
                
        except Exception as e:
            logger.error(f"    ✗ Ошибка при заполнении вопроса {q_idx + 1}: {e}")
            # Продолжаем работу
    
    # Прокручиваем вниз для кнопки "Далее"
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(0.5)

def submit_form_data(csv_file, form_url, start_index=0, delay=2, test_mode=False, progress_file=None):
    """
    Автоматическая отправка данных из CSV в Google Form
    
    Args:
        csv_file: путь к CSV файлу с данными
        form_url: URL Google Form
        start_index: индекс строки для начала отправки (для возобновления)
        delay: задержка между действиями в секундах
        test_mode: если True, обрабатывает только первую запись
        progress_file: путь к файлу для сохранения прогресса
    """
    # Настройка логирования
    logger, log_file = setup_logging()
    logger.info("=" * 60)
    logger.info("НАЧАЛО АВТОМАТИЧЕСКОЙ ОТПРАВКИ ДАННЫХ В GOOGLE FORM")
    logger.info("=" * 60)
    logger.info(f"CSV файл: {csv_file}")
    logger.info(f"Google Form: {form_url}")
    logger.info(f"Начало с записи: {start_index + 1}")
    logger.info(f"Задержка: {delay} секунд")
    logger.info(f"Тестовый режим: {test_mode}")
    logger.info(f"Лог файл: {log_file}")
    logger.info("=" * 60)
    
    # Читаем CSV файл
    logger.info(f"Чтение данных из {csv_file}...")
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    logger.info(f"Найдено записей: {len(df)}")
    
    # Настройка Chrome
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    # Файл для сохранения прогресса
    if progress_file is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(base_dir, '..')
        progress_file = os.path.join(project_root, 'data', 'generated', 'submission_progress.json')
    
    os.makedirs(os.path.dirname(progress_file), exist_ok=True)
    
    successful_submissions = []
    failed_submissions = []
    
    try:
        max_records = 1 if test_mode else len(df)
        
        for idx, row in df.iterrows():
            if idx < start_index:
                continue
            
            if idx >= start_index + max_records:
                break
            
            record_info = {
                'index': int(idx),
                'name': str(row.get('Имя', 'Unknown')),
                'timestamp': datetime.now().isoformat(),
                'status': 'processing'
            }
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Обработка записи {idx + 1}/{len(df)}: {row.get('Имя', 'Unknown')}")
            logger.info(f"{'='*60}")
            
            try:
                # Переходим на форму
                driver.get(form_url)
                time.sleep(delay)
                
                # Страница 1: Имя, Возраст, Класс
                logger.info("Страница 1: Заполнение основных данных...")
                try:
                    # Ищем все текстовые поля
                    text_inputs = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='text']"))
                    )
                    
                    # Заполняем Имя
                    if len(text_inputs) > 0:
                        text_inputs[0].clear()
                        text_inputs[0].send_keys(str(row.get('Имя', '')))
                        time.sleep(0.5)
                    
                    # Заполняем Возраст
                    if len(text_inputs) > 1:
                        text_inputs[1].clear()
                        text_inputs[1].send_keys(str(int(row.get('Возраст', 0))))
                        time.sleep(0.5)
                    
                    # Заполняем Класс
                    if len(text_inputs) > 2:
                        text_inputs[2].clear()
                        text_inputs[2].send_keys(str(row.get('Класс', '')))
                        time.sleep(0.5)
                    
                    # Нажимаем "Далее"
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Далее')] | //div[contains(text(), 'Далее')]"))
                    )
                    next_button.click()
                    time.sleep(delay)
                    logger.info("  ✓ Страница 1 заполнена")
                    
                except Exception as e:
                    logger.error(f"  ✗ Ошибка на странице 1: {e}")
                    raise
                
                # Страница 2: 60 вопросов Q1-Q60 (шкала 1-5)
                logger.info("Страница 2: Заполнение 60 вопросов Q1-Q60...")
                try:
                    questions_data = []
                    for q_num in range(1, 61):
                        q_col = f'Q{q_num}'
                        answer = int(row.get(q_col, 1))
                        questions_data.append((q_num - 1, answer))  # question_index = q_num - 1
                    
                    fill_question_page(driver, questions_data, 'scale', "Страница 2", logger, delay=0.2)
                    
                    # Нажимаем "Далее"
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Далее')] | //div[contains(text(), 'Далее')]"))
                    )
                    next_button.click()
                    time.sleep(delay)
                    logger.info("  ✓ Страница 2 заполнена")
                    
                except Exception as e:
                    logger.error(f"  ✗ Ошибка на странице 2: {e}")
                    raise
                
                # Страница 3: 42 вопроса Choice1-Choice42 (выбор 1 или 2)
                logger.info("Страница 3: Заполнение 42 вопросов Choice1-Choice42...")
                try:
                    questions_data = []
                    for choice_num in range(1, 43):
                        choice_col = f'Choice{choice_num}'
                        answer = int(row.get(choice_col, 1))
                        questions_data.append((choice_num - 1, answer))
                    
                    fill_question_page(driver, questions_data, 'choice', "Страница 3", logger, delay=0.2)
                    
                    # Нажимаем "Далее"
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Далее')] | //div[contains(text(), 'Далее')]"))
                    )
                    next_button.click()
                    time.sleep(delay)
                    logger.info("  ✓ Страница 3 заполнена")
                    
                except Exception as e:
                    logger.error(f"  ✗ Ошибка на странице 3: {e}")
                    raise
                
                # Страница 4: 20 вопросов ProfQ1-ProfQ20 (шкала 1-5)
                logger.info("Страница 4: Заполнение 20 вопросов ProfQ1-ProfQ20...")
                try:
                    questions_data = []
                    for prof_q_num in range(1, 21):
                        prof_q_col = f'ProfQ{prof_q_num}'
                        answer = int(row.get(prof_q_col, 1))
                        questions_data.append((prof_q_num - 1, answer))
                    
                    fill_question_page(driver, questions_data, 'scale', "Страница 4", logger, delay=0.2)
                    
                    # Нажимаем "Отправить"
                    submit_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Отправить')] | //div[contains(text(), 'Отправить')]"))
                    )
                    submit_button.click()
                    time.sleep(delay * 2)
                    
                    logger.info(f"  ✓ Запись {idx + 1} успешно отправлена!")
                    record_info['status'] = 'success'
                    successful_submissions.append(record_info)
                    
                except Exception as e:
                    logger.error(f"  ✗ Ошибка на странице 4: {e}")
                    raise
                
            except Exception as e:
                logger.error(f"✗ Ошибка при обработке записи {idx + 1}: {e}")
                record_info['status'] = 'failed'
                record_info['error'] = str(e)
                failed_submissions.append(record_info)
                
                # Сохраняем скриншот при ошибке
                try:
                    screenshot_dir = os.path.join(os.path.dirname(progress_file), 'screenshots')
                    os.makedirs(screenshot_dir, exist_ok=True)
                    screenshot_file = os.path.join(screenshot_dir, f'error_record_{idx + 1}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
                    driver.save_screenshot(screenshot_file)
                    logger.info(f"  Скриншот сохранен: {screenshot_file}")
                except:
                    pass
                
                # Продолжаем работу со следующей записью
                continue
            
            # Сохраняем прогресс
            progress_data = {
                'last_processed_index': int(idx),
                'successful_count': len(successful_submissions),
                'failed_count': len(failed_submissions),
                'successful_submissions': successful_submissions,
                'failed_submissions': failed_submissions,
                'last_update': datetime.now().isoformat()
            }
            
            try:
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(progress_data, f, ensure_ascii=False, indent=2)
            except:
                pass
            
            # Небольшая задержка между отправками
            time.sleep(delay)
            
    except KeyboardInterrupt:
        logger.info(f"\n\nПрервано пользователем. Последняя обработанная запись: {idx}")
        logger.info(f"Для продолжения используйте start_index={idx + 1}")
    except Exception as e:
        logger.error(f"\nКритическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("\n" + "=" * 60)
        logger.info("ИТОГИ")
        logger.info("=" * 60)
        logger.info(f"Успешно отправлено: {len(successful_submissions)}")
        logger.info(f"Ошибок: {len(failed_submissions)}")
        logger.info(f"Прогресс сохранен в: {progress_file}")
        logger.info("=" * 60)
        
        print("\nЗакрытие браузера...")
        driver.quit()


if __name__ == "__main__":
    import sys
    
    # Пути
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(base_dir, '..')
    
    # CSV файл
    csv_file = r'c:\Users\krono\Downloads\new-all_50_pairs.csv'
    
    # URL Google Form
    form_url = 'https://forms.gle/jtdB9xU37NZUmH8o6'
    
    # Параметры
    start_index = 1  # Начало со второй записи (первая уже отправлена в тестовом режиме)
    delay = 2  # Задержка между действиями в секундах
    test_mode = False  # Обработка всех записей (измените на True для тестового режима)
    
    # Проверка наличия файла
    if not os.path.exists(csv_file):
        print(f"Ошибка: файл {csv_file} не найден!")
        sys.exit(1)
    
    print("=" * 60)
    print("АВТОМАТИЧЕСКАЯ ОТПРАВКА ДАННЫХ В GOOGLE FORM")
    print("=" * 60)
    print(f"CSV файл: {csv_file}")
    print(f"Google Form: {form_url}")
    print(f"Начало с записи: {start_index + 1}")
    print(f"Задержка: {delay} секунд")
    print(f"Тестовый режим: {test_mode}")
    print("=" * 60)
    
    input("Нажмите Enter для начала...")
    
    submit_form_data(csv_file, form_url, start_index, delay, test_mode=test_mode)
