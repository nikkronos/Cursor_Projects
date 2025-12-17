from typing import Dict, Optional
from dotenv import load_dotenv
import os

def load_config() -> Dict[str, Optional[str]]:
    load_dotenv(dotenv_path='env_vars.txt')
    return {
        'BOT_TOKEN': os.getenv('BOT_TOKEN'),
        'GROUP_CHAT_ID': os.getenv('GROUP_CHAT_ID'),
        'ADMIN_ID': os.getenv('ADMIN_ID'),
        'GROUP_INVITE_LINK': os.getenv('GROUP_INVITE_LINK', '')
    }
