import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.api.routes import handle_messages, handle_inbox, handle_outbox, handle_responses

class TestAPIRoutesMissingCoverage:
    """Test missing coverage in API routes"""
    
    @patch('app.api.routes.get_rate_limiter')
    def test_handle_messages_rate_limit_exceeded(self, mock_get_rate_limiter):
        """Test rate limit exceeded in handle_messages"""
        from flask import request
        from app import create_app
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', json={'session_id': 'test', 'message': 'test'}):
            # Mock rate limiter to return False (rate limit exceeded)
            mock_limiter = MagicMock()
            mock_limiter.check_rate_limit.return_value = False
            mock_get_rate_limiter.return_value = mock_limiter
            
            result = handle_messages()
            
            assert result[1] == 429  # Rate limit exceeded
            assert 'Rate limit exceeded' in result[0].json['error']
    
    @patch('app.api.routes.require_auth_internal')
    @patch('app.api.routes.get_rate_limiter')
    def test_handle_inbox_rate_limit_exceeded(self, mock_get_rate_limiter, mock_require_auth):
        """Test rate limit exceeded in handle_inbox"""
        from flask import request
        from app import create_app
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='GET', headers={'Authorization': 'Bearer test_key'}):
            # Mock authentication to return None (success)
            mock_require_auth.return_value = None
            
            # Mock rate limiter to return False (rate limit exceeded)
            mock_limiter = MagicMock()
            mock_limiter.check_rate_limit.return_value = False
            mock_get_rate_limiter.return_value = mock_limiter
            
            result = handle_inbox()
            
            assert result[1] == 429  # Rate limit exceeded
            assert 'Rate limit exceeded' in result[0].json['error']
    
    @patch('app.api.routes.require_auth_internal')
    @patch('app.api.routes.get_rate_limiter')
    def test_handle_outbox_rate_limit_exceeded(self, mock_get_rate_limiter, mock_require_auth):
        """Test rate limit exceeded in handle_outbox"""
        from flask import request
        from app import create_app
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', json={'session_id': 'session_test_123', 'response': 'test'}, headers={'Authorization': 'Bearer test_key'}):
            # Mock authentication to return None (success)
            mock_require_auth.return_value = None
            
            # Mock rate limiter to return False (rate limit exceeded)
            mock_limiter = MagicMock()
            mock_limiter.check_rate_limit.return_value = False
            mock_get_rate_limiter.return_value = mock_limiter
            
            result = handle_outbox()
            
            assert result[1] == 429  # Rate limit exceeded
            assert 'Rate limit exceeded' in result[0].json['error']
    
    @patch('app.api.routes.get_rate_limiter')
    def test_handle_responses_rate_limit_exceeded(self, mock_get_rate_limiter):
        """Test rate limit exceeded in handle_responses"""
        from flask import request
        from app import create_app
        
        app = create_app()
        with app.test_request_context('/api/v1/?session_id=session_test_123', method='GET'):
            # Mock rate limiter to return False (rate limit exceeded)
            mock_limiter = MagicMock()
            mock_limiter.check_rate_limit.return_value = False
            mock_get_rate_limiter.return_value = mock_limiter
            
            result = handle_responses()
            
            assert result[1] == 429  # Rate limit exceeded
            assert 'Rate limit exceeded' in result[0].json['error']
    
    @patch('app.api.routes.require_auth_internal')
    @patch('app.api.routes.get_db')
    def test_handle_outbox_invalid_session(self, mock_get_db, mock_require_auth):
        """Test invalid session in handle_outbox"""
        from flask import request
        from app import create_app
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', json={'session_id': 'session_test_123', 'response': 'test'}, headers={'Authorization': 'Bearer test_key'}):
            # Mock authentication to return None (success)
            mock_require_auth.return_value = None
            
            # Mock database to return False for session_exists
            mock_db = MagicMock()
            mock_db.session_exists.return_value = False
            mock_get_db.return_value = mock_db
            
            # Mock rate limiter to return True
            with patch('app.api.routes.get_rate_limiter') as mock_get_limiter:
                mock_limiter = MagicMock()
                mock_limiter.check_rate_limit.return_value = True
                mock_get_limiter.return_value = mock_limiter
                
                result = handle_outbox()
                
                assert result[1] == 400  # Bad request
                assert 'Invalid session' in result[0].json['error']
    
    @patch('app.api.routes.require_auth_internal')
    @patch('app.api.routes.get_db')
    def test_handle_outbox_database_error(self, mock_get_db, mock_require_auth):
        """Test database error in handle_outbox"""
        from flask import request
        from app import create_app
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', json={'session_id': 'session_test_123', 'response': 'test'}, headers={'Authorization': 'Bearer test_key'}):
            # Mock authentication to return None (success)
            mock_require_auth.return_value = None
            
            # Mock database to raise exception
            mock_db = MagicMock()
            mock_db.session_exists.side_effect = Exception("Database error")
            mock_get_db.return_value = mock_db
            
            # Mock rate limiter to return True
            with patch('app.api.routes.get_rate_limiter') as mock_get_limiter:
                mock_limiter = MagicMock()
                mock_limiter.check_rate_limit.return_value = True
                mock_get_limiter.return_value = mock_limiter
                
                result = handle_outbox()
                
                assert result[1] == 500  # Internal server error
                assert 'Internal server error' in result[0].json['error']
    
    @patch('app.api.routes.get_db')
    def test_handle_responses_database_error(self, mock_get_db):
        """Test database error in handle_responses"""
        from flask import request
        from app import create_app
        
        app = create_app()
        with app.test_request_context('/api/v1/?session_id=session_test_123', method='GET'):
            # Mock database to raise exception
            mock_db = MagicMock()
            mock_db.session_exists.side_effect = Exception("Database error")
            mock_get_db.return_value = mock_db
            
            # Mock rate limiter to return True
            with patch('app.api.routes.get_rate_limiter') as mock_get_limiter:
                mock_limiter = MagicMock()
                mock_limiter.check_rate_limit.return_value = True
                mock_get_limiter.return_value = mock_limiter
                
                result = handle_responses()
                
                assert result[1] == 500  # Internal server error
                assert 'Internal server error' in result[0].json['error']
