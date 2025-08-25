import pytest
from unittest.mock import patch, MagicMock
from app import create_app

class TestAPIAdminErrorConditions:
    """Test error conditions in admin API routes for 100% coverage"""
    
    @patch('app.api.routes.require_admin_auth_internal')
    @patch('app.api.routes.get_db')
    def test_handle_clear_data_database_error(self, mock_get_db, mock_require_auth):
        """Test database error in handle_clear_data"""
        from app.api.routes import handle_clear_data
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', headers={'Authorization': 'Bearer test_key'}):
            # Mock authentication to return None (success)
            mock_require_auth.return_value = None
            
            # Mock database to raise exception during get_connection
            mock_db = MagicMock()
            mock_db.get_connection.side_effect = Exception("Database connection error")
            mock_get_db.return_value = mock_db
            
            result = handle_clear_data()
            
            assert result[1] == 500  # Internal server error
            assert 'Internal server error' in result[0].json['error']
    
    @patch('app.api.routes.require_admin_auth_internal')
    @patch('app.api.routes.get_db')
    def test_handle_clear_data_cursor_error(self, mock_get_db, mock_require_auth):
        """Test cursor error in handle_clear_data"""
        from app.api.routes import handle_clear_data
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', headers={'Authorization': 'Bearer test_key'}):
            # Mock authentication to return None (success)
            mock_require_auth.return_value = None
            
            # Mock database and connection
            mock_db = MagicMock()
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_db.get_connection.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock cursor to raise exception during execute
            mock_cursor.execute.side_effect = Exception("Cursor execution error")
            mock_get_db.return_value = mock_db
            
            result = handle_clear_data()
            
            assert result[1] == 500  # Internal server error
            assert 'Internal server error' in result[0].json['error']
    
    @patch('app.api.routes.require_admin_auth_internal')
    @patch('app.api.routes.get_db')
    def test_handle_clear_data_commit_error(self, mock_get_db, mock_require_auth):
        """Test commit error in handle_clear_data"""
        from app.api.routes import handle_clear_data
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', headers={'Authorization': 'Bearer test_key'}):
            # Mock authentication to return None (success)
            mock_require_auth.return_value = None
            
            # Mock database and connection
            mock_db = MagicMock()
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_db.get_connection.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock cursor operations to succeed but commit to fail
            mock_cursor.fetchone.return_value = [0]  # Count queries succeed
            mock_cursor.execute.return_value = None  # Delete queries succeed
            mock_conn.commit.side_effect = Exception("Commit error")
            mock_get_db.return_value = mock_db
            
            result = handle_clear_data()
            
            assert result[1] == 500  # Internal server error
            assert 'Internal server error' in result[0].json['error']
    
    @patch('app.api.routes.require_admin_auth_internal')
    def test_handle_cleanup_logs_success(self, mock_require_auth):
        """Test successful cleanup_logs execution"""
        from app.api.routes import handle_cleanup_logs
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', headers={'Authorization': 'Bearer test_key'}):
            # Mock authentication to return None (success)
            mock_require_auth.return_value = None
            
            result = handle_cleanup_logs()
            
            assert result[1] == 200  # Success
            assert result[0].json['success'] is True
            assert 'Success' in result[0].json['message']
    
    @patch('app.api.routes.require_admin_auth_internal')
    def test_handle_cleanup_logs_authentication_failure(self, mock_require_auth):
        """Test authentication failure in handle_cleanup_logs"""
        from app.api.routes import handle_cleanup_logs
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='POST', headers={'Authorization': 'Bearer test_key'}):
            # Mock authentication to return error response
            mock_require_auth.return_value = ('Unauthorized', 401)
            
            result = handle_cleanup_logs()
            
            assert result[1] == 401  # Unauthorized
            assert 'Unauthorized' in result[0]
    
    def test_handle_clear_data_method_not_allowed(self):
        """Test method not allowed in handle_clear_data"""
        from app.api.routes import handle_clear_data
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='GET'):
            result = handle_clear_data()
            
            assert result[1] == 405  # Method not allowed
            assert 'Method not allowed' in result[0].json['error']
    
    def test_handle_cleanup_logs_method_not_allowed(self):
        """Test method not allowed in handle_cleanup_logs"""
        from app.api.routes import handle_cleanup_logs
        
        app = create_app()
        with app.test_request_context('/api/v1/', method='GET'):
            result = handle_cleanup_logs()
            
            assert result[1] == 405  # Method not allowed
            assert 'Method not allowed' in result[0].json['error']
