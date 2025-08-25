import pytest
from unittest.mock import Mock, patch


class TestAdminRoutesEdgeCases:
    """Test admin routes edge cases and error handling"""
    
    def test_admin_interface_route(self, app):
        """Test admin interface main page route"""
        with app.test_client() as client:
            response = client.get('/admin/')
            assert response.status_code == 200
            assert 'text/html' in response.content_type
    
    @patch('app.admin.routes.get_db')
    def test_get_sessions_database_error(self, mock_get_db, app):
        """Test sessions endpoint with database error"""
        mock_get_db.return_value.get_active_sessions.side_effect = Exception("Database error")
        
        with app.test_client() as client:
            response = client.get('/admin/api/sessions', 
                               headers={'Authorization': 'Bearer test_admin_key_456'})
            assert response.status_code == 500
            data = response.get_json()
            assert data['error'] == 'Database error'
    
    @patch('app.admin.routes.get_db')
    def test_get_session_messages_database_error(self, mock_get_db, app):
        """Test session_messages endpoint with database error"""
        mock_get_db.return_value.get_connection.side_effect = Exception("Database error")
        
        with app.test_client() as client:
            response = client.get('/admin/api/session_messages?session_id=session_test', 
                               headers={'Authorization': 'Bearer test_admin_key_456'})
            assert response.status_code == 500
            data = response.get_json()
            assert data['error'] == 'Database error'
    
    @patch('app.admin.routes.get_db')
    def test_get_session_messages_session_not_found(self, mock_get_db, app):
        """Test session_messages endpoint with non-existent session"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value.get_connection.return_value = mock_conn
        
        with app.test_client() as client:
            response = client.get('/admin/api/session_messages?session_id=session_nonexistent', 
                               headers={'Authorization': 'Bearer test_admin_key_456'})
            assert response.status_code == 404
            data = response.get_json()
            assert data['error'] == 'Session not found'
    
    @patch('app.admin.routes.get_db')
    def test_get_session_messages_cursor_error(self, mock_get_db, app):
        """Test session_messages endpoint with cursor execution error"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("SQL error")
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value.get_connection.return_value = mock_conn
        
        with app.test_client() as client:
            response = client.get('/admin/api/session_messages?session_id=session_test', 
                               headers={'Authorization': 'Bearer test_admin_key_456'})
            assert response.status_code == 500
            data = response.get_json()
            assert data['error'] == 'SQL error'
    
    @patch('app.admin.routes.get_db')
    def test_get_config_database_error(self, mock_get_db, app):
        """Test config endpoint with database error"""
        mock_get_db.return_value.get_all_config.side_effect = Exception("Database error")
        
        with app.test_client() as client:
            response = client.get('/admin/api/config', 
                               headers={'Authorization': 'Bearer test_admin_key_456'})
            assert response.status_code == 500
            data = response.get_json()
            assert data['error'] == 'Database error'
    
    @patch('app.admin.routes.get_db')
    def test_update_config_database_error(self, mock_get_db, app):
        """Test config update endpoint with database error"""
        mock_get_db.return_value.update_config.side_effect = Exception("Database error")
        
        with app.test_client() as client:
            response = client.post('/admin/api/config', 
                                json={'api_key': 'new_key'},
                                headers={'Authorization': 'Bearer test_admin_key_456'})
            assert response.status_code == 500
            data = response.get_json()
            assert data['error'] == 'Database error'
    
    @patch('app.admin.routes.get_db')
    def test_cleanup_database_error(self, mock_get_db, app):
        """Test cleanup endpoint with database error"""
        mock_get_db.return_value.cleanup_inactive_sessions.side_effect = Exception("Database error")
        
        with app.test_client() as client:
            response = client.post('/admin/api/cleanup', 
                                headers={'Authorization': 'Bearer test_admin_key_456'})
            assert response.status_code == 500
            data = response.get_json()
            assert data['error'] == 'Database error'
    
    @patch('app.admin.routes.get_db')
    def test_clear_data_database_error(self, mock_get_db, app):
        """Test clear_data endpoint with database error"""
        mock_get_db.return_value.get_connection.side_effect = Exception("Database error")
        
        with app.test_client() as client:
            response = client.post('/admin/api/clear_data', 
                                headers={'Authorization': 'Bearer test_admin_key_456'})
            assert response.status_code == 500
            data = response.get_json()
            assert data['error'] == 'Database error'
    
    @patch('app.admin.routes.get_db')
    def test_clear_data_cursor_error(self, mock_get_db, app):
        """Test clear_data endpoint with cursor execution error"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("SQL error")
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value.get_connection.return_value = mock_conn
        
        with app.test_client() as client:
            response = client.post('/admin/api/clear_data', 
                                headers={'Authorization': 'Bearer test_admin_key_456'})
            assert response.status_code == 500
            data = response.get_json()
            assert data['error'] == 'SQL error'
