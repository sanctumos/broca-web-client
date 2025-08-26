"""
Unit tests for API route handlers
Tests all API endpoints with mocked dependencies
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, request
from app.api.routes import (
    handle_messages, handle_inbox, handle_outbox, handle_responses,
    handle_sessions, handle_config, handle_cleanup, validate_session_id,
    validate_message, require_auth_internal, require_admin_auth_internal
)

class TestAPIValidation:
    """Test input validation functions"""
    
    def test_validate_session_id_valid(self):
        """Test valid session ID validation"""
        valid_ids = [
            'session_test_123',
            'session_abc123',
            'session_123_abc',
            'session_' + 'a' * 50  # 50 chars total
        ]
        
        for session_id in valid_ids:
            assert validate_session_id(session_id) is True
    
    def test_validate_session_id_invalid(self):
        """Test invalid session ID validation"""
        invalid_ids = [
            'invalid_session',
            'session',  # Too short
            'session_' + 'a' * 60,  # Too long
            'session-123',  # Invalid characters
            'session 123',  # Spaces
            '',  # Empty
            None  # None
        ]
        
        for session_id in invalid_ids:
            assert validate_session_id(session_id) is False
    
    def test_validate_message_valid(self):
        """Test valid message validation"""
        valid_messages = [
            'Hello world',
            'A',  # Single character
            'a' * 10000,  # Maximum length
            'Message with numbers 123',
            'Message with symbols !@#$%'
        ]
        
        for message in valid_messages:
            assert validate_message(message) is True
    
    def test_validate_message_invalid(self):
        """Test invalid message validation"""
        invalid_messages = [
            '',  # Empty
            '   ',  # Whitespace only
            'a' * 10001,  # Too long
            None,  # None
            123,  # Number
            [],  # List
            {}  # Dict
        ]
        
        for message in invalid_messages:
            assert validate_message(message) is False

class TestAPIAuthentication:
    """Test authentication functions"""
    
    def test_require_auth_internal_valid(self, app_context, request_context, db_manager):
        """Test valid API key authentication"""
        with patch('app.api.routes.request') as mock_request:
            mock_request.headers = {'Authorization': 'Bearer test_api_key_123'}
            
            with patch('app.api.routes.DatabaseManager') as mock_db_class:
                mock_db_class.return_value = db_manager
                with patch('app.api.routes.current_app') as mock_app:
                    mock_app.config = {'DEFAULT_API_KEY': 'test_api_key_123', 'DEFAULT_ADMIN_KEY': 'test_admin_key_456'}
                    
                    result = require_auth_internal()
                    assert result is None  # Authentication successful
    
    def test_require_auth_internal_invalid_key(self, app_context, request_context, db_manager):
        """Test invalid API key authentication"""
        with patch('app.api.routes.request') as mock_request:
            mock_request.headers = {'Authorization': 'Bearer invalid_key'}
            
            with patch('app.api.routes.DatabaseManager') as mock_db_class:
                mock_db_class.return_value = db_manager
                with patch('app.api.routes.current_app') as mock_app:
                    mock_app.config = {'DEFAULT_API_KEY': 'test_api_key_123', 'DEFAULT_ADMIN_KEY': 'test_admin_key_456'}
                    
                    result = require_auth_internal()
                    assert result is not None  # Authentication failed
                    assert result[1] == 401  # Unauthorized status
    
    def test_require_auth_internal_missing_header(self, app_context, request_context, db_manager):
        """Test missing authorization header"""
        with patch('app.api.routes.request') as mock_request:
            mock_request.headers = {}
            
            result = require_auth_internal()
            assert result is not None  # Authentication failed
            assert result[1] == 401  # Unauthorized status
    
    def test_require_auth_internal_malformed_header(self, app_context, request_context, db_manager):
        """Test malformed authorization header"""
        with patch('app.api.routes.request') as mock_request:
            mock_request.headers = {'Authorization': 'InvalidFormat'}
            
            result = require_auth_internal()
            assert result is not None  # Authentication failed
            assert result[1] == 401  # Unauthorized status
    
    def test_require_admin_auth_internal_valid(self, app_context, request_context, db_manager):
        """Test valid admin key authentication"""
        with patch('app.api.routes.request') as mock_request:
            mock_request.headers = {'Authorization': 'Bearer test_admin_key_456'}
            
            with patch('app.api.routes.DatabaseManager') as mock_db_class:
                mock_db_class.return_value = db_manager
                with patch('app.api.routes.current_app') as mock_app:
                    mock_app.config = {'DEFAULT_ADMIN_KEY': 'test_admin_key_456'}
                    
                    result = require_admin_auth_internal()
                    assert result is None  # Authentication successful

class TestAPIMessageHandling:
    """Test message handling functions"""
    
    def test_handle_messages_success(self, app_context, request_context, db_manager):
        """Test successful message handling"""
        # Create a mock request object that behaves like Flask's request
        mock_request = Mock()
        mock_request.method = 'POST'
        mock_request.get_json.return_value = {
            'session_id': 'session_test_123',
            'message': 'Test message'
        }
        mock_request.remote_addr = '127.0.0.1'
        mock_request.headers = {'User-Agent': 'test_agent'}
        
        with patch('app.api.routes.request', mock_request):
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_get_db.return_value = db_manager
                with patch('app.api.routes.get_rate_limiter') as mock_get_rate_limiter:
                    mock_rate_limiter = Mock()
                    mock_rate_limiter.check_rate_limit.return_value = True
                    mock_get_rate_limiter.return_value = mock_rate_limiter
                    
                    # Mock database methods
                    with patch.object(db_manager, 'session_exists') as mock_session_exists:
                        mock_session_exists.return_value = False
                        with patch.object(db_manager, 'create_session') as mock_create_session:
                            mock_create_session.return_value = 'test_uid_123'
                            with patch.object(db_manager, 'get_or_create_uid') as mock_get_uid:
                                mock_get_uid.return_value = {'uid': 'test_uid_123', 'is_new': True}
                                with patch.object(db_manager, 'create_message') as mock_create_message:
                                    mock_create_message.return_value = 123
                                    
                                    response = handle_messages()
                                    # Check if response is a tuple (status_code, data) or JSONResponse
                                    if hasattr(response, 'status_code'):
                                        assert response.status_code == 200
                                    else:
                                        assert response[1] == 200
    
    def test_handle_messages_rate_limit_exceeded(self, app_context, request_context, db_manager):
        """Test message handling when rate limit is exceeded"""
        with patch('app.api.routes.request') as mock_request:
            mock_request.method = 'POST'
            mock_request.get_json.return_value = {
                'session_id': 'session_test_123',
                'message': 'Test message'
            }
            mock_request.remote_addr = '127.0.0.1'
            
            with patch('app.api.routes.DatabaseManager') as mock_db_class:
                mock_db_class.return_value = db_manager
                with patch('app.api.routes.RateLimitManager') as mock_rate_limiter_class:
                    mock_rate_limiter = Mock()
                    mock_rate_limiter.check_rate_limit.return_value = False
                    mock_rate_limiter_class.return_value = mock_rate_limiter
                    
                    response = handle_messages()
                    assert response[1] == 429  # Rate limit exceeded status
    
    def test_handle_messages_invalid_session_id(self, app_context, request_context, db_manager):
        """Test message handling with invalid session ID"""
        # Create a mock request object that behaves like Flask's request
        mock_request = Mock()
        mock_request.method = 'POST'
        mock_request.get_json.return_value = {
            'session_id': 'invalid_session',
            'message': 'Test message'
        }
        mock_request.remote_addr = '127.0.0.1'
        mock_request.headers = {'User-Agent': 'test_agent'}
        
        with patch('app.api.routes.request', mock_request):
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_get_db.return_value = db_manager
                with patch('app.api.routes.get_rate_limiter') as mock_get_rate_limiter:
                    mock_rate_limiter = Mock()
                    mock_rate_limiter.check_rate_limit.return_value = True
                    mock_get_rate_limiter.return_value = mock_rate_limiter
                    
                    response = handle_messages()
                    if hasattr(response, 'status_code'):
                        assert response.status_code == 400
                    else:
                        assert response[1] == 400
    
    def test_handle_messages_missing_fields(self, app_context, request_context, db_manager):
        """Test message handling with missing required fields"""
        # Create a mock request object that behaves like Flask's request
        mock_request = Mock()
        mock_request.method = 'POST'
        mock_request.get_json.return_value = {
            'session_id': 'session_test_123'
            # Missing 'message' field
        }
        mock_request.remote_addr = '127.0.0.1'
        mock_request.headers = {'User-Agent': 'test_agent'}
        
        with patch('app.api.routes.request', mock_request):
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_get_db.return_value = db_manager
                with patch('app.api.routes.get_rate_limiter') as mock_get_rate_limiter:
                    mock_rate_limiter = Mock()
                    mock_rate_limiter.check_rate_limit.return_value = True
                    mock_get_rate_limiter.return_value = mock_rate_limiter
                    
                    response = handle_messages()
                    if hasattr(response, 'status_code'):
                        assert response.status_code == 400
                    else:
                        assert response[1] == 400

class TestAPIInboxHandling:
    """Test inbox handling functions"""
    
    def test_handle_inbox_success(self, app_context, request_context, db_manager):
        """Test successful inbox retrieval"""
        with patch('app.api.routes.request') as mock_request:
            mock_request.method = 'GET'
            mock_request.args = {}
            mock_request.headers = {'Authorization': 'Bearer test_api_key_123'}
            mock_request.remote_addr = '127.0.0.1'
            
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_get_db.return_value = db_manager
                with patch('app.api.routes.get_rate_limiter') as mock_get_rate_limiter:
                    mock_rate_limiter = Mock()
                    mock_rate_limiter.check_rate_limit.return_value = True
                    mock_get_rate_limiter.return_value = mock_rate_limiter
                    
                    # Mock database methods
                    with patch.object(db_manager, 'get_unprocessed_messages') as mock_get_messages:
                        mock_get_messages.return_value = []
                        with patch.object(db_manager, 'get_unprocessed_message_count') as mock_get_count:
                            mock_get_count.return_value = 0
                            with patch.object(db_manager, 'mark_messages_processed') as mock_mark_processed:
                                
                                response = handle_inbox()
                                if hasattr(response, 'status_code'):
                                    assert response.status_code == 200
                                else:
                                    assert response[1] == 200
    
    def test_handle_inbox_unauthorized(self, app_context, request_context, db_manager):
        """Test inbox retrieval without authentication"""
        with patch('app.api.routes.request') as mock_request:
            mock_request.method = 'GET'
            mock_request.args = {}
            mock_request.headers = {}  # No authorization header
            mock_request.remote_addr = '127.0.0.1'
            
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_get_db.return_value = db_manager
                with patch('app.api.routes.get_rate_limiter') as mock_get_rate_limiter:
                    mock_rate_limiter = Mock()
                    mock_rate_limiter.check_rate_limit.return_value = True
                    mock_get_rate_limiter.return_value = mock_rate_limiter
                    
                    response = handle_inbox()
                    if hasattr(response, 'status_code'):
                        assert response.status_code == 401
                    else:
                        assert response[1] == 401

class TestAPIOutboxHandling:
    """Test outbox handling functions"""
    
    def test_handle_outbox_success(self, app_context, request_context, db_manager):
        """Test successful outbox retrieval"""
        # Create a mock request object that behaves like Flask's request
        mock_request = Mock()
        mock_request.method = 'POST'
        mock_request.get_json.return_value = {
            'session_id': 'session_test_123',
            'response': 'Test response message'  # Add the required response field
        }
        mock_request.headers = {'Authorization': 'Bearer test_api_key_123', 'User-Agent': 'test_agent'}
        mock_request.remote_addr = '127.0.0.1'
        
        with patch('app.api.routes.request', mock_request):
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_get_db.return_value = db_manager
                with patch('app.api.routes.get_rate_limiter') as mock_get_rate_limiter:
                    mock_rate_limiter = Mock()
                    mock_rate_limiter.check_rate_limit.return_value = True
                    mock_get_rate_limiter.return_value = mock_rate_limiter
                    
                    # Mock database methods
                    with patch.object(db_manager, 'session_exists') as mock_session_exists:
                        mock_session_exists.return_value = True
                        with patch.object(db_manager, 'create_response') as mock_create_response:
                            mock_create_response.return_value = 456
                            
                            response = handle_outbox()
                            if hasattr(response, 'status_code'):
                                assert response.status_code == 200
                            else:
                                assert response[1] == 200
    
    def test_handle_outbox_invalid_session(self, app_context, request_context, db_manager):
        """Test outbox retrieval with invalid session"""
        # Create a mock request object that behaves like Flask's request
        mock_request = Mock()
        mock_request.method = 'POST'
        mock_request.get_json.return_value = {'session_id': 'invalid_session'}
        mock_request.headers = {'Authorization': 'Bearer test_api_key_123', 'User-Agent': 'test_agent'}
        mock_request.remote_addr = '127.0.0.1'
        
        with patch('app.api.routes.request', mock_request):
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_get_db.return_value = db_manager
                with patch('app.api.routes.get_rate_limiter') as mock_get_rate_limiter:
                    mock_rate_limiter = Mock()
                    mock_rate_limiter.check_rate_limit.return_value = True
                    mock_get_rate_limiter.return_value = mock_rate_limiter
                    
                    # Mock database methods
                    with patch.object(db_manager, 'session_exists') as mock_session_exists:
                        mock_session_exists.return_value = False
                        
                        response = handle_outbox()
                        if hasattr(response, 'status_code'):
                            assert response.status_code == 400
                        else:
                            assert response[1] == 400

class TestAPIResponseHandling:
    """Test response handling functions"""
    
    def test_handle_responses_success(self, app_context, request_context, db_manager):
        """Test successful response retrieval"""
        with patch('app.api.routes.request') as mock_request:
            mock_request.method = 'GET'
            mock_request.args = {'session_id': 'session_test_123'}
            mock_request.remote_addr = '127.0.0.1'
            
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_get_db.return_value = db_manager
                with patch('app.api.routes.get_rate_limiter') as mock_get_rate_limiter:
                    mock_rate_limiter = Mock()
                    mock_rate_limiter.check_rate_limit.return_value = True
                    mock_get_rate_limiter.return_value = mock_rate_limiter
                    
                    # Mock database methods
                    with patch.object(db_manager, 'session_exists') as mock_session_exists:
                        mock_session_exists.return_value = False
                        with patch.object(db_manager, 'create_session') as mock_create_session:
                            mock_create_session.return_value = 'test_uid_123'
                            with patch.object(db_manager, 'get_session_responses') as mock_get_responses:
                                mock_get_responses.return_value = []
                                
                                response = handle_responses()
                                if hasattr(response, 'status_code'):
                                    assert response.status_code == 200
                                else:
                                    assert response[1] == 200

class TestAPIAdminHandling:
    """Test admin handling functions"""
    
    def test_handle_sessions_success(self, app_context, request_context, db_manager):
        """Test successful sessions retrieval"""
        with patch('app.api.routes.request') as mock_request:
            mock_request.method = 'GET'
            mock_request.args = {}
            mock_request.headers = {'Authorization': 'Bearer test_admin_key_456'}
            mock_request.remote_addr = '127.0.0.1'
            
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_get_db.return_value = db_manager
                with patch('app.api.routes.get_rate_limiter') as mock_get_rate_limiter:
                    mock_rate_limiter = Mock()
                    mock_rate_limiter.check_rate_limit.return_value = True
                    mock_get_rate_limiter.return_value = mock_rate_limiter
                    
                    # Mock database methods
                    with patch.object(db_manager, 'get_active_sessions') as mock_get_sessions:
                        mock_get_sessions.return_value = []
                        with patch.object(db_manager, 'get_session_count') as mock_get_count:
                            mock_get_count.return_value = 0
                            
                            response = handle_sessions()
                            if hasattr(response, 'status_code'):
                                assert response.status_code == 200
                            else:
                                assert response[1] == 200
    
    def test_handle_config_get_success(self, app_context, request_context, db_manager):
        """Test successful config retrieval"""
        with patch('app.api.routes.request') as mock_request:
            mock_request.method = 'GET'
            mock_request.args = {}
            mock_request.headers = {'Authorization': 'Bearer test_admin_key_456'}
            mock_request.remote_addr = '127.0.0.1'
            
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_get_db.return_value = db_manager
                with patch('app.api.routes.get_rate_limiter') as mock_get_rate_limiter:
                    mock_rate_limiter = Mock()
                    mock_rate_limiter.check_rate_limit.return_value = True
                    mock_get_rate_limiter.return_value = mock_rate_limiter
                    
                    # Mock database methods
                    with patch.object(db_manager, 'get_all_config') as mock_get_config:
                        mock_get_config.return_value = {'api_key': 'test_key'}
                        
                        response = handle_config()
                        if hasattr(response, 'status_code'):
                            assert response.status_code == 200
                        else:
                            assert response[1] == 200
    
    def test_handle_config_update_success(self, app_context, request_context, db_manager):
        """Test successful config update"""
        with patch('app.api.routes.request') as mock_request:
            mock_request.method = 'POST'
            mock_request.get_json.return_value = {'api_key': 'new_key'}
            mock_request.headers = {'Authorization': 'Bearer test_admin_key_456'}
            mock_request.remote_addr = '127.0.0.1'
            
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_get_db.return_value = db_manager
                with patch('app.api.routes.get_rate_limiter') as mock_get_rate_limiter:
                    mock_rate_limiter = Mock()
                    mock_rate_limiter.check_rate_limit.return_value = True
                    mock_get_rate_limiter.return_value = mock_rate_limiter
                    
                    # Mock database methods
                    with patch.object(db_manager, 'update_config') as mock_update_config:
                        mock_update_config.return_value = None
                        
                        response = handle_config()
                        if hasattr(response, 'status_code'):
                            assert response.status_code == 200
                        else:
                            assert response[1] == 200

class TestAPICleanupHandling:
    """Test cleanup handling functions"""
    
    def test_handle_cleanup_success(self, app_context, request_context, db_manager):
        """Test successful cleanup operation"""
        with patch('app.api.routes.request') as mock_request:
            mock_request.method = 'POST'
            mock_request.headers = {'Authorization': 'Bearer test_admin_key_456'}
            mock_request.remote_addr = '127.0.0.1'
            
            with patch('app.api.routes.get_db') as mock_get_db:
                mock_get_db.return_value = db_manager
                with patch('app.api.routes.get_rate_limiter') as mock_get_rate_limiter:
                    mock_rate_limiter = Mock()
                    mock_rate_limiter.check_rate_limit.return_value = True
                    mock_get_rate_limiter.return_value = mock_rate_limiter
                    
                    # Mock database methods
                    with patch.object(db_manager, 'cleanup_inactive_sessions') as mock_cleanup:
                        mock_cleanup.return_value = 5
                        
                        response = handle_cleanup()
                        if hasattr(response, 'status_code'):
                            assert response.status_code == 200
                        else:
                            assert response[1] == 200

    # Direct route tests to cover lines 40-70
    def test_handle_messages_direct_route(self, app, db_manager):
        """Test direct route for messages to cover line 68"""
        # Create a test session first
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO web_chat_sessions (id, last_active) 
            VALUES ('session_test_123', datetime('now'))
        """)
        conn.commit()
        conn.close()
        
        with app.test_client() as client:
            response = client.post('/api/v1/messages', 
                                json={'session_id': 'session_test_123', 'message': 'test message'})
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
    
    def test_handle_inbox_direct_route(self, app, db_manager):
        """Test direct route for inbox to cover line 73"""
        # Create a test session and message first
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO web_chat_sessions (id, last_active) 
            VALUES ('session_test_456', datetime('now'))
        """)
        cursor.execute("""
            INSERT OR REPLACE INTO web_chat_messages (session_id, message, timestamp) 
            VALUES ('session_test_456', 'test message', datetime('now'))
        """)
        conn.commit()
        conn.close()
        
        with app.test_client() as client:
            response = client.get('/api/v1/inbox', 
                               headers={'Authorization': 'Bearer test_api_key_123'})
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
    
    def test_handle_outbox_direct_route(self, app, db_manager):
        """Test direct route for outbox to cover line 78"""
        # Create a test session and message first
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO web_chat_sessions (id, last_active) 
            VALUES ('session_test_789', datetime('now'))
        """)
        cursor.execute("""
            INSERT OR REPLACE INTO web_chat_messages (session_id, message, timestamp) 
            VALUES ('session_test_789', 'test message', datetime('now'))
        """)
        conn.commit()
        conn.close()
        
        with app.test_client() as client:
            response = client.post('/api/v1/outbox', 
                                json={'session_id': 'session_test_789', 'response': 'test response'},
                                headers={'Authorization': 'Bearer test_api_key_123'})
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
    
    def test_handle_responses_direct_route(self, app, db_manager):
        """Test direct route for responses to cover line 83"""
        # Create a test session and response first
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO web_chat_sessions (id, last_active) 
            VALUES ('session_test_resp', datetime('now'))
        """)
        cursor.execute("""
            INSERT OR REPLACE INTO web_chat_responses (session_id, response, message_id, timestamp) 
            VALUES ('session_test_resp', 'test response', 1, datetime('now'))
        """)
        conn.commit()
        conn.close()
        
        with app.test_client() as client:
            response = client.get('/api/v1/responses?session_id=session_test_resp')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
    
    def test_handle_sessions_direct_route(self, app):
        """Test direct route for sessions to cover line 88"""
        with app.test_client() as client:
            response = client.get('/api/v1/sessions', 
                               headers={'Authorization': 'Bearer test_admin_key_456'})
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
    
    def test_handle_config_direct_route(self, app):
        """Test direct route for config to cover line 93"""
        with app.test_client() as client:
            response = client.get('/api/v1/config', 
                               headers={'Authorization': 'Bearer test_admin_key_456'})
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
    
    def test_handle_cleanup_direct_route(self, app):
        """Test direct route for cleanup to cover line 98"""
        with app.test_client() as client:
            response = client.post('/api/v1/cleanup', 
                                headers={'Authorization': 'Bearer test_admin_key_456'})
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
    
    def test_handle_clear_data_direct_route(self, app):
        """Test direct route for clear_data to cover line 103"""
        with app.test_client() as client:
            response = client.post('/api/v1/clear_data', 
                                headers={'Authorization': 'Bearer test_admin_key_456'})
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
    
    def test_handle_cleanup_logs_direct_route(self, app):
        """Test direct route for cleanup_logs to cover line 108"""
        with app.test_client() as client:
            response = client.post('/api/v1/cleanup_logs', 
                                headers={'Authorization': 'Bearer test_admin_key_456'})
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
