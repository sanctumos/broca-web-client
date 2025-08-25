import pytest
from unittest.mock import patch, MagicMock
from app import create_app

class TestAPIInboxOutboxErrorConditions:
    """Test error conditions in inbox and outbox functions for 100% coverage"""
    
    @patch('app.api.routes.require_auth_internal')
    @patch('app.api.routes.get_db')
    def test_handle_inbox_database_error(self, mock_get_db, mock_require_auth):
        """Test database error in handle_inbox"""
        from app.api.routes import handle_inbox
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='GET', headers={'Authorization': 'Bearer test_key'}):
            # Mock authentication to return None (success)
            mock_require_auth.return_value = None
            
            # Mock rate limiter to return True
            with patch('app.api.routes.get_rate_limiter') as mock_get_limiter:
                mock_limiter = MagicMock()
                mock_limiter.check_rate_limit.return_value = True
                mock_get_limiter.return_value = mock_limiter
                
                # Mock database to raise exception during get_unprocessed_messages
                mock_db = MagicMock()
                mock_db.get_unprocessed_messages.side_effect = Exception("Database error")
                mock_get_db.return_value = mock_db
                
                result = handle_inbox()
                
                assert result[1] == 500  # Internal server error
                assert 'Internal server error' in result[0].json['error']
    
    @patch('app.api.routes.require_auth_internal')
    @patch('app.api.routes.get_db')
    def test_handle_inbox_count_error(self, mock_get_db, mock_require_auth):
        """Test database error during count in handle_inbox"""
        from app.api.routes import handle_inbox
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='GET', headers={'Authorization': 'Bearer test_key'}):
            # Mock authentication to return None (success)
            mock_require_auth.return_value = None
            
            # Mock rate limiter to return True
            with patch('app.api.routes.get_rate_limiter') as mock_get_limiter:
                mock_limiter = MagicMock()
                mock_limiter.check_rate_limit.return_value = True
                mock_get_limiter.return_value = mock_limiter
                
                # Mock database to succeed on get_unprocessed_messages but fail on count
                mock_db = MagicMock()
                mock_db.get_unprocessed_messages.return_value = []
                mock_db.get_unprocessed_message_count.side_effect = Exception("Count error")
                mock_get_db.return_value = mock_db
                
                result = handle_inbox()
                
                assert result[1] == 500  # Internal server error
                assert 'Internal server error' in result[0].json['error']
    
    @patch('app.api.routes.require_auth_internal')
    @patch('app.api.routes.get_db')
    def test_handle_inbox_mark_processed_error(self, mock_get_db, mock_require_auth):
        """Test database error during mark_processed in handle_inbox"""
        from app.api.routes import handle_inbox
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='GET', headers={'Authorization': 'Bearer test_key'}):
            # Mock authentication to return None (success)
            mock_require_auth.return_value = None
            
            # Mock rate limiter to return True
            with patch('app.api.routes.get_rate_limiter') as mock_get_limiter:
                mock_limiter = MagicMock()
                mock_limiter.check_rate_limit.return_value = True
                mock_get_limiter.return_value = mock_limiter
                
                # Mock database to succeed on get_unprocessed_messages and count but fail on mark_processed
                mock_db = MagicMock()
                mock_db.get_unprocessed_messages.return_value = [{'id': 1}]
                mock_db.get_unprocessed_message_count.return_value = 1
                mock_db.mark_messages_processed.side_effect = Exception("Mark processed error")
                mock_get_db.return_value = mock_db
                
                result = handle_inbox()
                
                assert result[1] == 500  # Internal server error
                assert 'Internal server error' in result[0].json['error']
    
    @patch('app.api.routes.require_auth_internal')
    @patch('app.api.routes.get_db')
    def test_handle_outbox_create_response_error(self, mock_get_db, mock_require_auth):
        """Test database error during create_response in handle_outbox"""
        from app.api.routes import handle_outbox
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', json={'session_id': 'session_test_123', 'response': 'test'}, headers={'Authorization': 'Bearer test_key'}):
            # Mock authentication to return None (success)
            mock_require_auth.return_value = None
            
            # Mock rate limiter to return True
            with patch('app.api.routes.get_rate_limiter') as mock_get_limiter:
                mock_limiter = MagicMock()
                mock_limiter.check_rate_limit.return_value = True
                mock_get_limiter.return_value = mock_limiter
                
                # Mock database to succeed on session_exists but fail on create_response
                mock_db = MagicMock()
                mock_db.session_exists.return_value = True
                mock_db.create_response_with_message_id.side_effect = Exception("Create response error")
                mock_get_db.return_value = mock_db
                
                result = handle_outbox()
                
                assert result[1] == 500  # Internal server error
                assert 'Internal server error' in result[0].json['error']
    
    @patch('app.api.routes.require_auth_internal')
    @patch('app.api.routes.get_db')
    def test_handle_outbox_get_uid_error(self, mock_get_db, mock_require_auth):
        """Test database error during get_or_create_uid in handle_outbox"""
        from app.api.routes import handle_outbox
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', json={'session_id': 'session_test_123', 'response': 'test'}, headers={'Authorization': 'Bearer test_key'}):
            # Mock authentication to return None (success)
            mock_require_auth.return_value = None
            
            # Mock rate limiter to return True
            with patch('app.api.routes.get_rate_limiter') as mock_get_limiter:
                mock_limiter = MagicMock()
                mock_limiter.check_rate_limit.return_value = True
                mock_get_limiter.return_value = mock_limiter
                
                # Mock database to succeed on session_exists but fail on get_or_create_uid
                mock_db = MagicMock()
                mock_db.session_exists.return_value = True
                mock_db.get_or_create_uid.side_effect = Exception("Get UID error")
                mock_get_db.return_value = mock_db
                
                result = handle_outbox()
                
                assert result[1] == 500  # Internal server error
                assert 'Internal server error' in result[0].json['error']
