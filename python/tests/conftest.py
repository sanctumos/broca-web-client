"""
Pytest configuration and fixtures for Web Chat Bridge Flask API tests
Provides test database, app instances, and common test utilities
"""

import pytest
import tempfile
import os
import sqlite3
import json
from unittest.mock import Mock, patch
from flask import Flask
from app import create_app
from app.utils.database import DatabaseManager
from app.utils.rate_limiting import RateLimitManager

@pytest.fixture(scope="session")
def test_config():
    """Test configuration with temporary database"""
    class TestConfig:
        TESTING = True
        DATABASE_PATH = 'test_web_chat_bridge.db'
        DEFAULT_API_KEY = 'test_api_key_123'
        DEFAULT_ADMIN_KEY = 'test_admin_key_456'
        SECRET_KEY = 'test_secret_key_789'
    
    return TestConfig

@pytest.fixture(scope="function")
def app(test_config, test_db):
    """Create Flask app for testing"""
    app = create_app(test_config)
    return app

@pytest.fixture(scope="function")
def app_context(app):
    """Create Flask application context"""
    with app.app_context():
        yield app

@pytest.fixture(scope="function")
def request_context(app):
    """Create Flask request context"""
    with app.test_request_context():
        yield app

@pytest.fixture(scope="function")
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture(scope="function")
def test_db():
    """Create test database with sample data"""
    db_path = 'test_web_chat_bridge.db'
    
    # Clean up any existing test database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create fresh test database using the application's DatabaseManager
    from app.utils.database import DatabaseManager
    
    # Create a temporary database manager that can find the SQL file
    # We need to use the actual project directory for the SQL file
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sql_file_path = os.path.join(project_root, 'db', 'init_database.sql')
    
    # Create the database manager and manually execute the SQL
    db_manager = DatabaseManager(db_path)
    
    # Manually read and execute the SQL file
    if os.path.exists(sql_file_path):
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        with open(sql_file_path, 'r') as f:
            init_script = f.read()
        
        # Execute the entire script as one statement to ensure proper order
        try:
            cursor.executescript(init_script)
            conn.commit()
        except Exception as e:
            print(f"Error executing init script: {e}")
            # Fallback to basic schema
            db_manager.init_database()
        finally:
            conn.close()
    else:
        # Fallback to basic schema if SQL file not found
        db_manager.init_database()
    
    # Insert test configuration data
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO system_config (config_key, config_value, description) VALUES 
        ('api_key', 'test_api_key_123', 'Test API key'),
        ('admin_key', 'test_admin_key_456', 'Test admin key'),
        ('session_timeout', '1800', 'Test session timeout'),
        ('max_message_length', '10000', 'Test max message length'),
        ('rate_limit_window', '3600', 'Test rate limit window')
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup - add delay to ensure connections are fully closed
    import time
    time.sleep(0.1)  # Small delay to ensure SQLite connections are closed
    
    # Try to remove the file, but don't fail if it's still locked
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except PermissionError:
        # File might still be locked, that's okay for tests
        pass

@pytest.fixture(scope="function")
def db_manager(test_db):
    """Create database manager instance for testing"""
    # Create the manager directly with the test database path
    manager = DatabaseManager(test_db)
    yield manager

@pytest.fixture(scope="function")
def rate_limiter(test_db):
    """Create rate limiter instance for testing"""
    # Create the database manager and rate limiter directly
    db_manager = DatabaseManager(test_db)
    limiter = RateLimitManager(db_manager)
    yield limiter

@pytest.fixture
def auth_headers():
    """Common authentication headers"""
    return {
        'api_key': {'Authorization': 'Bearer test_api_key_123'},
        'admin_key': {'Authorization': 'Bearer test_admin_key_456'},
        'invalid_key': {'Authorization': 'Bearer invalid_key'},
        'no_auth': {}
    }

@pytest.fixture
def sample_messages():
    """Sample message data for testing"""
    return [
        {
            'session_id': 'session_test_1',
            'message': 'Test message 1',
            'timestamp': '2025-08-24T16:00:00'
        },
        {
            'session_id': 'session_test_2', 
            'message': 'Test message 2',
            'timestamp': '2025-08-24T16:01:00'
        }
    ]

@pytest.fixture
def sample_responses():
    """Sample response data for testing"""
    return [
        {
            'session_id': 'session_test_1',
            'response': 'Test response 1',
            'message_id': 1
        },
        {
            'session_id': 'session_test_1',
            'response': 'Test response 2', 
            'message_id': 2
        }
    ]

@pytest.fixture
def mock_request():
    """Mock request object for testing"""
    mock_req = Mock()
    mock_req.remote_addr = '127.0.0.1'
    mock_req.headers = {'User-Agent': 'test_agent'}
    mock_req.method = 'POST'
    mock_req.get_json.return_value = {
        'session_id': 'session_test_1',
        'message': 'Test message'
    }
    mock_req.args = {}
    return mock_req
