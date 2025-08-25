import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'db/web_chat_bridge.db'
    LOG_PATH = os.environ.get('LOG_PATH') or 'logs'
    
    # Database configuration is loaded from system_config table
    # These are fallback values only - actual config comes from database
    DEFAULT_API_KEY = 'ObeyG1ant'
    DEFAULT_ADMIN_KEY = 'FreeUkra1ne'
    
    # Hardcoded constants (not in database)
    API_KEY_HEADER = 'Authorization'
    API_KEY_PREFIX = 'Bearer '
    MAX_MESSAGE_LENGTH = 10000
    MAX_SESSION_ID_LENGTH = 64
    MIN_MESSAGE_LENGTH = 1
    
    # Endpoint rate limits (can be overridden via database)
    ENDPOINT_RATE_LIMITS = {
        '/api/messages': 50,
        '/api/responses': 200,
        '/api/inbox': 120,
        '/api/outbox': 200,
        '/api/sessions': 20
    }
    
    @classmethod
    def load_from_database(cls, db_manager):
        """Load configuration values from database"""
        try:
            config_values = db_manager.get_all_config()
            for key, value in config_values.items():
                if hasattr(cls, key.upper()):
                    setattr(cls, key.upper(), value)
        except Exception as e:
            # Fall back to defaults if database is not available
            pass
