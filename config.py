from dotenv import load_dotenv
import os

def load_config():
    load_dotenv(dotenv_path='env_vars.txt')
    return {
        'BOT_TOKEN': os.getenv('BOT_TOKEN'),
        'DB_NAME': os.getenv('DB_NAME'),
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD'),
        'DB_HOST': os.getenv('DB_HOST'),
        'GROUP_CHAT_ID': os.getenv('GROUP_CHAT_ID'),
        'ADMIN_ID': os.getenv('ADMIN_ID')
    }
