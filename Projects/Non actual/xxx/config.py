"""
Configuration module for Копия иксуюемся.
Loads configuration from env_vars.txt file.
"""
from typing import Dict, Optional
from dotenv import load_dotenv
import os

def load_config() -> Dict[str, Optional[str]]:
    """
    Load configuration from env_vars.txt file.
    
    Returns:
        Dictionary with configuration values
    """
    load_dotenv(dotenv_path='env_vars.txt')
    return {
        # Bot configuration (for management bot)
        'BOT_TOKEN': os.getenv('BOT_TOKEN'),
        'ADMIN_ID': os.getenv('ADMIN_ID'),
        
        # Pyrogram Userbot configuration (for reading messages)
        'API_ID': os.getenv('API_ID'),
        'API_HASH': os.getenv('API_HASH'),
        'PHONE_NUMBER': os.getenv('PHONE_NUMBER'),
        
        # Channel configuration
        'SOURCE_CHANNEL_ID': os.getenv('SOURCE_CHANNEL_ID'),
        'TARGET_CHANNEL_ID': os.getenv('TARGET_CHANNEL_ID'),
        
        # Server configuration (optional)
        'SERVER_IP': os.getenv('SERVER_IP', ''),
        'SERVER_USER': os.getenv('SERVER_USER', 'root'),
        'SERVER_PASSWORD': os.getenv('SERVER_PASSWORD', ''),
    }
