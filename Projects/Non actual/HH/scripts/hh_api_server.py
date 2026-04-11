"""
HTTP API сервер для запуска автоматизации HeadHunter через N8N
Использует Flask для создания REST API endpoint
"""
import os
import json
import threading
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / 'env_vars.txt')

# Настройка путей
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Настройка логирования
log_file = LOGS_DIR / f'hh_api_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Глобальная переменная для хранения результатов выполнения
execution_results = {}
execution_lock = threading.Lock()

def run_automation():
    """Запускает автоматизацию в отдельном потоке"""
    try:
        # Импортируем функцию main из основного скрипта
        from apply_to_vacancies import main as run_hh_automation
        
        # Запускаем автоматизацию
        logger.info("Запуск автоматизации HeadHunter...")
        result = run_hh_automation()
        
        # Если функция вернула результаты, используем их
        if result and isinstance(result, dict):
            return {
                'status': 'completed',
                'successful': result.get('successful', 0),
                'failed': result.get('failed', 0),
                'skipped': result.get('skipped', 0),
                'processed': result.get('processed', 0)
            }
        
        # Если результатов нет, читаем из файла прогресса
        progress_file = BASE_DIR / 'data' / 'progress.json'
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)
                return {
                    'status': 'completed',
                    'successful': progress.get('successful', 0),
                    'failed': progress.get('failed', 0),
                    'total': progress.get('total', 0)
                }
        
        return {
            'status': 'completed',
            'message': 'Автоматизация завершена'
        }
    except Exception as e:
        logger.error(f"Ошибка при выполнении автоматизации: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'status': 'error',
            'error': str(e)
        }

@app.route('/health', methods=['GET'])
def health():
    """Проверка работоспособности сервера"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/run', methods=['POST'])
def run_automation_endpoint():
    """Запускает автоматизацию HeadHunter"""
    try:
        # Проверяем авторизацию (опционально)
        auth_token = request.headers.get('Authorization')
        expected_token = os.getenv('HH_API_TOKEN', 'default_token_change_me')
        
        if auth_token != f'Bearer {expected_token}':
            return jsonify({
                'status': 'error',
                'error': 'Unauthorized'
            }), 401
        
        # Проверяем, не запущена ли уже автоматизация
        with execution_lock:
            if 'current_execution' in execution_results:
                last_execution = execution_results.get('current_execution')
                if last_execution and last_execution.get('status') == 'running':
                    return jsonify({
                        'status': 'error',
                        'error': 'Automation is already running'
                    }), 409
        
        # Запускаем автоматизацию в отдельном потоке
        execution_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        with execution_lock:
            execution_results['current_execution'] = {
                'execution_id': execution_id,
                'status': 'running',
                'started_at': datetime.now().isoformat()
            }
        
        def run_in_thread():
            result = run_automation()
            with execution_lock:
                execution_results['current_execution'] = {
                    'execution_id': execution_id,
                    'status': result.get('status', 'completed'),
                    'started_at': execution_results['current_execution']['started_at'],
                    'completed_at': datetime.now().isoformat(),
                    **result
                }
        
        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()
        
        return jsonify({
            'status': 'started',
            'execution_id': execution_id,
            'message': 'Automation started successfully'
        }), 202
        
    except Exception as e:
        logger.error(f"Ошибка при запуске автоматизации: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Получает статус последнего выполнения"""
    try:
        with execution_lock:
            if 'current_execution' in execution_results:
                return jsonify(execution_results['current_execution'])
            else:
                return jsonify({
                    'status': 'no_executions',
                    'message': 'No executions found'
                })
    except Exception as e:
        logger.error(f"Ошибка при получении статуса: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/status/<execution_id>', methods=['GET'])
def get_execution_status(execution_id):
    """Получает статус конкретного выполнения"""
    try:
        with execution_lock:
            current = execution_results.get('current_execution', {})
            if current.get('execution_id') == execution_id:
                return jsonify(current)
            else:
                return jsonify({
                    'status': 'not_found',
                    'message': f'Execution {execution_id} not found'
                }), 404
    except Exception as e:
        logger.error(f"Ошибка при получении статуса выполнения: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('HH_API_PORT', 5000))
    host = os.getenv('HH_API_HOST', '127.0.0.1')
    
    logger.info(f"Запуск HH API сервера на {host}:{port}")
    logger.info(f"Health check: http://{host}:{port}/health")
    logger.info(f"Run automation: POST http://{host}:{port}/run")
    logger.info(f"Get status: GET http://{host}:{port}/status")
    
    app.run(host=host, port=port, debug=False)

