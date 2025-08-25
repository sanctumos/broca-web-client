# Flask Implementation Guide - Web Chat Bridge

## Project Structure

```
web_chat_bridge_flask/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── session.py
│   │   ├── message.py
│   │   └── response.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── auth.py
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── templates/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── rate_limiting.py
│   │   └── logging.py
│   └── templates/
│       ├── admin.html
│       └── base.html
├── db/
│   ├── init_database.sql
│   └── web_chat_bridge.db
├── logs/
├── config.py
├── requirements.txt
└── run.py
```

**Note:** The original PHP system has been moved to the `php/` folder for reference during development.

## Core Dependencies

```txt
Flask==2.3.3
Flask-CORS==4.0.0
python-dotenv==1.0.0
Werkzeug==2.3.7
```

## Main Application (`app/__init__.py`)

```python
from flask import Flask
from flask_cors import CORS
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    return app
```

## Configuration (`config.py`)

```python
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
```

## API Routes (`app/api/routes.py`)

```python
from flask import Blueprint, request, jsonify
from app.utils.database import DatabaseManager
from app.utils.rate_limiting import RateLimitManager
from app.api.auth import require_auth, require_admin_auth
from app.utils.logging import log_api_request
import json

bp = Blueprint('api', __name__)
db = DatabaseManager()
rate_limiter = RateLimitManager(db)

@bp.route('/messages', methods=['POST'])
def handle_messages():
    """Handle message submission"""
    # Rate limiting
    if not rate_limiter.check_rate_limit(request.remote_addr, '/api/messages', 50):
        return jsonify({
            'success': False,
            'error': 'Rate limit exceeded',
            'code': 429
        }), 429
    
    # Get and validate input
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON'}), 400
    
    session_id = data.get('session_id')
    message = data.get('message')
    
    if not session_id or not message:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    # Validate session ID format
    if not validate_session_id(session_id):
        return jsonify({'success': False, 'error': 'Invalid session ID'}), 400
    
    try:
        # Create/update session
        if not db.session_exists(session_id):
            db.create_session(session_id, request.remote_addr)
        
        # Store message
        message_id = db.create_message(session_id, message)
        
        # Get or create UID
        uid_data = db.get_or_create_uid(session_id, request.remote_addr)
        
        log_api_request('/api/messages', 'POST')
        
        return jsonify({
            'success': True,
            'message': 'Message received',
            'data': {
                'message_id': message_id,
                'session_id': session_id,
                'uid': uid_data['uid'],
                'is_new_user': uid_data['is_new']
            }
        })
        
    except Exception as e:
        log_api_request('/api/messages', 'POST', error=str(e))
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@bp.route('/inbox', methods=['GET'])
@require_auth
def handle_inbox():
    """Get unprocessed messages for plugin"""
    # Rate limiting
    if not rate_limiter.check_rate_limit(request.remote_addr, '/api/inbox', 120):
        return jsonify({'success': False, 'error': 'Rate limit exceeded'}), 429
    
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    since = request.args.get('since')
    
    try:
        messages = db.get_unprocessed_messages(limit, offset, since)
        total = db.get_unprocessed_message_count(since)
        
        # Mark messages as processed
        if messages:
            message_ids = [msg['id'] for msg in messages]
            db.mark_messages_processed(message_ids)
        
        log_api_request('/api/inbox', 'GET')
        
        return jsonify({
            'success': True,
            'data': {
                'messages': messages,
                'pagination': {
                    'total': total,
                    'limit': limit,
                    'offset': offset,
                    'has_more': (offset + limit) < total
                }
            }
        })
        
    except Exception as e:
        log_api_request('/api/inbox', 'GET', error=str(e))
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@bp.route('/outbox', methods=['POST'])
@require_auth
def handle_outbox():
    """Submit plugin response"""
    # Rate limiting
    if not rate_limiter.check_rate_limit(request.remote_addr, '/api/outbox', 200):
        return jsonify({'success': False, 'error': 'Rate limit exceeded'}), 429
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON'}), 400
    
    session_id = data.get('session_id')
    response = data.get('response')
    message_id = data.get('message_id')
    
    if not session_id or not response:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    try:
        # Validate session
        if not db.session_exists(session_id):
            return jsonify({'success': False, 'error': 'Invalid session'}), 400
        
        # Store response
        response_id = db.create_response(session_id, response, message_id)
        
        log_api_request('/api/outbox', 'POST')
        
        return jsonify({
            'success': True,
            'message': 'Response sent successfully',
            'data': {
                'response_id': response_id,
                'session_id': session_id
            }
        })
        
    except Exception as e:
        log_api_request('/api/outbox', 'POST', error=str(e))
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@bp.route('/responses', methods=['GET'])
def handle_responses():
    """Get session responses"""
    session_id = request.args.get('session_id')
    since = request.args.get('since')
    
    if not session_id:
        return jsonify({'success': False, 'error': 'Missing session_id'}), 400
    
    try:
        # Create session if doesn't exist
        if not db.session_exists(session_id):
            db.create_session(session_id, request.remote_addr)
        
        responses = db.get_session_responses(session_id, since)
        
        log_api_request('/api/responses', 'GET')
        
        return jsonify({
            'success': True,
            'data': {
                'session_id': session_id,
                'responses': responses
            }
        })
        
    except Exception as e:
        log_api_request('/api/responses', 'GET', error=str(e))
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
```

## Admin Routes (`app/admin/routes.py`)

```python
from flask import Blueprint, request, jsonify, render_template
from app.utils.database import DatabaseManager
from app.api.auth import require_admin_auth
from app.utils.logging import log_admin_action

bp = Blueprint('admin', __name__)
db = DatabaseManager()

@bp.route('/')
def admin_interface():
    """Admin interface main page"""
    return render_template('admin.html')

@bp.route('/api/sessions')
@require_admin_auth
def get_sessions():
    """Get active sessions"""
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    active = request.args.get('active', 'true')
    
    try:
        sessions = db.get_active_sessions(limit, offset, active == 'true')
        total = db.get_session_count(active == 'true')
        
        return jsonify({
            'success': True,
            'data': {
                'sessions': sessions,
                'pagination': {
                    'total': total,
                    'limit': limit,
                    'offset': offset,
                    'has_more': (offset + limit) < total
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/config', methods=['GET', 'POST'])
@require_admin_auth
def handle_config():
    """Get or update configuration"""
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'data': {
                'api_key': current_app.config['API_KEY'],
                'admin_key': current_app.config['ADMIN_KEY'],
                'session_timeout': current_app.config['SESSION_TIMEOUT']
            }
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Invalid JSON'}), 400
        
        try:
            # Update configuration
            db.update_config(data)
            log_admin_action('Configuration updated', request.remote_addr)
            
            return jsonify({
                'success': True,
                'message': 'Configuration updated successfully'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/cleanup', methods=['POST'])
@require_admin_auth
def manual_cleanup():
    """Manual cleanup of inactive sessions"""
    try:
        cleaned_count = db.cleanup_inactive_sessions()
        log_admin_action(f'Manual cleanup: {cleaned_count} sessions', request.remote_addr)
        
        return jsonify({
            'success': True,
            'data': {
                'cleaned_count': cleaned_count,
                'message': f'Cleaned up {cleaned_count} inactive sessions'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/clear_data', methods=['POST'])
@require_admin_auth
def clear_all_data():
    """Clear all data (dangerous operation)"""
    try:
        db.clear_all_data()
        log_admin_action('All data cleared', request.remote_addr)
        
        return jsonify({
            'success': True,
            'message': 'All data cleared successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

## Authentication (`app/api/auth.py`)

```python
from functools import wraps
from flask import request, jsonify, current_app
from app.utils.logging import log_auth_attempt

def require_auth(f):
    """Require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            log_auth_attempt('Missing API key', request.remote_addr)
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        api_key = auth_header[7:]  # Remove 'Bearer ' prefix
        if api_key != current_app.config['API_KEY']:
            log_auth_attempt('Invalid API key', request.remote_addr)
            return jsonify({'success': False, 'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def require_admin_auth(f):
    """Require admin password authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            log_auth_attempt('Missing admin key', request.remote_addr)
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        admin_key = auth_header[7:]  # Remove 'Bearer ' prefix
        if admin_key != current_app.config['ADMIN_KEY']:
            log_auth_attempt('Invalid admin key', request.remote_addr)
            return jsonify({'success': False, 'error': 'Invalid admin key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function
```

## Utility Functions

### Database Manager (`app/utils/database.py`)
```python
import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            from flask import current_app
            db_path = current_app.config['DATABASE_PATH']
        
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_database()
    
    def ensure_db_directory(self):
        """Ensure database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def session_exists(self, session_id: str) -> bool:
        """Check if session exists"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM web_chat_sessions WHERE id = ?", (session_id,))
            return cursor.fetchone() is not None
        finally:
            conn.close()
    
    def create_session(self, session_id: str, ip_address: str = None):
        """Create new session"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO web_chat_sessions (id, created_at, last_active, ip_address)
                VALUES (?, datetime('now'), datetime('now'), ?)
            """, (session_id, ip_address))
            conn.commit()
        finally:
            conn.close()
    
    def create_message(self, session_id: str, message: str) -> int:
        """Create new message"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO web_chat_messages (session_id, message, timestamp)
                VALUES (?, ?, datetime('now'))
            """, (session_id, message))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_unprocessed_messages(self, limit: int, offset: int, since: str = None) -> List[Dict]:
        """Get unprocessed messages"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            where_conditions = ["processed = 0"]
            params = []
            
            if since:
                where_conditions.append("timestamp > ?")
                params.append(since)
            
            where_clause = " AND ".join(where_conditions)
            
            sql = f"""
                SELECT m.id, m.session_id, m.message, m.timestamp, s.uid
                FROM web_chat_messages m
                LEFT JOIN web_chat_sessions s ON m.session_id = s.id
                WHERE {where_clause}
                ORDER BY m.timestamp ASC
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])
            
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def mark_messages_processed(self, message_ids: List[int]):
        """Mark messages as processed"""
        if not message_ids:
            return
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            placeholders = ','.join(['?' for _ in message_ids])
            sql = f"UPDATE web_chat_messages SET processed = 1 WHERE id IN ({placeholders})"
            cursor.execute(sql, message_ids)
            conn.commit()
        finally:
            conn.close()
    
    def cleanup_inactive_sessions(self) -> int:
        """Clean up inactive sessions"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM web_chat_sessions 
                WHERE last_active < datetime('now', '-1800 seconds')
            """)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
```

## Running the Application

### Entry Point (`run.py`)
```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
```

### Environment Variables (`.env`)
```bash
FLASK_APP=run.py
FLASK_ENV=development
WEB_CHAT_API_KEY=your_api_key_here
WEB_CHAT_ADMIN_KEY=your_admin_key_here
DATABASE_PATH=db/web_chat_bridge.db
LOG_PATH=logs
```

### Startup Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app.utils.database import DatabaseManager; DatabaseManager()"

# Run application
python run.py
```

## Testing

### Test Configuration
```python
# tests/conftest.py
import pytest
import tempfile
import os
from app import create_app
from app.utils.database import DatabaseManager

@pytest.fixture
def app():
    """Create test application"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['DATABASE_PATH'] = ':memory:'
    
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def db():
    """Create test database"""
    return DatabaseManager(':memory:')
```

### Example Test
```python
# tests/test_api.py
def test_message_submission(client):
    """Test message submission endpoint"""
    response = client.post('/api/v1/messages', json={
        'session_id': 'test_session_123',
        'message': 'Hello, world!'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'message_id' in data['data']
```

This implementation guide provides the core structure and code needed to build the Flask port. The development team should follow the detailed specifications in the other documentation files to ensure 100% functional parity.
